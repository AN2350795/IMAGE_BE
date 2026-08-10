from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, List, Any

from app.database import get_db
from app.models import Team

router = APIRouter(
    prefix="/characters",
    tags=["characters"]
)

@router.get("/filter", response_model=Dict[str, Any])
def get_character_filter(db: Session = Depends(get_db)):
    teams = db.query(Team).all()
    
    result = {}
    for team in teams:
        result[team.name] = {
            "image": f"/img/{team.name}.webp",
            "characters": [
                {"name": c.name, "image": f"/img/{c.name}.webp"} 
                for c in team.characters
            ]
        }
        
    return result
