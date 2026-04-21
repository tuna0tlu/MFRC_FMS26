from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TeamCreate(BaseModel):
    id: str
    name: str


class TeamUpdate(BaseModel):
    name: str | None = None
    ranking_points: int | None = Field(default=None, ge=0)


class TeamRead(BaseModel):
    id: str
    name: str
    ranking_points: int


class MatchCreate(BaseModel):
    match_type: Literal["Qualification", "Elimination", "Final"] = "Qualification"
    red_team_ids: list[str] = Field(min_length=1)
    blue_team_ids: list[str] = Field(min_length=1)


class MatchRead(BaseModel):
    id: int
    match_type: str
    red_team_ids: list[str]
    blue_team_ids: list[str]
    red_score: int
    blue_score: int
    winner: int
    played: bool
    point_breakdown: dict


class RefereeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    alliance: Literal["red", "blue"]
    minor_faul: int = Field(alias="minorFaul", ge=0)
    major_faul: int = Field(alias="majorFaul", ge=0)
    season_specific_values: list[int] = Field(alias="seasonSpecificValues", min_length=2, max_length=2)
    climb_selections: list[Literal["L1", "L2", "L3"] | None] | None = Field(
        default=None,
        alias="climbSelections",
        min_length=3,
        max_length=3,
    )


class RefereeResponse(BaseModel):
    status: str
    red_score: int
    blue_score: int
    shift_number: int


class ScorekeeperResponse(BaseModel):
    status: str
    alliance: Literal["red", "blue"]
    fuel_count: int
    delta: int
    red_score: int
    blue_score: int


class StatusResponse(BaseModel):
    status: str


class MessageResponse(BaseModel):
    status: str
    detail: str


class StreamSettingsRead(BaseModel):
    stream_url: str
    stream_enabled: bool


class StreamSettingsUpdate(BaseModel):
    stream_url: str = Field(min_length=1)
    stream_enabled: bool


class StreamProbeResponse(BaseModel):
    status: str
    reachable: bool
    http_status: int | None = None
    detail: str | None = None
