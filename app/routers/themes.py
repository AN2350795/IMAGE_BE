import json
import os
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models import Major, Theme

router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)

# Load the theme filter configuration
FILTER_THEME_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "data", "seed", "filter-theme.json"
)

@router.get("/filter", response_model=Dict[str, Any])
def get_theme_filters(db: Session = Depends(get_db)):
    try:
        with open(FILTER_THEME_PATH, "r", encoding="utf-8") as f:
            filter_data = json.load(f)
    except FileNotFoundError:
        filter_data = {}

    majors = db.query(Major).all()
    themes = db.query(Theme).all()

    major_map = {m.name: m.id for m in majors}
    theme_map = {t.name: t.id for t in themes}

    result = {}
    for major_name, major_info in filter_data.items():
        major_id = major_map.get(major_name)
        
        options = []
        for opt in major_info.get("options", []):
            theme_name = opt.get("value")
            theme_id = theme_map.get(theme_name)
            
            options.append({
                "theme_id": theme_id,
                "value": theme_name,
                "label": opt.get("label")
            })
            
        result[major_name] = {
            "major_id": major_id,
            "options": options
        }

    return result
