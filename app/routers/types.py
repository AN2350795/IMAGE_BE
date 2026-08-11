from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Type
from app.schemas.illustration import TypeResponse

router = APIRouter(
    prefix="/types",
    tags=["types"]
)

@router.get("/filter", response_model=List[TypeResponse])
def get_type_filters(db: Session = Depends(get_db)):
    """
    유형 필터 목록 조회
    """
    types = db.query(Type).order_by(Type.id).all()
    return types
