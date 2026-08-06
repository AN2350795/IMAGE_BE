from pydantic import BaseModel
from typing import List, Optional

class TypeResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class ThemeResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class MajorResponse(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes = True

class CharacterResponse(BaseModel):
    id: int
    name: str
    fullname: str
    team_id: Optional[int]
    class Config:
        from_attributes = True

class IllustrationResponse(BaseModel):
    id: int
    filename: str
    path: str
    character: Optional[CharacterResponse] = None
    major: Optional[MajorResponse] = None
    theme: Optional[ThemeResponse] = None
    types: List[TypeResponse] = []
    order: int
    is_new: bool
    
    class Config:
        from_attributes = True

class IllustrationListResponse(BaseModel):
    total: int
    page: int
    limit: int
    items: List[IllustrationResponse]
