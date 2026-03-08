from app.services.geocoding_client import GeocodeCandidate


MAX_CANDIDATES = 5


def limit_candidates(candidates: list[GeocodeCandidate]) -> list[GeocodeCandidate]:
    return candidates[:MAX_CANDIDATES]


def resolve_candidate(
    candidates: list[GeocodeCandidate], selected_candidate_id: str | None
) -> GeocodeCandidate | None:
    if not candidates:
        return None
    if selected_candidate_id:
        for candidate in candidates:
            if candidate.candidate_id == selected_candidate_id:
                return candidate
        return None
    if len(candidates) == 1:
        return candidates[0]
    return None
