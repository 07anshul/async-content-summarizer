from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator


class SubmitRequest(BaseModel):
    url: Optional[str] = None
    text: Optional[str] = None

    @model_validator(mode="after")
    def validate_url_or_text(self) -> "SubmitRequest":
        if bool(self.url) == bool(self.text):
            raise ValueError("either url or text must be provided not both")
        return self


class SubmitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    status: Literal["queued", "processing", "completed", "failed"]


class StatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    status: Literal["queued", "processing", "completed", "failed"]
    updated_at: Optional[datetime] = None


class ResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    original_url: Optional[str] = None
    summary: Optional[str] = None
    cached: bool = False
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None

