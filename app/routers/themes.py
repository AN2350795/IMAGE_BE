from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database import get_db
from app.models import Major, Theme, Illustration

router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)

# 인메모리 캐시 변수
_THEME_FILTER_CACHE: Optional[Dict[str, Any]] = None

@router.get("/filter", response_model=Dict[str, Any])
def get_theme_filters(db: Session = Depends(get_db)):
    global _THEME_FILTER_CACHE
    
    # 1. 캐시 히트 시 즉시 반환
    if _THEME_FILTER_CACHE is not None:
        return _THEME_FILTER_CACHE

    # 2. DB를 통해 Major와 Theme 계층 구조 조회
    # (Illustration 테이블을 통해 두 테이블 간의 연관 관계를 확인)
    results = db.query(Major, Theme)\
        .join(Illustration, Illustration.major_id == Major.id)\
        .join(Theme, Illustration.theme_id == Theme.id)\
        .distinct()\
        .all()

    result = {}
    for major, theme in results:
        major_name = major.name
        
        # 대분류가 처음 등장하면 뼈대 생성
        if major_name not in result:
            result[major_name] = {
                "major_id": major.id,
                "options": []
            }
            
        # 해당 대분류의 테마 옵션 추가
        result[major_name]["options"].append({
            "theme_id": theme.id,
            "value": theme.name,
            "label": theme.name
        })

    # 3. 결과 캐싱 및 반환
    _THEME_FILTER_CACHE = result
    return result
