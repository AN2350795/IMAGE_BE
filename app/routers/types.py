from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Type
from app.schemas.illustration import TypeResponse

from cachetools import cached, TTLCache

router = APIRouter(
    prefix="/types",
    tags=["types"]
)

# 최대 1개 항목 보관, 1시간(3600초)마다 만료되는 캐시 생성
type_filter_cache = TTLCache(maxsize=1, ttl=3600)

@router.get("/filter", response_model=List[TypeResponse])
@cached(type_filter_cache)
def get_type_filters(db: Session = Depends(get_db)):
    types = db.query(Type).order_by(Type.id).all()
    return types
