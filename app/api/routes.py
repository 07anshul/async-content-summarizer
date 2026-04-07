from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas import ResultResponse, StatusResponse, SubmitRequest, SubmitResponse
from app.cache.redis_cache import get_cache
from app.core.config import settings
from app.core.logger import log
from app.db.deps import get_db
from app.db.models import Job
from app.queue.redis_queue import get_queue
from app.services.content_hash import compute_content_hash, compute_extracted_hash


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.post("/submit", response_model=SubmitResponse)
def submit(payload: SubmitRequest, db: Session = Depends(get_db)) -> SubmitResponse:
    cache = get_cache(settings.redis_url)

    if payload.text:
        content_hash = compute_extracted_hash(payload.text)
        cached = cache.get_summary(content_hash)
        if cached is not None:
            job = Job(
                status="completed",
                input_type="text",
                url=None,
                text=payload.text,
                content_hash=content_hash,
                summary=cached,
                error=None,
                cached=True,
                processing_time_ms=0,
            )
            db.add(job)
            db.commit()
            db.refresh(job)
            log.info("created job job_id=%s status=%s (cache hit)", job.id, job.status)
            return SubmitResponse(job_id=job.id, status=job.status)

    job = Job(
        status="queued",
        input_type="url" if payload.url else "text",
        url=payload.url,
        text=payload.text,
        content_hash=compute_content_hash(url=payload.url, text=payload.text),
        cached=False,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    log.info("created job job_id=%s status=%s", job.id, job.status)

    queue = get_queue(settings.redis_url)
    queue.push(str(job.id))
    log.info("queued job job_id=%s", job.id)

    return SubmitResponse(job_id=job.id, status=job.status)


@router.get("/status/{job_id}", response_model=StatusResponse)
def status(job_id: UUID, db: Session = Depends(get_db)) -> StatusResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return StatusResponse(job_id=job.id, status=job.status, updated_at=job.updated_at)


@router.get("/result/{job_id}", response_model=ResultResponse)
def result(job_id: UUID, db: Session = Depends(get_db)) -> ResultResponse:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return ResultResponse(
        job_id=job.id,
        original_url=job.url,
        summary=job.summary,
        cached=bool(job.cached),
        processing_time_ms=job.processing_time_ms,
        error=job.error,
    )

