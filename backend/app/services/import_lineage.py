from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class ImportLineageMetadata:
    source_file_name: str
    source_file_path: str
    rule_version: str
    started_at: str


def build_lineage(source_file_name: str, source_file_path: str, rule_version: str) -> ImportLineageMetadata:
    return ImportLineageMetadata(
        source_file_name=source_file_name,
        source_file_path=source_file_path,
        rule_version=rule_version,
        started_at=datetime.now(timezone.utc).isoformat(),
    )
