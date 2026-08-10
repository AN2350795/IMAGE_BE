import json
import os
import sys
from pathlib import Path

# Add the parent directory of 'scripts' to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Illustration, Team, Character, Major, Theme, Type

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def seed():
    # Make sure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Define paths
    base_dir = Path(__file__).resolve().parent.parent
    seed_dir = base_dir / "data" / "seed"
    filter_char_path = seed_dir / "filter-char.json"
    filter_theme_path = seed_dir / "filter-theme.json"
    output_path = seed_dir / "output.json"

    # Load data
    print("Loading data files...")
    filter_char_data = load_json(filter_char_path)
    filter_theme_data = load_json(filter_theme_path)
    output_data = load_json(output_path)
    print(f"Loaded {len(output_data)} illustrations from output.json")

    # Dictionaries to keep track of objects
    teams = {}
    characters = {}
    majors = {}
    themes = {}
    types = {}

    try:
        # --- 1. Populate Teams and Characters based on filter-char.json ---
        print("Populating Teams and Characters...")
        
        # Build character name map from output.json (fullname -> short name)
        char_name_map = {}
        for item in output_data:
            t_name = item.get("team")
            c_short = item.get("character")
            c_full = item.get("character_fullname")
            if t_name and c_short and c_full:
                if t_name not in char_name_map:
                    char_name_map[t_name] = {}
                char_name_map[t_name][c_full] = c_short

        team_idx = 1
        for team_name, team_info in filter_char_data.items():
            team = db.query(Team).filter_by(id=team_idx).first()
            if not team:
                team = Team(id=team_idx, name=team_name)
                db.add(team)
                db.flush() # flush to get ID
            elif team.name != team_name:
                team.name = team_name
                db.flush()
            teams[team_name] = team

            char_idx = 1
            for char_info in team_info.get("characters", []):
                # filter-char.json 의 "name" 필드에는 풀네임(예: 윤리아, 김철수)이 들어있음
                char_fullname = char_info.get("name")
                # output.json 의 데이터를 바탕으로 풀네임에서 짧은 이름(예: 리아, 철수)을 찾음
                char_shortname = char_name_map.get(team_name, {}).get(char_fullname, char_fullname)
                
                target_char_id = team_idx * 100 + char_idx
                
                char = db.query(Character).filter_by(id=target_char_id).first()
                if not char:
                    char = Character(id=target_char_id, name=char_shortname, fullname=char_fullname, team_id=team.id)
                    db.add(char)
                    db.flush()
                else:
                    char.name = char_shortname
                    char.fullname = char_fullname
                    char.team_id = team.id
                    db.flush()
                characters[char_fullname] = char
                char_idx += 1
            
            team_idx += 1
        
        # --- 2. Populate Majors and Themes based on filter-theme.json ---
        print("Populating Majors and Themes...")
        for major_name, major_info in filter_theme_data.items():
            major = db.query(Major).filter_by(name=major_name).first()
            if not major:
                major = Major(name=major_name)
                db.add(major)
                db.flush()
            majors[major_name] = major

            for theme_info in major_info.get("options", []):
                theme_name = theme_info.get("value")
                theme = db.query(Theme).filter_by(name=theme_name).first()
                if not theme:
                    theme = Theme(name=theme_name)
                    db.add(theme)
                    db.flush()
                themes[theme_name] = theme

        # --- 3. Populate Types (Dynamic from output.json, just in order of appearance) ---
        print("Populating Types...")
        for item in output_data:
            item_types = item.get("type", [])
            for type_name in item_types:
                if type_name not in types:
                    type_obj = db.query(Type).filter_by(name=type_name).first()
                    if not type_obj:
                        type_obj = Type(name=type_name)
                        db.add(type_obj)
                        db.flush()
                    types[type_name] = type_obj
        
        db.commit()
        
        # Reload characters into dict if not fully mapped by name
        # Because output.json uses character_fullname 
        for c in db.query(Character).all():
            characters[c.fullname] = c

        # --- 4. Insert/Update Illustrations in reverse order (bottom to top, oldest first) ---
        print("Caching existing illustrations...")
        # Pre-fetch all illustrations to memory (dict by path) for O(1) lookup
        existing_ills = {ill.path: ill for ill in db.query(Illustration).all()}

        print("Processing illustrations...")
        new_illustrations = 0
        updated_illustrations = 0
        for item in reversed(output_data):
            path = item.get("path")
            expected_char_fullname = item.get("character_fullname")
            
            raw_major_name = item.get("major")
            major_name = raw_major_name.replace(" 아바타", "") if raw_major_name else None
            
            theme_name = item.get("theme")
            item_types = item.get("type", [])
            
            # Fetch objects
            char_id = characters[expected_char_fullname].id if expected_char_fullname in characters else None
            major_id = majors[major_name].id if major_name in majors else None
            theme_id = themes[theme_name].id if theme_name in themes else None
            type_objs = [types[t] for t in item_types if t in types]
            
            order = item.get("order", 0)
            is_new = item.get("is_new", False)
            extra = item.get("extra", [])
            
            existing_ill = existing_ills.get(path)
            if not existing_ill:
                ill = Illustration(
                    filename=item.get("filename"),
                    path=path,
                    character_id=char_id,
                    major_id=major_id,
                    theme_id=theme_id,
                    order=order,
                    is_new=is_new,
                    extra=extra,
                    types=type_objs
                )
                db.add(ill)
                new_illustrations += 1
                
                # Commit periodically
                if new_illustrations % 1000 == 0:
                    db.commit()
            else:
                # Check for updates to sync DB with JSON changes
                needs_update = False
                if existing_ill.character_id != char_id:
                    existing_ill.character_id = char_id
                    needs_update = True
                if existing_ill.major_id != major_id:
                    existing_ill.major_id = major_id
                    needs_update = True
                if existing_ill.theme_id != theme_id:
                    existing_ill.theme_id = theme_id
                    needs_update = True
                if existing_ill.order != order:
                    existing_ill.order = order
                    needs_update = True
                if existing_ill.is_new != is_new:
                    existing_ill.is_new = is_new
                    needs_update = True
                if existing_ill.extra != extra:
                    existing_ill.extra = extra
                    needs_update = True
                
                current_type_ids = {t.id for t in existing_ill.types}
                new_type_ids = {t.id for t in type_objs}
                if current_type_ids != new_type_ids:
                    existing_ill.types = type_objs
                    needs_update = True
                    
                if needs_update:
                    updated_illustrations += 1
                    if updated_illustrations % 1000 == 0:
                        db.commit()

        # Final commit for illustrations
        db.commit()
        print(f"Successfully seeded {new_illustrations} new illustrations, updated {updated_illustrations} illustrations.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
