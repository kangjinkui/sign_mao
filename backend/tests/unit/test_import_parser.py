import tempfile
from datetime import date, datetime
from io import BytesIO

from openpyxl import Workbook

from app.services.import_parser import parse_billboards_xlsx


def _make_xlsx(rows: list[list]) -> str:
    """헬퍼: 주어진 행 목록으로 임시 xlsx 파일을 만들고 경로를 반환한다."""
    wb = Workbook()
    ws = wb.active
    ws.append(["title row"])
    ws.append(["연번", "광고물종류", "업체명", "허가날짜", "규격", "광고물 표시 주소", "법정동"])
    for row in rows:
        ws.append(row)
    stream = BytesIO()
    wb.save(stream)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    tmp.write(stream.getvalue())
    tmp.flush()
    tmp.close()
    return tmp.name


def test_parse_billboards_xlsx_basic() -> None:
    path = _make_xlsx([[1, "옥상전광", "업체A", 45000, "10x9", "서울 강남구 도산대로 306", "논현동"]])
    rows, failed = parse_billboards_xlsx(path)
    assert len(rows) == 1
    assert rows[0].ad_type == "ROOFTOP_LED"
    assert failed == 0


def test_parse_billboards_xlsx_invalid_row_counted_as_failed() -> None:
    """필수 컬럼(serial_no, ad_type, company, address)이 없으면 failed로 집계한다."""
    path = _make_xlsx([[None, "벽면전광", "업체B", 45000, "10x9", "", "논현동"]])
    rows, failed = parse_billboards_xlsx(path)
    assert len(rows) == 0
    assert failed == 1


def test_parse_billboards_xlsx_mixed_valid_invalid() -> None:
    path = _make_xlsx([
        [1, "옥상전광", "업체A", 45000, "10x9", "서울 강남구 도산대로 306", "논현동"],
        [None, "벽면전광", "업체B", 45000, "10x9", "", "논현동"],
    ])
    rows, failed = parse_billboards_xlsx(path)
    assert len(rows) == 1
    assert failed == 1


def test_parse_billboards_xlsx_wall_led_normalized() -> None:
    path = _make_xlsx([[2, "벽면전광", "업체C", 45000, "5x3", "서울 마포구 어딘가 1", "서교동"]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].ad_type == "WALL_LED"


def test_parse_billboards_xlsx_unknown_ad_type() -> None:
    path = _make_xlsx([[3, "기타광고물", "업체D", 45000, "5x3", "서울 종로구 어딘가 1", "혜화동"]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].ad_type == "UNKNOWN"


def test_parse_billboards_xlsx_permit_date_as_datetime() -> None:
    path = _make_xlsx([[1, "옥상전광", "업체A", datetime(2020, 5, 10), "10x9", "서울 어딘가", "논현동"]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].permit_date == date(2020, 5, 10)


def test_parse_billboards_xlsx_permit_date_as_date_obj() -> None:
    path = _make_xlsx([[1, "옥상전광", "업체A", date(2021, 3, 15), "10x9", "서울 어딘가", "논현동"]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].permit_date == date(2021, 3, 15)


def test_parse_billboards_xlsx_null_permit_date() -> None:
    path = _make_xlsx([[1, "옥상전광", "업체A", None, "10x9", "서울 어딘가", "논현동"]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].permit_date is None


def test_parse_billboards_xlsx_null_legal_dong() -> None:
    path = _make_xlsx([[1, "옥상전광", "업체A", 45000, "10x9", "서울 어딘가", None]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].legal_dong is None


def test_parse_billboards_xlsx_strips_whitespace() -> None:
    path = _make_xlsx([[1, "옥상전광", "  업체A  ", 45000, "10x9", "  서울 어딘가  ", "  논현동  "]])
    rows, _ = parse_billboards_xlsx(path)
    assert rows[0].company_name == "업체A"
    assert rows[0].display_address == "서울 어딘가"
    assert rows[0].legal_dong == "논현동"


def test_parse_billboards_xlsx_empty_sheet() -> None:
    path = _make_xlsx([])
    rows, failed = parse_billboards_xlsx(path)
    assert rows == []
    assert failed == 0
