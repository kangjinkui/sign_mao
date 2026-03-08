import os

import pytest

from app.api.v1.check_radius import get_geocoding_client
from app.api.v1.import_billboards import get_import_geocoding_client
from app.main import app
from app.services.geocoding_client import NoopGeocodingClient

# 테스트 환경에서는 외부 API 키 없이 실행되므로 NoopGeocodingClient로 교체한다.
app.dependency_overrides[get_geocoding_client] = lambda: NoopGeocodingClient()
app.dependency_overrides[get_import_geocoding_client] = lambda: NoopGeocodingClient()


@pytest.fixture(scope="session")
def db_url() -> str:
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "15432")
    name = os.getenv("DB_NAME", "sign_map")
    user = os.getenv("DB_USER", "sign_map")
    password = os.getenv("DB_PASSWORD", "sign_map")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{name}"
