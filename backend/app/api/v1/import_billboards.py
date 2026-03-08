import os

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.db.session import get_db_session
from app.services.billboard_import_service import BillboardImportService
from app.services.geocoding_client import GeocodingClient, KakaoGeocodingClient

router = APIRouter(prefix="/import/billboards", tags=["import"])


def get_import_geocoding_client() -> GeocodingClient:
    rest_api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()
    if not rest_api_key:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "KAKAO_REST_API_KEY가 설정되지 않았습니다.",
                "details": None,
            },
        )
    return KakaoGeocodingClient(rest_api_key)


@router.post("", status_code=202)
async def import_billboards(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
    geocoder: GeocodingClient = Depends(get_import_geocoding_client),
) -> dict[str, str | int]:
    service = BillboardImportService(session=session, geocoder=geocoder)
    try:
        content = await file.read()
        result = service.import_uploaded_file(filename=file.filename or "", content=content)
        return {
            "job_id": result.job_id,
            "status": "STARTED",
            "success_count": result.success_count,
            "failed_count": result.failed_count,
        }
    except ValueError as exc:
        if str(exc) == "EMPTY_FILENAME":
            raise HTTPException(
                status_code=400,
                detail={"code": "VALIDATION_ERROR", "message": "파일명이 비어 있습니다.", "details": None},
            ) from exc
        if str(exc) == "INVALID_FILE_TYPE":
            raise HTTPException(
                status_code=400,
                detail={"code": "VALIDATION_ERROR", "message": "xlsx 파일만 업로드할 수 있습니다.", "details": None},
            ) from exc
        raise
    except RuntimeError as exc:
        if str(exc) == "DB_WRITE_FAILED":
            raise HTTPException(
                status_code=500,
                detail={"code": "INTERNAL_ERROR", "message": "DB 저장에 실패했습니다.", "details": None},
            ) from exc
        raise
