from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

_LAT = 37.526
_LNG = 127.039


def test_check_radius_with_filters_param_shape() -> None:
    """필터 파라미터가 수용되고 200 응답을 반환해야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={
            "address": "서울 강남구 도산대로 306",
            "lat": _LAT,
            "lng": _LNG,
            "legal_dong": "논현동",
            "ad_type": "ROOFTOP_LED",
        },
    )
    assert response.status_code == 200


def test_check_radius_filter_result_subset_of_unfiltered() -> None:
    """필터 적용 결과 건수는 필터 미적용 결과 건수 이하여야 한다."""
    base = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG},
    )
    filtered = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG, "ad_type": "ROOFTOP_LED"},
    )
    assert base.status_code == 200
    assert filtered.status_code == 200
    assert filtered.json()["count"] <= base.json()["count"]


def test_check_radius_ad_type_filter_items_match_type() -> None:
    """ad_type 필터 적용 시 반환된 items는 모두 해당 타입이어야 한다."""
    response = client.post(
        "/api/v1/check-radius",
        json={"address": "테스트", "lat": _LAT, "lng": _LNG, "ad_type": "ROOFTOP_LED"},
    )
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert item["ad_type"] == "ROOFTOP_LED"


def test_check_radius_both_filters_param_accepted() -> None:
    response = client.post(
        "/api/v1/check-radius",
        json={
            "address": "테스트",
            "lat": _LAT,
            "lng": _LNG,
            "legal_dong": "논현동",
            "ad_type": "WALL_LED",
        },
    )
    assert response.status_code == 200
