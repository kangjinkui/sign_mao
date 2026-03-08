from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas.error import ErrorCode


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={
                "code": ErrorCode.VALIDATION_ERROR.value,
                "message": "요청 유효성 검증에 실패했습니다.",
                "details": {"errors": exc.errors()},
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        if isinstance(exc.detail, dict) and {"code", "message"}.issubset(exc.detail.keys()):
            payload = {
                "code": exc.detail["code"],
                "message": exc.detail["message"],
                "details": exc.detail.get("details"),
            }
            return JSONResponse(status_code=exc.status_code, content=payload)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": str(exc.detail),
                "details": None,
            },
        )

    @app.exception_handler(Exception)
    async def default_exception_handler(_: Request, __: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "code": ErrorCode.INTERNAL_ERROR.value,
                "message": "내부 서버 오류가 발생했습니다.",
                "details": None,
            },
        )
