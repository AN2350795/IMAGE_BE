from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.sql_echo,
    # 컨테이너 재시작 등으로 끊긴 커넥션을 재사용하지 않도록 검사한다.
    pool_pre_ping=True,
    # MySQL 의 wait_timeout(기본 8시간) 보다 먼저 커넥션을 교체한다.
    pool_recycle=3600,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """모든 ORM 모델이 상속할 기반 클래스."""


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
