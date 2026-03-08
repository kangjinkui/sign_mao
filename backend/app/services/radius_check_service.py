from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.schemas.check_radius import (
    GeocodeCandidateSchema,
    RadiusCheckRequest,
    RadiusCheckResponse,
    RadiusInput,
    RadiusItem,
)
from app.services.geocoding_client import GeocodeCandidate, GeocodingClient
from app.services.geocoding_resolution import limit_candidates, resolve_candidate
from app.services.spatial_query import query_radius


@dataclass(slots=True)
class GeocodingCandidatesRequiredError(Exception):
    candidates: list[GeocodeCandidate]


class RadiusCheckService:
    def __init__(self, geocoder: GeocodingClient, session: Session):
        self._geocoder = geocoder
        self._session = session

    async def check_radius(self, payload: RadiusCheckRequest) -> RadiusCheckResponse:
        if payload.lat is not None and payload.lng is not None:
            resolved = GeocodeCandidate(
                candidate_id=payload.selected_candidate_id or "client-input",
                address=payload.address,
                lat=payload.lat,
                lng=payload.lng,
            )
            candidates = [resolved]
        else:
            candidates = limit_candidates(await self._geocoder.search(payload.address))
            resolved = resolve_candidate(candidates, payload.selected_candidate_id)

            if not candidates:
                raise ValueError("GEOCODING_EMPTY")

            if resolved is None:
                raise GeocodingCandidatesRequiredError(candidates=candidates)

        # 초기 부트스트랩 단계에서 테이블 미생성 상태일 수 있어, 조회 실패 시 빈 결과로 처리한다.
        try:
            items = query_radius(
                self._session,
                lat=resolved.lat,
                lng=resolved.lng,
                radius_m=200,
                legal_dong=payload.legal_dong,
                ad_type=payload.ad_type,
            )
        except Exception:
            items = []

        return RadiusCheckResponse(
            input=RadiusInput(address=payload.address, lat=resolved.lat, lng=resolved.lng),
            radius=200,
            count=len(items),
            items=[RadiusItem(**item) for item in items],
            geocode_candidates=[
                GeocodeCandidateSchema(
                    candidate_id=item.candidate_id,
                    address=item.address,
                    lat=item.lat,
                    lng=item.lng,
                )
                for item in candidates
            ],
        )
