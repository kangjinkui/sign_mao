from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# conftest에서 NoopGeocodingClient로 오버라이드됨.
# 주소 기반 지오코딩이 필요한 테스트는 lat/lng를 직접 입력한다.
_LAT = 37.526
_LNG = 127.039


def test_check_radius_single_address_flow() -> None:
    """lat/lng 직접 입력 시 반경 판정 결과를 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "서울 강남구 도산대로 306", "lat": _LAT, "lng": _LNG},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["radius"] == 200
    assert isinstance(data["items"], list)


def test_check_radius_geocoding_empty_returns_error() -> None:
    """지오코딩 결과가 없으면 (Noop 환경) GEOCODING_ERROR 422를 반환해야 한다."""
    response = client.post("/api/v1/check-radius", json={"address": "서울 강남구 도산대로"})
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "GEOCODING_ERROR"


def test_check_radius_with_direct_coordinates_returns_200() -> None:
    """lat/lng 직접 입력 시 지오코딩 단계를 건너뛰고 결과를 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트 주소", "lat": _LAT, "lng": _LNG},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["input"]["lat"] == _LAT
    assert data["input"]["lng"] == _LNG
    assert data["count"] == len(data["items"])


def test_check_radius_zero_result_returns_count_zero() -> None:
    """반경 내 광고물이 없는 위치는 count=0, items=[]를 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "제주 서귀포시 어딘가", "lat": 33.254, "lng": 126.560},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["items"] == []


def test_check_radius_selected_candidate_id_flow() -> None:
    """selected_candidate_id가 있을 때 해당 좌표로 판정해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={
            "address": "서울 강남구 도산대로 306",
            "selected_candidate_id": "kakao-0",
            "lat": _LAT,
            "lng": _LNG,
        },
    )
    assert response.status_code == 200


def test_check_radius_items_distance_within_200m() -> None:
    """반환된 각 항목의 distance_m은 200 이하여야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG},
    )
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["distance_m"] <= 200.0


def test_check_radius_items_ordered_by_distance_asc() -> None:
    """items는 distance_m 오름차순으로 정렬되어야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG},
    )
    assert response.status_code == 200
    items = response.json()["items"]
    distances = [item["distance_m"] for item in items]
    assert distances == sorted(distances)


def test_check_radius_with_legal_dong_filter() -> None:
    """legal_dong 필터 파라미터가 수용되고 200 응답을 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG, "legal_dong": "논현동"},
    )
    assert response.status_code == 200


def test_check_radius_with_ad_type_filter() -> None:
    """ad_type 필터 파라미터가 수용되고 200 응답을 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG, "ad_type": "ROOFTOP_LED"},
    )
    assert response.status_code == 200
