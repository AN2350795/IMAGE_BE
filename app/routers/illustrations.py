from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas import IllustrationListResponse
from app.services import IllustrationService

router = APIRouter(
    prefix="/illustrations",
    tags=["illustrations"]
)

@router.get("", response_model=IllustrationListResponse)
def get_illustrations(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지 당 항목 수"),
    team_id: Optional[int] = Query(None, description="필터: 팀 ID"),
    character_id: Optional[List[int]] = Query(None, description="필터: 캐릭터 ID"),
    major_id: Optional[int] = Query(None, description="필터: 대분류 ID"),
    theme_id: Optional[List[int]] = Query(None, description="필터: 테마 ID"),
    type_ids: Optional[List[int]] = Query(None, description="필터: 여러 유형 ID 목록"),
    db: Session = Depends(get_db)
):
    """
    일러스트 목록 조회 (필터링 및 페이징 지원)
    """
    return IllustrationService.get_illustrations(
        db=db,
        page=page,
        limit=limit,
        team_id=team_id,
        character_id=character_id,
        major_id=major_id,
        theme_id=theme_id,
        type_ids=type_ids
    )
