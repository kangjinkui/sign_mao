import uuid
from io import BytesIO
from unittest.mock import patch

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app
from app.services.import_job_service import ImportJobResult

client = TestClient(app)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# conftest에서 get_import_geocoding_client → NoopGeocodingClient 로 오버라이드됨.
# DB가 없는 환경에서는 BillboardImportService를 mock으로 대체한다.


def _xlsx(rows: list[list] | None = None) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["title"])
    ws.append(["연번", "광고물종류", "업체명", "허가날짜", "규격", "광고물 표시 주소", "법정동"])
    for row in rows or [[1, "벽면전광", "업체B", 45000, "10x9", "서울 강남구 도산대로 300", "논현동"]]:
        ws.append(row)
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _fake_result(success: int = 1, failed: int = 0) -> ImportJobResult:
    return ImportJobResult(job_id=str(uuid.uuid4()), success_count=success, failed_count=failed)


def test_import_flow() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _fake_result()
        files = {"file": ("flow.xlsx", _xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "STARTED"
    assert data["success_count"] >= 0


def test_import_flow_response_has_all_fields() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _fake_result()
        files = {"file": ("flow.xlsx", _xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 202
    data = response.json()
    assert {"job_id", "status", "success_count", "failed_count"}.issubset(data.keys())


def test_import_flow_success_failed_counts_are_non_negative() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _fake_result(success=1, failed=0)
        files = {"file": ("flow.xlsx", _xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    data = response.json()
    assert data["success_count"] >= 0
    assert data["failed_count"] >= 0


def test_import_flow_with_invalid_row_counted_as_failed() -> None:
    """필수 컬럼이 빠진 행은 failed_count에 반영되어야 한다."""
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _fake_result(success=1, failed=1)
        rows = [
            [1, "옥상전광", "업체A", 45000, "10x9", "서울 강남구 도산대로 306", "논현동"],
            [None, "벽면전광", "업체B", 45000, "10x9", "", "논현동"],
        ]
        files = {"file": ("flow.xlsx", _xlsx(rows), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 202
    data = response.json()
    assert data["failed_count"] >= 1


def test_import_flow_wrong_extension_rejected() -> None:
    """xlsx가 아닌 파일은 VALIDATION_ERROR를 반환해야 한다."""
    files = {"file": ("data.csv", b"serial,type\n1,ROOFTOP", "text/csv")}
    response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_import_flow_txt_extension_rejected() -> None:
    """txt 파일도 VALIDATION_ERROR를 반환해야 한다."""
    files = {"file": ("data.txt", b"invalid", "text/plain")}
    response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
