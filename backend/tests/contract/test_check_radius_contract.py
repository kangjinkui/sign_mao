from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# 테스트에서는 NoopGeocodingClient를 사용하므로 주소 기반 지오코딩이 동작하지 않는다.
# 지오코딩이 필요없는 테스트는 lat/lng를 직접 전달한다.
_LAT = 37.526
_LNG = 127.039
_DIRECT = {"address": "서울 강남구 도산대로 306", "lat": _LAT, "lng": _LNG}


def test_check_radius_success_contract() -> None:
    response = client.post("/api/v1/check-radius", json=_DIRECT)
    assert response.status_code == 200
    data = response.json()
    assert {"input", "radius", "count", "items", "geocode_candidates"}.issubset(data.keys())


def test_check_radius_response_radius_field_is_200() -> None:
    response = client.post("/api/v1/check-radius", json=_DIRECT)
    assert response.status_code == 200
    assert response.json()["radius"] == 200


def test_check_radius_response_count_matches_items_length() -> None:
    response = client.post("/api/v1/check-radius", json=_DIRECT)
    data = response.json()
    assert data["count"] == len(data["items"])


def test_check_radius_input_field_contains_address() -> None:
    response = client.post("/api/v1/check-radius", json=_DIRECT)
    data = response.json()
    assert "address" in data["input"]
    assert "lat" in data["input"]
    assert "lng" in data["input"]


def test_check_radius_item_schema() -> None:
    """items 배열의 각 항목이 필수 필드를 갖춰야 한다."""
    response = client.post("/api/v1/check-radius", json=_DIRECT)
    data = response.json()
    for item in data["items"]:
        assert {"company", "ad_type", "address", "lat", "lng", "distance_m"}.issubset(item.keys())


def test_check_radius_validation_error_contract() -> None:
    response = client.post("/api/v1/check-radius", json={"address": ""})
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_check_radius_validation_error_short_address() -> None:
    """address가 min_length=2 미만이면 VALIDATION_ERROR를 반환해야 한다."""
    response = client.post("/api/v1/check-radius", json={"address": "A"})
    assert response.status_code == 400
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_check_radius_error_response_has_code_and_message() -> None:
    response = client.post("/api/v1/check-radius", json={"address": ""})
    data = response.json()
    assert "code" in data
    assert "message" in data


def test_check_radius_geocoding_empty_returns_geocoding_error() -> None:
    """지오코딩 결과가 없으면 GEOCODING_ERROR를 반환해야 한다 (NoopClient 환경)."""
    response = client.post("/api/v1/check-radius", json={"address": "서울 강남구 도산대로"})
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "GEOCODING_ERROR"


def test_check_radius_with_lat_lng_skips_geocoding() -> None:
    """lat/lng 직접 입력 시 지오코딩 없이 200 응답을 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "임의주소", "lat": _LAT, "lng": _LNG},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input"]["lat"] == _LAT
    assert data["input"]["lng"] == _LNG
