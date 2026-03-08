from fastapi.testclient import TestClient

from app.api.v1.check_radius import get_geocoding_client
from app.api.v1.import_billboards import get_import_geocoding_client
from app.main import app
from app.services.geocoding_client import NoopGeocodingClient

# 테스트 환경에서는 외부 API 키 없이 실행되므로 NoopGeocodingClient로 교체한다.
app.dependency_overrides[get_geocoding_client] = lambda: NoopGeocodingClient()
app.dependency_overrides[get_import_geocoding_client] = lambda: NoopGeocodingClient()


def test_client() -> TestClient:
    return TestClient(app)
