from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import ResultResponse, StatusResponse, SubmitRequest, SubmitResponse
from app.core.config import settings
from app.db.deps import get_db
from app.db.models import Job
from app.queue.redis_queue import get_queue
from app.services.content_hash import compute_content_hash


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.post("/submit", response_model=SubmitResponse)
def submit(payload: SubmitRequest, db: Session = Depends(get_db)) -> SubmitResponse:
    job = Job(
        status="queued",
        input_type="url" if payload.url else "text",
        url=payload.url,
        text=payload.text,
        content_hash=compute_content_hash(url=payload.url, text=payload.text),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    queue = get_queue(settings.redis_url)
    queue.push(str(job.id))

    return SubmitResponse(job_id=job.id, status=job.status)


@router.get("/status/{job_id}", response_model=StatusResponse)
def status(job_id: UUID) -> StatusResponse:
    raise NotImplementedError


@router.get("/result/{job_id}", response_model=ResultResponse)
def result(job_id: UUID) -> ResultResponse:
    raise NotImplementedError

