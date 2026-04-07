import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import log
from app.cache.redis_cache import get_cache
from app.db.models import Job
from app.db.session import SessionLocal
from app.queue.redis_queue import get_queue
from app.services.content_hash import compute_extracted_hash
from app.services.extract import fetch_and_extract_text
from app.services.summarizer import summarize


def process_job(db: Session, *, job_id: UUID) -> None:
    job = db.get(Job, job_id)
    if job is None:
        log.warning("job not found job_id=%s", job_id)
        return

    cache = get_cache(settings.redis_url)

    job.status = "processing"
    db.commit()

    try:
        log.info("processing job job_id=%s", job_id)
        content = fetch_and_extract_text(job.url) if job.input_type == "url" else (job.text or "")
        extracted_hash = compute_extracted_hash(content)
        job.content_hash = extracted_hash

        cached = cache.get_summary(extracted_hash)
        if cached is not None:
            job.summary = cached
        else:
            job.summary = summarize(content)
            cache.set_summary(extracted_hash, job.summary or "")

        job.status = "completed"
        job.error = None
        db.commit()
        log.info("completed job job_id=%s", job_id)
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()
        log.error("failed job job_id=%s error=%s", job_id, e)


def main() -> None:
    queue = get_queue(settings.redis_url)
    log.info("worker started")

    while True:
        raw = queue.pop_blocking(timeout_seconds=5)
        if raw is None:
            time.sleep(0.2)
            continue

        try:
            job_id = UUID(raw)
        except ValueError:
            log.warning("ignored queue item (not uuid): %r", raw)
            continue

        log.info("picked up job job_id=%s", job_id)

        db = SessionLocal()
        try:
            process_job(db, job_id=job_id)
        finally:
            db.close()


if __name__ == "__main__":
    main()

