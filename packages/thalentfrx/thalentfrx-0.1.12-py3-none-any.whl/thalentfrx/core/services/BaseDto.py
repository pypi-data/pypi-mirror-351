from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditBaseDto(BaseModel):
    id: Optional[str] = None
    is_deleted: Optional[bool] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    row_version: Optional[str] = None
    row_timespan: Optional[int] = None
