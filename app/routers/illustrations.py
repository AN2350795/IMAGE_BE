from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import IllustrationListResponse
from app.services import IllustrationService

router = APIRouter(
    prefix="/illustrations",
    tags=["illustrations"]
)

def parse_int_list(query: Optional[str] = None) -> Optional[List[int]]:
    """쉼표로 구분된 문자열을 List[int]로 변환하는 헬퍼 함수"""
    if not query:
        return None
    try:
        return [int(x.strip()) for x in query.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid list format. Expected comma-separated integers.")

@router.get("", response_model=IllustrationListResponse)
def get_illustrations(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지 당 항목 수"),
    team_id: Optional[int] = Query(None, description="필터: 팀 ID"),
    character_id: Optional[str] = Query(None, description="필터: 캐릭터 ID (쉼표로 구분, 예: 1,2)"),
    major_id: Optional[int] = Query(None, description="필터: 대분류 ID"),
    theme_id: Optional[str] = Query(None, description="필터: 테마 ID (쉼표로 구분, 예: 1,2)"),
    type_ids: Optional[str] = Query(None, description="필터: 여러 유형 ID (쉼표로 구분, 예: 1,2)"),
    db: Session = Depends(get_db)
):
    """
    일러스트 목록 조회 (필터링 및 페이징 지원)
    """
    # 쉼표로 구분된 문자열을 List[int]로 변환
    parsed_character_ids = parse_int_list(character_id)
    parsed_theme_ids = parse_int_list(theme_id)
    parsed_type_ids = parse_int_list(type_ids)

    return IllustrationService.get_illustrations(
        db=db,
        page=page,
        limit=limit,
        team_id=team_id,
        character_id=parsed_character_ids,
        major_id=major_id,
        theme_id=parsed_theme_ids,
        type_ids=parsed_type_ids
    )
