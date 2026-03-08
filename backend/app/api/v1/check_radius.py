import os

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db.session import get_db_session
from app.schemas.check_radius import RadiusCheckRequest, RadiusCheckResponse
from app.services.audit_log_service import log_radius_check
from app.services.geocoding_client import (
    GeocodeCandidate,
    GeocodingClient,
    KakaoGeocodingClient,
    NoopGeocodingClient,
)
from app.services.radius_check_service import GeocodingCandidatesRequiredError, RadiusCheckService

router = APIRouter(prefix="/check-radius", tags=["radius"])

def get_geocoding_client() -> GeocodingClient:
    rest_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not rest_api_key:
        return NoopGeocodingClient()
    return KakaoGeocodingClient(rest_api_key)


def _geocode_required_error(candidates: list[GeocodeCandidate]) -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "GEOCODING_ERROR",
            "message": "지오코딩 후보 선택이 필요합니다.",
            "details": {
                "geocode_candidates": [
                    {
                        "candidate_id": c.candidate_id,
                        "address": c.address,
                        "lat": c.lat,
                        "lng": c.lng,
                    }
                    for c in candidates
                ]
            },
        },
    )


def _geocode_empty_error() -> HTTPException:
    return HTTPException(
        status_code=422,
        detail={
            "code": "GEOCODING_ERROR",
            "message": "지오코딩 결과가 없습니다.",
            "details": None,
        },
    )


@router.post("", response_model=RadiusCheckResponse)
async def check_radius(
    payload: RadiusCheckRequest,
    session: Session = Depends(get_db_session),
    geocoder: GeocodingClient = Depends(get_geocoding_client),
) -> RadiusCheckResponse:
    service = RadiusCheckService(geocoder=geocoder, session=session)
    try:
        result = await service.check_radius(payload)
        log_radius_check(payload.address, result.count)
        return result
    except GeocodingCandidatesRequiredError as exc:
        raise _geocode_required_error(exc.candidates) from exc
    except ValueError as exc:
        if str(exc) == "GEOCODING_EMPTY":
            raise _geocode_empty_error() from exc
        raise
