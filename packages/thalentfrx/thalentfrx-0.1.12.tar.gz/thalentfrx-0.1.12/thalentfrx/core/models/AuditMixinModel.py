from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Column,
    Integer,
    PrimaryKeyConstraint,
    String,
    DateTime,
    Boolean, text, func,
)
import uuid
import pytz
from thalentfrx.core.models.Helpers import Helpers

class AuditMixin(object):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("'0'")
    )
    created_by: Mapped[str] = mapped_column(
        String(100), nullable=False, default="system", server_default=text("'system'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now(),
        server_default=func.now()
    )
    updated_by: Mapped[str] = mapped_column(String(100), nullable=False, default="", server_default=text("''"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime(
            1900, 1, 1, tzinfo=pytz.utc
        ),
        server_default=text("'1900-01-01'")
    )
    row_version: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        default=uuid.uuid4,
        onupdate=uuid.uuid4,
        server_default=text("uuid_generate_v4()"),
    )
    row_timespan: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=Helpers().get_timestamp(),
        server_default=text("'0'"),
    )

    PrimaryKeyConstraint(id)
    
    def to_dict(self):
        return Helpers().row2dict(self)
