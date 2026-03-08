import tempfile
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.geocoding_client import GeocodingClient
from app.services.import_job_service import ImportJobResult, create_import_job
from app.services.import_parser import parse_billboards_xlsx
from app.services.upload_validation import validate_upload_filename


class BillboardImportService:
    def __init__(self, session: Session, geocoder: GeocodingClient):
        self._session = session
        self._geocoder = geocoder

    def import_uploaded_file(self, *, filename: str, content: bytes, created_by: str = "system") -> ImportJobResult:
        validate_upload_filename(filename)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)

        parsed_rows, failed = parse_billboards_xlsx(str(temp_path))

        success = 0
        for row in parsed_rows:
            try:
                lat: float | None = None
                lng: float | None = None
                try:
                    candidates = self._geocoder.search_sync(row.display_address)
                    if candidates:
                        lat = candidates[0].lat
                        lng = candidates[0].lng
                except Exception:
                    # Keep the source record even when geocoding fails.
                    lat = None
                    lng = None
                self._session.execute(
                    text(
                        """
                        INSERT INTO billboards (
                          serial_no, ad_type, company_name, permit_date, size_text,
                          display_address, legal_dong, status, lat, lng
                        ) VALUES (
                          :serial_no, :ad_type, :company_name, :permit_date, :size_text,
                          :display_address, :legal_dong, :status, :lat, :lng
                        )
                        """
                    ),
                    {
                        "serial_no": row.serial_no,
                        "ad_type": row.ad_type,
                        "company_name": row.company_name,
                        "permit_date": row.permit_date,
                        "size_text": row.size_text,
                        "display_address": row.display_address,
                        "legal_dong": row.legal_dong,
                        "status": "ACTIVE",
                        "lat": lat,
                        "lng": lng,
                    },
                )
                success += 1
            except Exception:
                failed += 1

        self._session.execute(
            text(
                """
                UPDATE billboards
                SET geom = ST_SetSRID(ST_MakePoint(lng::double precision, lat::double precision), 4326)
                WHERE geom IS NULL
                  AND lat IS NOT NULL
                  AND lng IS NOT NULL
                """
            )
        )

        try:
            self._session.commit()
        except Exception as exc:
            self._session.rollback()
            raise RuntimeError("DB_WRITE_FAILED") from exc

        result = create_import_job(
            self._session,
            source_file_name=filename,
            source_file_path=str(temp_path),
            rule_version="v1",
            success_count=success,
            failed_count=failed,
            created_by=created_by,
        )

        return result
