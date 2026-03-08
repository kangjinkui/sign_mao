import statistics
import time

from fastapi.testclient import TestClient

from app.main import app


def _p95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = max(0, int(len(ordered) * 0.95) - 1)
    return ordered[idx]


def test_check_radius_p95_under_1s() -> None:
    client = TestClient(app)
    samples: list[float] = []

    for _ in range(100):
        start = time.perf_counter()
        response = client.post("/api/v1/check-radius", json={"address": "서울 강남구 도산대로 306"})
        elapsed = time.perf_counter() - start
        assert response.status_code == 200
        samples.append(elapsed)

    p95 = _p95(samples)
    avg = statistics.mean(samples)
    assert avg < 1.0
    assert p95 < 1.0
