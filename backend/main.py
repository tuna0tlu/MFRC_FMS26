from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .db import create_db_and_tables, get_session
from .models import Match, Team
from .schemas import (
    MatchCreate,
    MatchRead,
    MessageResponse,
    RefereeRequest,
    RefereeResponse,
    ScorekeeperResponse,
    StreamProbeResponse,
    StreamSettingsRead,
    StreamSettingsUpdate,
    StatusResponse,
    TeamCreate,
    TeamRead,
    TeamUpdate,
)
from .service import FMSService

service = FMSService()


def serialize_match(match: Match) -> MatchRead:
    return MatchRead(
        id=match.id,
        match_type=match.match_type,
        red_team_ids=[str(team_id) for team_id in match.red_team_ids],
        blue_team_ids=[str(team_id) for team_id in match.blue_team_ids],
        red_score=match.red_score,
        blue_score=match.blue_score,
        winner=match.winner,
        played=match.played,
        point_breakdown=match.point_breakdown,
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables()
    yield
    await service.shutdown()


app = FastAPI(title="Mini FRC FMS Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.websocket("/audis/ws")
async def audis_ws(websocket: WebSocket) -> None:
    await service.connect_websocket(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await service.disconnect_websocket(websocket)
    except Exception:
        await service.disconnect_websocket(websocket)


@app.post("/game/referee", response_model=RefereeResponse)
async def game_referee(payload: RefereeRequest) -> RefereeResponse:
    fuel_count = payload.season_specific_values[0]
    climb_count = payload.season_specific_values[1]

    response = await service.apply_referee_submission(
        alliance=payload.alliance,
        minor_faul=payload.minor_faul,
        major_faul=payload.major_faul,
        fuel_count=fuel_count,
        climb_count=climb_count,
        climb_selections=payload.climb_selections,
    )
    return RefereeResponse(**response)


@app.post("/game/scorekeeper", response_model=ScorekeeperResponse)
async def game_scorekeeper(fuel: int = Query(..., ge=0)) -> ScorekeeperResponse:
    fuel_count = fuel
    response = await service.apply_scorekeeper_submission(fuel_count=fuel_count)
    return ScorekeeperResponse(**response)


@app.post("/admin/teams", response_model=TeamRead)
async def create_team(payload: TeamCreate, session: Session = Depends(get_session)) -> TeamRead:
    existing = session.get(Team, payload.id)
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Team {payload.id} already exists")

    team = Team(id=payload.id, name=payload.name)
    session.add(team)
    session.commit()
    session.refresh(team)
    await service.broadcast_leaderboard_if_active()
    return TeamRead(id=team.id, name=team.name, ranking_points=team.ranking_points)


@app.get("/admin/teams", response_model=list[TeamRead])
def list_teams(session: Session = Depends(get_session)) -> list[TeamRead]:
    teams = session.exec(select(Team).order_by(Team.ranking_points.desc(), Team.id.asc())).all()
    return [TeamRead(id=team.id, name=team.name, ranking_points=team.ranking_points) for team in teams]


@app.put("/admin/teams/{team_id}", response_model=TeamRead)
async def update_team(team_id: str, payload: TeamUpdate, session: Session = Depends(get_session)) -> TeamRead:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    if payload.name is not None:
        team.name = payload.name
    if payload.ranking_points is not None:
        team.ranking_points = payload.ranking_points

    session.add(team)
    session.commit()
    session.refresh(team)
    await service.broadcast_leaderboard_if_active()
    return TeamRead(id=team.id, name=team.name, ranking_points=team.ranking_points)


@app.delete("/admin/teams/{team_id}", response_model=StatusResponse)
async def delete_team(team_id: str, session: Session = Depends(get_session)) -> StatusResponse:
    team = session.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team {team_id} not found")

    session.delete(team)
    session.commit()
    await service.broadcast_leaderboard_if_active()
    return StatusResponse(status="ok")


@app.post("/admin/matches", response_model=MatchRead)
def create_match(payload: MatchCreate, session: Session = Depends(get_session)) -> MatchRead:
    overlapping = set(payload.red_team_ids).intersection(payload.blue_team_ids)
    if overlapping:
        raise HTTPException(
            status_code=400,
            detail=f"A team cannot be in both alliances: {', '.join(sorted(overlapping))}",
        )

    required_ids = set(payload.red_team_ids + payload.blue_team_ids)
    found_teams = session.exec(select(Team).where(Team.id.in_(required_ids))).all()
    found_ids = {team.id for team in found_teams}
    missing = sorted(required_ids - found_ids)
    if missing:
        raise HTTPException(status_code=400, detail=f"Unknown team IDs: {', '.join(missing)}")

    match = Match(
        match_type=payload.match_type,
        red_team_ids=[str(team_id) for team_id in payload.red_team_ids],
        blue_team_ids=[str(team_id) for team_id in payload.blue_team_ids],
        red_score=0,
        blue_score=0,
        winner=0,
        played=False,
        point_breakdown={},
    )
    session.add(match)
    session.commit()
    session.refresh(match)
    return serialize_match(match)


@app.get("/admin/matches", response_model=list[MatchRead])
def list_matches(session: Session = Depends(get_session)) -> list[MatchRead]:
    matches = session.exec(select(Match).order_by(Match.id.asc())).all()
    return [serialize_match(match) for match in matches]


@app.post("/admin/matches/{match_id}/prematch", response_model=StatusResponse)
async def admin_prematch(match_id: int) -> StatusResponse:
    await service.broadcast_prematch(match_id)
    return StatusResponse(status="ok")


@app.post("/admin/matches/{match_id}/start", response_model=StatusResponse)
async def admin_start_match(match_id: int) -> StatusResponse:
    await service.start_match(match_id)
    return StatusResponse(status="ok")


@app.post("/admin/matches/{match_id}/force-end", response_model=StatusResponse)
async def admin_force_end_match(match_id: int) -> StatusResponse:
    await service.force_end_match(match_id)
    return StatusResponse(status="ok")


@app.post("/admin/matches/{match_id}/replay", response_model=StatusResponse)
async def admin_replay_match(match_id: int) -> StatusResponse:
    await service.replay_match(match_id)
    await service.broadcast_leaderboard_if_active()
    return StatusResponse(status="ok")


@app.delete("/admin/matches/{match_id}", response_model=StatusResponse)
async def admin_delete_match(match_id: int) -> StatusResponse:
    await service.delete_match(match_id)
    await service.broadcast_leaderboard_if_active()
    return StatusResponse(status="ok")


@app.post("/admin/leaderboard/broadcast", response_model=StatusResponse)
async def admin_broadcast_leaderboard() -> StatusResponse:
    await service.broadcast_leaderboard()
    return StatusResponse(status="ok")


@app.post("/admin/welcome", response_model=StatusResponse)
async def admin_broadcast_welcome() -> StatusResponse:
    await service.broadcast_welcome()
    return StatusResponse(status="ok")


@app.get("/admin/leaderboard", response_model=dict)
def admin_get_leaderboard(session: Session = Depends(get_session)) -> dict:
    teams = session.exec(select(Team).order_by(Team.ranking_points.desc(), Team.id.asc())).all()
    return {
        "teams": [
            {"id": team.id, "name": team.name, "score": str(team.ranking_points)}
            for team in teams
        ]
    }


@app.get("/admin/messages/current", response_model=dict)
def current_message() -> dict:
    return service.last_message


@app.post("/admin/reset-ranking", response_model=MessageResponse)
async def reset_ranking(session: Session = Depends(get_session)) -> MessageResponse:
    teams = session.exec(select(Team)).all()
    for team in teams:
        team.ranking_points = 0
        session.add(team)
    session.commit()
    await service.broadcast_leaderboard_if_active()
    return MessageResponse(status="ok", detail="Ranking points reset")


@app.post("/admin/recalculate-ranking", response_model=StatusResponse)
async def recalculate_ranking() -> StatusResponse:
    await service.recalculate_ranking_points()
    await service.broadcast_leaderboard_if_active()
    return StatusResponse(status="ok")


@app.get("/admin/stream-settings", response_model=StreamSettingsRead)
async def admin_get_stream_settings() -> StreamSettingsRead:
    settings = await service.get_stream_settings()
    return StreamSettingsRead(**settings)


@app.put("/admin/stream-settings", response_model=StreamSettingsRead)
async def admin_update_stream_settings(payload: StreamSettingsUpdate) -> StreamSettingsRead:
    stream_url = payload.stream_url.strip()
    if not stream_url:
        raise HTTPException(status_code=400, detail="stream_url cannot be empty")
    settings = await service.update_stream_settings(
        stream_url=stream_url,
        stream_enabled=payload.stream_enabled,
    )
    return StreamSettingsRead(**settings)


@app.get("/admin/stream-status", response_model=StreamProbeResponse)
async def admin_stream_status() -> StreamProbeResponse:
    status = await service.probe_stream_status()
    return StreamProbeResponse(**status)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=5022, reload=False)
