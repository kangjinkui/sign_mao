from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Billboard(Base):
    __tablename__ = "billboards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    serial_no: Mapped[int] = mapped_column(Integer, nullable=False)
    ad_type: Mapped[str] = mapped_column(String(32), nullable=False)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    permit_date: Mapped[str | None] = mapped_column(Date, nullable=True)
    size_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_address: Mapped[str] = mapped_column(String(500), nullable=False)
    legal_dong: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    lat: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
    lng: Mapped[float | None] = mapped_column(Numeric(10, 7), nullable=True)
