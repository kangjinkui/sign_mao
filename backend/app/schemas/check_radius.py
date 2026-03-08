from pydantic import BaseModel, Field


class RadiusCheckRequest(BaseModel):
    address: str = Field(min_length=2)
    selected_candidate_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    legal_dong: str | None = None
    ad_type: str | None = None


class GeocodeCandidateSchema(BaseModel):
    candidate_id: str
    address: str
    lat: float
    lng: float


class RadiusItem(BaseModel):
    company: str
    ad_type: str
    address: str
    lat: float
    lng: float
    distance_m: float


class RadiusInput(BaseModel):
    address: str
    lat: float
    lng: float


class RadiusCheckResponse(BaseModel):
    input: RadiusInput
    radius: int = 200
    count: int
    items: list[RadiusItem]
    geocode_candidates: list[GeocodeCandidateSchema] = []
