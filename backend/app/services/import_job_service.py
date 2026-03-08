import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.import_job_log import ImportJobLog


@dataclass(slots=True)
class ImportJobResult:
    job_id: str
    success_count: int
    failed_count: int


def create_import_job(
    session: Session,
    *,
    source_file_name: str,
    source_file_path: str,
    rule_version: str,
    success_count: int,
    failed_count: int,
    created_by: str,
) -> ImportJobResult:
    job = ImportJobLog(
        source_file_name=source_file_name,
        source_file_path=source_file_path,
        rule_version=rule_version,
        success_count=success_count,
        failed_count=failed_count,
        created_by=created_by,
    )
    session.add(job)
    session.commit()
    return ImportJobResult(job_id=str(uuid.uuid4()), success_count=success_count, failed_count=failed_count)
