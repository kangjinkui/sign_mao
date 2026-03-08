"""initial schema: billboards and import_job_logs

Revision ID: 0001
Revises:
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PostGIS 확장 활성화
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # billboards 테이블
    op.create_table(
        "billboards",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("serial_no", sa.Integer(), nullable=False),
        sa.Column("ad_type", sa.String(32), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("permit_date", sa.Date(), nullable=True),
        sa.Column("size_text", sa.Text(), nullable=True),
        sa.Column("display_address", sa.String(500), nullable=False),
        sa.Column("legal_dong", sa.String(100), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("lng", sa.Numeric(10, 7), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # geom 컬럼 추가 (GeoAlchemy2 없이 raw DDL 사용)
    op.execute(
        "ALTER TABLE billboards ADD COLUMN geom geometry(Point, 4326)"
    )

    # 공간 인덱스
    op.execute(
        "CREATE INDEX idx_billboards_geom ON billboards USING GIST (geom)"
    )

    # status 인덱스 (필터 쿼리 성능)
    op.create_index("idx_billboards_status", "billboards", ["status"])

    # legal_dong 인덱스 (필터 쿼리 성능)
    op.create_index("idx_billboards_legal_dong", "billboards", ["legal_dong"])

    # import_job_logs 테이블
    op.create_table(
        "import_job_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("source_file_name", sa.String(255), nullable=False),
        sa.Column("source_file_path", sa.String(500), nullable=False),
        sa.Column("rule_version", sa.String(50), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(100), nullable=False, server_default="system"),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("import_job_logs")
    op.execute("DROP INDEX IF EXISTS idx_billboards_legal_dong")
    op.execute("DROP INDEX IF EXISTS idx_billboards_status")
    op.execute("DROP INDEX IF EXISTS idx_billboards_geom")
    op.drop_table("billboards")
