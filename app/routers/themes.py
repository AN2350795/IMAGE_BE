from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from app.database import get_db
from app.models import Major, Theme, Illustration

from cachetools import cached, TTLCache

router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)

# 최대 1개 항목 보관, 1시간(3600초)마다 만료되는 캐시 생성
theme_filter_cache = TTLCache(maxsize=1, ttl=3600)

@router.get("/filter", response_model=Dict[str, Any])
@cached(theme_filter_cache)
def get_theme_filters(db: Session = Depends(get_db)):

    # Major와 Theme 계층 구조 조회
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
            "label": theme.label or theme.name
        })

    # 반환 전 그룹별 정렬 수행
    for major_name, major_data in result.items():
        if major_name == "일러스트":
            major_data["options"].sort(key=lambda x: x["label"]) 
        else:
            major_data["options"].sort(key=lambda x: x["theme_id"])

    return result
