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
        for team_name, team_info in filter_char_data.items():
            team = db.query(Team).filter_by(name=team_name).first()
            if not team:
                team = Team(name=team_name)
                db.add(team)
                db.flush() # flush to get ID
            teams[team_name] = team

            for char_info in team_info.get("characters", []):
                char_name = char_info.get("name")
                char_fullname = f"{team_name} {char_name}"
                
                char = db.query(Character).filter_by(fullname=char_fullname).first()
                if not char:
                    char = Character(name=char_name, fullname=char_fullname, team_id=team.id)
                    db.add(char)
                    db.flush()
                characters[char_fullname] = char
        
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

        # --- 4. Insert Illustrations in reverse order (bottom to top, oldest first) ---
        print("Inserting illustrations in reverse order...")
        new_illustrations = 0
        for item in reversed(output_data):
            path = item.get("path")
            existing_ill = db.query(Illustration).filter(Illustration.path == path).first()
            if not existing_ill:
                char_fullname = item.get("character_fullname")
                major_name = item.get("major")
                theme_name = item.get("theme")
                item_types = item.get("type", [])
                
                # Fetch objects
                char_id = characters[char_fullname].id if char_fullname in characters else None
                major_id = majors[major_name].id if major_name in majors else None
                theme_id = themes[theme_name].id if theme_name in themes else None
                type_objs = [types[t] for t in item_types if t in types]
                
                ill = Illustration(
                    filename=item.get("filename"),
                    path=path,
                    character_id=char_id,
                    major_id=major_id,
                    theme_id=theme_id,
                    order=item.get("order", 0),
                    is_new=item.get("is_new", False),
                    extra=item.get("extra", []),
                    types=type_objs
                )
                db.add(ill)
                new_illustrations += 1
                
                # Commit every 100 insertions
                if new_illustrations % 100 == 0:
                    db.commit()

        # Final commit for illustrations
        db.commit()
        print(f"Successfully seeded {new_illustrations} new illustrations.")

    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed()
