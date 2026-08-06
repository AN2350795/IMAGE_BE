from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from app.database import Base

illustration_types = Table(
    "illustration_types",
    Base.metadata,
    Column("illustration_id", Integer, ForeignKey("illustrations.id", ondelete="CASCADE"), primary_key=True),
    Column("type_id", Integer, ForeignKey("types.id", ondelete="CASCADE"), primary_key=True),
)

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    characters = relationship("Character", back_populates="team")

class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    fullname = Column(String(100), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)

    team = relationship("Team", back_populates="characters")
    illustrations = relationship("Illustration", back_populates="character")

class Major(Base):
    __tablename__ = "majors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    illustrations = relationship("Illustration", back_populates="major")

class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)

    illustrations = relationship("Illustration", back_populates="theme")

class Type(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

    illustrations = relationship("Illustration", secondary=illustration_types, back_populates="types")

class Illustration(Base):
    __tablename__ = "illustrations"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    
    character_id = Column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=True)
    major_id = Column(Integer, ForeignKey("majors.id", ondelete="SET NULL"), nullable=True)
    theme_id = Column(Integer, ForeignKey("themes.id", ondelete="SET NULL"), nullable=True)
    
    order = Column(Integer, default=0, nullable=False)
    is_new = Column(Boolean, default=False, nullable=False)
    extra = Column(JSON, nullable=True)

    character = relationship("Character", back_populates="illustrations")
    major = relationship("Major", back_populates="illustrations")
    theme = relationship("Theme", back_populates="illustrations")
    types = relationship("Type", secondary=illustration_types, back_populates="illustrations")
