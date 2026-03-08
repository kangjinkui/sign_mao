import uuid
from io import BytesIO
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app
from app.services.import_job_service import ImportJobResult

client = TestClient(app)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# conftest에서 get_import_geocoding_client → NoopGeocodingClient 로 오버라이드됨.
# import 테스트는 DB 세션도 mock으로 대체해 DB 없이 실행한다.

_FAKE_JOB_RESULT = ImportJobResult(
    job_id=str(uuid.uuid4()),
    success_count=1,
    failed_count=0,
)


def _sample_xlsx() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "전광판 현황"
    ws.append(["대형 광고물(전광판) 현황"])
    ws.append(["연번", "광고물종류", "업체명", "허가날짜", "규격", "광고물 표시 주소", "법정동"])
    ws.append([1, "옥상전광", "업체A", 45000, "10x9", "서울 강남구 도산대로 306", "논현동"])
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_import_billboards_contract() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _FAKE_JOB_RESULT
        files = {"file": ("sample.xlsx", _sample_xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 202
    body = response.json()
    assert {"job_id", "status", "success_count", "failed_count"}.issubset(body.keys())


def test_import_billboards_status_field_is_started() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _FAKE_JOB_RESULT
        files = {"file": ("sample.xlsx", _sample_xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert response.json()["status"] == "STARTED"


def test_import_billboards_job_id_is_string() -> None:
    with patch("app.api.v1.import_billboards.BillboardImportService") as MockService:
        MockService.return_value.import_uploaded_file.return_value = _FAKE_JOB_RESULT
        files = {"file": ("sample.xlsx", _sample_xlsx(), XLSX_MIME)}
        response = client.post("/api/v1/import/billboards", files=files)
    assert isinstance(response.json()["job_id"], str)


def test_import_billboards_non_xlsx_returns_validation_error() -> None:
    files = {"file": ("data.txt", b"invalid content", "text/plain")}
    response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_import_billboards_csv_extension_rejected() -> None:
    files = {"file": ("data.csv", b"serial,type\n1,ROOFTOP", "text/csv")}
    response = client.post("/api/v1/import/billboards", files=files)
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"


def test_import_billboards_error_response_schema() -> None:
    """오류 응답은 code/message/details 필드를 포함해야 한다."""
    files = {"file": ("data.txt", b"invalid", "text/plain")}
    response = client.post("/api/v1/import/billboards", files=files)
    data = response.json()
    assert "code" in data
    assert "message" in data
    assert "details" in data
