import pytest

from app.services.spatial_query import build_radius_query


def test_build_radius_query_contains_postgis_and_active_filter() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0)
    assert "ST_DWithin" in sql
    assert "status = 'ACTIVE'" in sql
    assert params["radius_m"] == 200


def test_build_radius_query_default_radius_is_200() -> None:
    _, params = build_radius_query(lat=37.5, lng=127.0)
    assert params["radius_m"] == 200


def test_build_radius_query_custom_radius() -> None:
    _, params = build_radius_query(lat=37.5, lng=127.0, radius_m=500)
    assert params["radius_m"] == 500


def test_build_radius_query_lat_lng_in_params() -> None:
    _, params = build_radius_query(lat=37.1234, lng=127.5678)
    assert params["lat"] == 37.1234
    assert params["lng"] == 127.5678


def test_build_radius_query_ordered_by_distance() -> None:
    sql, _ = build_radius_query(lat=37.5, lng=127.0)
    assert "ORDER BY distance_m ASC" in sql


def test_build_radius_query_includes_distance_column() -> None:
    sql, _ = build_radius_query(lat=37.5, lng=127.0)
    assert "ST_Distance" in sql
    assert "distance_m" in sql


def test_build_radius_query_uses_geography_cast() -> None:
    """geography 타입 캐스팅으로 meter 단위 계산을 보장한다."""
    sql, _ = build_radius_query(lat=37.5, lng=127.0)
    assert "geography" in sql


def test_build_radius_query_with_legal_dong_filter() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0, legal_dong="논현동")
    assert "legal_dong = :legal_dong" in sql
    assert params["legal_dong"] == "논현동"


def test_build_radius_query_with_ad_type_filter() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0, ad_type="ROOFTOP_LED")
    assert "ad_type = :ad_type" in sql
    assert params["ad_type"] == "ROOFTOP_LED"


def test_build_radius_query_with_both_filters() -> None:
    sql, params = build_radius_query(
        lat=37.5, lng=127.0, legal_dong="논현동", ad_type="ROOFTOP_LED"
    )
    assert "legal_dong = :legal_dong" in sql
    assert "ad_type = :ad_type" in sql
    assert params["legal_dong"] == "논현동"
    assert params["ad_type"] == "ROOFTOP_LED"


def test_build_radius_query_no_filter_excludes_filter_clauses() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0)
    assert "legal_dong" not in sql
    assert "ad_type" not in params


def test_build_radius_query_geom_not_null_condition() -> None:
    """geom IS NOT NULL 조건으로 좌표 없는 데이터를 제외해야 한다."""
    sql, _ = build_radius_query(lat=37.5, lng=127.0)
    assert "geom IS NOT NULL" in sql
