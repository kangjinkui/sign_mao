import os

from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/auth", tags=["auth"])


def require_admin(x_admin_secret: str = Header(...)):
    secret = os.getenv("ADMIN_SECRET", "")
    if not secret or x_admin_secret != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/verify")
def verify_admin(x_admin_secret: str = Header(...)):
    secret = os.getenv("ADMIN_SECRET", "")
    if not secret or x_admin_secret != secret:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"ok": True}
