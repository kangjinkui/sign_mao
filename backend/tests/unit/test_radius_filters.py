from app.services.spatial_query import build_radius_query


def test_build_radius_query_with_filters() -> None:
    sql, params = build_radius_query(
        lat=37.5,
        lng=127.0,
        legal_dong="논현동",
        ad_type="ROOFTOP_LED",
    )
    assert "legal_dong = :legal_dong" in sql
    assert "ad_type = :ad_type" in sql
    assert params["legal_dong"] == "논현동"
    assert params["ad_type"] == "ROOFTOP_LED"


def test_build_radius_query_only_legal_dong_filter() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0, legal_dong="역삼동")
    assert "legal_dong = :legal_dong" in sql
    assert "ad_type" not in params


def test_build_radius_query_only_ad_type_filter() -> None:
    sql, params = build_radius_query(lat=37.5, lng=127.0, ad_type="WALL_LED")
    assert "ad_type = :ad_type" in sql
    assert "legal_dong" not in params


def test_build_radius_query_wall_led_ad_type() -> None:
    _, params = build_radius_query(lat=37.5, lng=127.0, ad_type="WALL_LED")
    assert params["ad_type"] == "WALL_LED"


def test_build_radius_query_filter_does_not_remove_active_condition() -> None:
    """필터가 추가되어도 status = ACTIVE 조건은 유지되어야 한다."""
    sql, _ = build_radius_query(lat=37.5, lng=127.0, legal_dong="논현동", ad_type="ROOFTOP_LED")
    assert "status = 'ACTIVE'" in sql
