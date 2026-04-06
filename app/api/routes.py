from fastapi import APIRouter

from app.api.schemas import ResultResponse, StatusResponse, SubmitRequest, SubmitResponse


router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"ok": True}


@router.post("/submit", response_model=SubmitResponse)
def submit(payload: SubmitRequest) -> SubmitResponse:
    # Phase 5 will create job + enqueue.
    raise NotImplementedError


@router.get("/status/{job_id}", response_model=StatusResponse)
def status(job_id: str) -> StatusResponse:
    # Phase 7 will read status from DB.
    raise NotImplementedError


@router.get("/result/{job_id}", response_model=ResultResponse)
def result(job_id: str) -> ResultResponse:
    # Phase 7 will read result from DB/cache.
    raise NotImplementedError

