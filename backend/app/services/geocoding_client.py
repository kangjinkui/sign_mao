from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import Request, urlopen
import json


@dataclass(slots=True)
class GeocodeCandidate:
    candidate_id: str
    address: str
    lat: float
    lng: float


class GeocodingClient:
    async def search(self, address: str) -> list[GeocodeCandidate]:
        return self.search_sync(address)

    def search_sync(self, address: str) -> list[GeocodeCandidate]:
        raise NotImplementedError("지오코딩 공급자 어댑터 구현이 필요합니다.")


class NoopGeocodingClient(GeocodingClient):
    def search_sync(self, address: str) -> list[GeocodeCandidate]:
        return []


class KakaoGeocodingClient(GeocodingClient):
    def __init__(self, rest_api_key: str, *, timeout_sec: float = 5.0):
        self._rest_api_key = rest_api_key
        self._timeout_sec = timeout_sec

    def search_sync(self, address: str) -> list[GeocodeCandidate]:
        query = quote(address.strip())
        if not query:
            return []

        req = Request(
            f"https://dapi.kakao.com/v2/local/search/address.json?query={query}",
            headers={"Authorization": f"KakaoAK {self._rest_api_key}"},
        )
        with urlopen(req, timeout=self._timeout_sec) as response:
            payload = json.loads(response.read().decode("utf-8"))

        documents = payload.get("documents", [])
        candidates: list[GeocodeCandidate] = []
        for index, item in enumerate(documents):
            road_address = item.get("road_address") or {}
            address_obj = item.get("address") or {}
            address_name = road_address.get("address_name") or address_obj.get("address_name")
            y = road_address.get("y") or address_obj.get("y")
            x = road_address.get("x") or address_obj.get("x")
            if not address_name or not y or not x:
                continue
            candidates.append(
                GeocodeCandidate(
                    candidate_id=f"kakao-{index}",
                    address=str(address_name),
                    lat=float(y),
                    lng=float(x),
                )
            )
        return candidates
