from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ImportJobLog(Base):
    __tablename__ = "import_job_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    rule_version: Mapped[str] = mapped_column(String(50), nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(100), nullable=False, default="system")
    started_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
