from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional

from app.models import Illustration, Character, Major, Theme, Type

class IllustrationService:
    @staticmethod
    def get_illustrations(
        db: Session,
        page: int = 1,
        limit: int = 20,
        team_id: Optional[int] = None,
        character_id: Optional[int] = None,
        major_id: Optional[int] = None,
        theme_id: Optional[int] = None,
        type_ids: Optional[List[int]] = None
    ):
        query = db.query(Illustration)

        if character_id:
            query = query.filter(Illustration.character_id == character_id)
        
        if team_id:
            query = query.join(Illustration.character).filter(Character.team_id == team_id)

        if major_id:
            query = query.filter(Illustration.major_id == major_id)
        
        if theme_id:
            query = query.filter(Illustration.theme_id == theme_id)

        if type_ids:
            query = query.filter(Illustration.types.any(Type.id.in_(type_ids)))

        total = query.count()

        # 정렬: 최신 항목(id가 큰 것)부터 내림차순 정렬
        query = query.order_by(desc(Illustration.id))

        offset = (page - 1) * limit
        items = query.offset(offset).limit(limit).all()

        return {
            "total": total,
            "page": page,
            "limit": limit,
            "items": items
        }
