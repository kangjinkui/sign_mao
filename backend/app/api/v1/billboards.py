from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db.session import get_db_session
from app.api.v1.auth import require_admin

router = APIRouter(prefix="/billboards", tags=["billboards"])


@router.get("")
def list_billboards(
    limit: int = 200,
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    rows = session.execute(
        text(
            """
            SELECT
              id,
              company_name AS company,
              ad_type,
              display_address AS address,
              lat::double precision AS lat,
              lng::double precision AS lng,
              permit_date,
              size_text
            FROM billboards
            WHERE status = 'ACTIVE'
            ORDER BY id ASC
            LIMIT :limit
            """
        ),
        {"limit": max(1, min(limit, 1000))},
    ).mappings().all()
    return {
        "count": len(rows),
        "items": [
            {
                "id": int(row["id"]),
                "company": str(row["company"]),
                "ad_type": str(row["ad_type"]),
                "address": str(row["address"]),
                "lat": float(row["lat"]) if row["lat"] is not None else None,
                "lng": float(row["lng"]) if row["lng"] is not None else None,
                "permit_date": str(row["permit_date"]) if row["permit_date"] is not None else None,
                "size_text": str(row["size_text"]) if row["size_text"] is not None else None,
            }
            for row in rows
        ],
    }


class BillboardCreate(BaseModel):
    company_name: str
    ad_type: str
    display_address: str
    permit_date: str | None = None
    size_text: str | None = None
    lat: float | None = None
    lng: float | None = None


@router.post("", dependencies=[Depends(require_admin)])
def create_billboard(
    body: BillboardCreate,
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    row = session.execute(
        text(
            """
            INSERT INTO billboards
              (serial_no, company_name, ad_type, display_address, permit_date, size_text, lat, lng, status)
            VALUES (
              COALESCE((SELECT MAX(serial_no) FROM billboards), 0) + 1,
              :company_name, :ad_type, :display_address,
              :permit_date, :size_text,
              :lat, :lng,
              'ACTIVE'
            )
            RETURNING id
            """
        ),
        body.model_dump(),
    ).fetchone()
    session.commit()
    return {"id": row[0]}


class BillboardUpdate(BaseModel):
    company_name: str | None = None
    ad_type: str | None = None
    display_address: str | None = None
    permit_date: str | None = None
    size_text: str | None = None
    lat: float | None = None
    lng: float | None = None


@router.patch("/{billboard_id}", dependencies=[Depends(require_admin)])
def update_billboard(
    billboard_id: int,
    body: BillboardUpdate,
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    fields = {k: v for k, v in body.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(status_code=422, detail="변경할 필드가 없습니다.")

    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    fields["billboard_id"] = billboard_id
    result = session.execute(
        text(f"UPDATE billboards SET {set_clause} WHERE id = :billboard_id AND status = 'ACTIVE'"),
        fields,
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="광고물을 찾을 수 없습니다.")
    session.commit()
    return {"ok": True}


@router.delete("/{billboard_id}", dependencies=[Depends(require_admin)])
def delete_billboard(
    billboard_id: int,
    session: Session = Depends(get_db_session),
) -> dict[str, object]:
    result = session.execute(
        text("UPDATE billboards SET status = 'DELETED' WHERE id = :id AND status = 'ACTIVE'"),
        {"id": billboard_id},
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="광고물을 찾을 수 없습니다.")
    session.commit()
    return {"ok": True}
