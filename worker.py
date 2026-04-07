import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import Job
from app.db.session import SessionLocal
from app.queue.redis_queue import get_queue
from app.services.extract import fetch_and_extract_text
from app.services.summarizer import summarize


def process_job(db: Session, *, job_id: UUID) -> None:
    job = db.get(Job, job_id)
    if job is None:
        return

    job.status = "processing"
    db.commit()

    try:
        content = fetch_and_extract_text(job.url) if job.input_type == "url" else (job.text or "")
        job.summary = summarize(content)
        job.status = "completed"
        job.error = None
        db.commit()
    except Exception as e:
        job.status = "failed"
        job.error = str(e)
        db.commit()


def main() -> None:
    queue = get_queue(settings.redis_url)

    while True:
        raw = queue.pop_blocking(timeout_seconds=5)
        if raw is None:
            time.sleep(0.2)
            continue

        try:
            job_id = UUID(raw)
        except ValueError:
            continue

        db = SessionLocal()
        try:
            process_job(db, job_id=job_id)
        finally:
            db.close()


if __name__ == "__main__":
    main()

