from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from app.database import get_db
from app.models import Team

from cachetools import cached, TTLCache

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

# 최대 1개 항목 보관, 1시간(3600초)마다 만료되는 캐시 생성
character_filter_cache = TTLCache(maxsize=1, ttl=3600)

@router.get("/filter", response_model=Dict[str, Any])
@cached(character_filter_cache)
def get_character_filter(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    
    result = {}
    for team in teams:
        result[team.name] = {
            "image": f"/img/{team.name}.webp",
            "characters": [
                {"id": c.id, "name": c.name, "image": f"/img/{c.name}.webp"} 
                for c in team.characters
            ]
        }
        
    return result
