from sqlalchemy import text
from sqlalchemy.orm import Session

BASE_SQL = """
SELECT
  company_name AS company,
  ad_type,
  display_address AS address,
  ST_Y(geom) AS lat,
  ST_X(geom) AS lng,
  ST_Distance(
    geom::geography,
    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
  ) AS distance_m
FROM billboards
WHERE status = 'ACTIVE'
  AND geom IS NOT NULL
  AND ST_DWithin(
    geom::geography,
    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
    :radius_m
  )
"""


def build_radius_query(
    *,
    lat: float,
    lng: float,
    radius_m: int = 200,
    legal_dong: str | None = None,
    ad_type: str | None = None,
) -> tuple[str, dict[str, object]]:
    query = BASE_SQL
    params: dict[str, object] = {"lat": lat, "lng": lng, "radius_m": radius_m}

    if legal_dong:
        query += "\n  AND legal_dong = :legal_dong"
        params["legal_dong"] = legal_dong
    if ad_type:
        query += "\n  AND ad_type = :ad_type"
        params["ad_type"] = ad_type

    query += "\nORDER BY distance_m ASC"
    return query, params


def query_radius(
    session: Session,
    *,
    lat: float,
    lng: float,
    radius_m: int = 200,
    legal_dong: str | None = None,
    ad_type: str | None = None,
) -> list[dict[str, object]]:
    sql, params = build_radius_query(
        lat=lat,
        lng=lng,
        radius_m=radius_m,
        legal_dong=legal_dong,
        ad_type=ad_type,
    )
    rows = session.execute(text(sql), params).mappings().all()
    return [
        {
            "company": str(row["company"]),
            "ad_type": str(row["ad_type"]),
            "address": str(row["address"]),
            "lat": float(row["lat"]),
            "lng": float(row["lng"]),
            "distance_m": float(row["distance_m"]),
        }
        for row in rows
    ]
