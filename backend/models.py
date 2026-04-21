from datetime import datetime, timezone

from sqlalchemy import Column, Integer
from sqlalchemy.types import JSON
from sqlmodel import Field, SQLModel


class Team(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    name: str
    ranking_points: int = Field(default=0, ge=0)


class Match(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    match_type: str = Field(default="Qualification")
    red_team_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    blue_team_ids: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    red_score: int = Field(default=0)
    blue_score: int = Field(default=0)
    winner: int = Field(default=0)
    played: bool = Field(default=False)
    point_breakdown: dict = Field(default_factory=dict, sa_column=Column(JSON))


class RefereeSubmission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    match_id: int = Field(index=True, foreign_key="match.id")
    alliance: str
    minor_faul: int = Field(default=0, ge=0)
    major_faul: int = Field(default=0, ge=0)
    # Keep legacy DB column name for backward compatibility with existing SQLite files.
    fuel_count: int = Field(default=0, ge=0, sa_column=Column("mercan_count", Integer))
    climb_count: int = Field(default=0, ge=0)
    shift_number: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AppConfig(SQLModel, table=True):
    id: int = Field(default=1, primary_key=True)
    stream_url: str = Field(default="http://localhost:8889/live/mfrc/")
    stream_enabled: bool = Field(default=True)
