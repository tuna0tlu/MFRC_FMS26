import asyncio
import random
from dataclasses import dataclass, field
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

from fastapi import HTTPException, WebSocket
from sqlmodel import Session, select

from .db import engine
from .models import AppConfig, Match, Team, RefereeSubmission

MATCH_DURATION_SECONDS = 210
ACTIVE_PHASE_SECONDS = 180
SHIFT_SECONDS = 30
SCORE_CHECK_DELAY_SECONDS = 3
PRESTART_COUNTDOWN_SECONDS = 3
POINT_TYPES = ["FUEL", "CLIMB", "MINOR FAUL", "MAJOR FAUL"]

INVERT_ATTACKER_MAPPING = True
DEFAULT_STREAM_URL = "http://localhost:8889/live/mfrc/"


def format_remaining_time(seconds: int) -> str:
    minutes = max(seconds, 0) // 60
    secs = max(seconds, 0) % 60
    return f"{minutes}:{secs:02d}"


def compute_winner(red_score: int, blue_score: int) -> int:
    if red_score > blue_score:
        return 1
    if blue_score > red_score:
        return 2
    return 0


def compute_rp_delta(winner: int) -> tuple[int, int]:
    if winner == 1:
        return 2, 0
    if winner == 2:
        return 0, 2
    return 1, 1


def empty_breakdown() -> dict[str, dict[str, int]]:
    return {
        "red": {point_type: 0 for point_type in POINT_TYPES},
        "blue": {point_type: 0 for point_type in POINT_TYPES},
    }


def normalize_breakdown(raw: Any) -> dict[str, dict[str, int]]:
    normalized = empty_breakdown()
    if not isinstance(raw, dict):
        return normalized

    for alliance in ("red", "blue"):
        source = raw.get(alliance, {}) if isinstance(raw, dict) else {}
        if not isinstance(source, dict):
            continue
        for point_type in POINT_TYPES:
            value = source.get(point_type, 0)
            try:
                normalized[alliance][point_type] = int(value)
            except (TypeError, ValueError):
                normalized[alliance][point_type] = 0

    return normalized


@dataclass
class MatchRuntime:
    match_id: int
    title: str
    initial_attacker: int
    attacker_alliance: int
    last_non_endgame_attacker: int
    remaining_seconds: int = MATCH_DURATION_SECONDS
    elapsed_seconds: int = 0
    prestart_countdown: int = PRESTART_COUNTDOWN_SECONDS
    score_check_in_progress: bool = False
    stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    task: asyncio.Task | None = None
    fuel_counts: dict[str, int] = field(default_factory=lambda: {"red": 0, "blue": 0})
    referee_counters: dict[str, dict[str, Any]] = field(
        default_factory=lambda: {
            "red": {
                "minor_faul": 0,
                "major_faul": 0,
                "fuel_count": 0,
                "climb_count": 0,
                "climb_selections": [None, None, None],
            },
            "blue": {
                "minor_faul": 0,
                "major_faul": 0,
                "fuel_count": 0,
                "climb_count": 0,
                "climb_selections": [None, None, None],
            },
        }
    )


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, initial_message: dict[str, Any]) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        await websocket.send_json(initial_message)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections)

        disconnected: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.append(websocket)

        if disconnected:
            async with self._lock:
                for websocket in disconnected:
                    self._connections.discard(websocket)


class FMSService:
    def __init__(self) -> None:
        self.connections = ConnectionManager()
        self.last_message: dict[str, Any] = {"page": "welcome", "data": None}

        self._state_lock = asyncio.Lock()
        self._runtime: MatchRuntime | None = None
        self._runtime_token = 0

    async def connect_websocket(self, websocket: WebSocket) -> None:
        await self.connections.connect(websocket, self.last_message)

    async def disconnect_websocket(self, websocket: WebSocket) -> None:
        await self.connections.disconnect(websocket)

    async def _broadcast_message(self, message: dict[str, Any]) -> None:
        self.last_message = message
        await self.connections.broadcast(message)

    @staticmethod
    def _client_attacker_value(attacker_value: int) -> int:
        if attacker_value not in (0, 1):
            return attacker_value
        if INVERT_ATTACKER_MAPPING:
            return 1 - attacker_value
        return attacker_value

    @staticmethod
    def _get_match_or_404(session: Session, match_id: int) -> Match:
        match = session.get(Match, match_id)
        if match is None:
            raise HTTPException(status_code=404, detail=f"Match {match_id} not found")
        return match

    @staticmethod
    def _get_or_create_app_config(session: Session) -> AppConfig:
        config = session.get(AppConfig, 1)
        if config is None:
            config = AppConfig(id=1, stream_url=DEFAULT_STREAM_URL, stream_enabled=True)
            session.add(config)
            session.flush()
        return config

    @staticmethod
    def _match_position_and_total_in_type(session: Session, match: Match) -> tuple[int, int]:
        same_type_matches = session.exec(
            select(Match.id).where(Match.match_type == match.match_type).order_by(Match.id.asc())
        ).all()
        total = len(same_type_matches)
        for index, current_id in enumerate(same_type_matches, start=1):
            if current_id == match.id:
                return index, total
        return int(match.id or 0), total

    @classmethod
    def _match_title(cls, session: Session, match: Match) -> str:
        match_number, total = cls._match_position_and_total_in_type(session, match)
        if total > 0:
            return f"{match.match_type} {match_number} of {total}"
        return f"{match.match_type} {match_number}"

    @staticmethod
    def _ordered_team_data(session: Session, team_ids: list[str]) -> list[dict[str, str]]:
        if not team_ids:
            return []

        result = session.exec(select(Team).where(Team.id.in_(team_ids))).all()
        by_id = {team.id: team for team in result}

        teams: list[dict[str, str]] = []
        for team_id in team_ids:
            team = by_id.get(team_id)
            teams.append({"id": str(team_id), "name": team.name if team else str(team_id)})
        return teams

    @staticmethod
    def _recalculate_ranking_points(session: Session) -> None:
        teams = session.exec(select(Team)).all()
        team_by_id = {team.id: team for team in teams}

        for team in teams:
            team.ranking_points = 0
            session.add(team)

        played_matches = session.exec(select(Match).where(Match.played == True)).all()
        for match in played_matches:
            red_rp, blue_rp = compute_rp_delta(match.winner)
            for team_id in match.red_team_ids:
                team = team_by_id.get(team_id)
                if team is not None:
                    team.ranking_points += red_rp
                    session.add(team)
            for team_id in match.blue_team_ids:
                team = team_by_id.get(team_id)
                if team is not None:
                    team.ranking_points += blue_rp
                    session.add(team)

    @staticmethod
    def _delete_referee_submissions(session: Session, match_id: int) -> None:
        submissions = session.exec(
            select(RefereeSubmission).where(RefereeSubmission.match_id == match_id)
        ).all()
        for submission in submissions:
            session.delete(submission)

    def _build_prematch_message(self, session: Session, match: Match) -> dict[str, Any]:
        return {
            "page": "prematch",
            "data": {
                "title": self._match_title(session, match),
                "redTeams": self._ordered_team_data(session, match.red_team_ids),
                "blueTeams": self._ordered_team_data(session, match.blue_team_ids),
            },
        }

    @staticmethod
    def _build_referee_state(runtime: MatchRuntime) -> dict[str, Any]:
        state: dict[str, Any] = {}
        for alliance in ("red", "blue"):
            counters = runtime.referee_counters.get(alliance, {})
            climb_selections = counters.get("climb_selections", [None, None, None])
            if not isinstance(climb_selections, list) or len(climb_selections) != 3:
                climb_selections = [None, None, None]
            state[alliance] = {
                "minorFaul": int(counters.get("minor_faul", 0)),
                "majorFaul": int(counters.get("major_faul", 0)),
                "fuelCount": int(counters.get("fuel_count", 0)),
                "climbCount": int(counters.get("climb_count", 0)),
                "climbSelections": list(climb_selections),
            }
        return state

    @staticmethod
    def _build_matchbar_data(
        match: Match,
        runtime: MatchRuntime,
        stream_url: str,
        stream_enabled: bool,
    ) -> dict[str, Any]:
        attacker_alliance = FMSService._client_attacker_value(runtime.attacker_alliance)
        prestart_countdown = runtime.prestart_countdown if runtime.prestart_countdown > 0 else None
        return {
            "title": runtime.title,
            "redTeamIDs": [str(team_id) for team_id in match.red_team_ids],
            "blueTeamIDs": [str(team_id) for team_id in match.blue_team_ids],
            "redScore": str(match.red_score),
            "blueScore": str(match.blue_score),
            "remainingTime": format_remaining_time(runtime.remaining_seconds),
            "scoreCheckInProgress": runtime.score_check_in_progress,
            "matchbarVisible": True,
            "attackerAlliance": int(attacker_alliance),
            "preStartCountdown": prestart_countdown,
            "streamUrl": stream_url,
            "streamEnabled": stream_enabled,
            "refereeState": FMSService._build_referee_state(runtime),
        }

    def _build_matchbar_message(self, session: Session, match: Match, runtime: MatchRuntime) -> dict[str, Any]:
        config = self._get_or_create_app_config(session)
        return {
            "page": "matchbar",
            "data": self._build_matchbar_data(
                match=match,
                runtime=runtime,
                stream_url=config.stream_url,
                stream_enabled=config.stream_enabled,
            ),
        }

    def _build_postmatch_message(self, session: Session, match: Match) -> dict[str, Any]:
        breakdown = normalize_breakdown(match.point_breakdown)
        red_points = [str(breakdown["red"][point_type]) for point_type in POINT_TYPES]
        blue_points = [str(breakdown["blue"][point_type]) for point_type in POINT_TYPES]

        return {
            "page": "postmatch",
            "data": {
                "title": self._match_title(session, match),
                "redTeams": self._ordered_team_data(session, match.red_team_ids),
                "blueTeams": self._ordered_team_data(session, match.blue_team_ids),
                "pointTypes": POINT_TYPES,
                "redPoints": red_points,
                "bluePoints": blue_points,
                "redScore": str(match.red_score),
                "blueScore": str(match.blue_score),
                "winner": int(match.winner),
            },
        }

    @staticmethod
    def _calculate_attacker(initial_attacker: int, elapsed_seconds: int) -> int:
        if elapsed_seconds >= ACTIVE_PHASE_SECONDS:
            return 2
        shift_index = elapsed_seconds // SHIFT_SECONDS
        if shift_index % 2 == 0:
            return initial_attacker
        return 1 - initial_attacker

    @staticmethod
    def _compute_shift_number(elapsed_seconds: int) -> int:
        if elapsed_seconds >= ACTIVE_PHASE_SECONDS:
            return 7
        return (elapsed_seconds // SHIFT_SECONDS) + 1

    @staticmethod
    def _resolve_scorekeeper_alliance(runtime: MatchRuntime) -> str:
        attacker_alliance = FMSService._client_attacker_value(runtime.attacker_alliance)
        if attacker_alliance == 0:
            return "red"
        if attacker_alliance == 1:
            return "blue"
        last_attacker = FMSService._client_attacker_value(runtime.last_non_endgame_attacker)
        return "red" if last_attacker == 0 else "blue"

    async def broadcast_welcome(self) -> None:
        async with self._state_lock:
            message = {"page": "welcome", "data": None}
        await self._broadcast_message(message)

    async def broadcast_prematch(self, match_id: int) -> None:
        async with self._state_lock:
            if self._runtime is not None and self._runtime.task is not None and not self._runtime.task.done():
                raise HTTPException(status_code=409, detail="Cannot start prematch while another match is running")

            with Session(engine) as session:
                match = self._get_match_or_404(session, match_id)
                message = self._build_prematch_message(session, match)

        await self._broadcast_message(message)

    async def start_match(self, match_id: int) -> None:
        async with self._state_lock:
            if self._runtime is not None and self._runtime.task is not None and not self._runtime.task.done():
                raise HTTPException(status_code=409, detail="Another match is already running")

            with Session(engine) as session:
                match = self._get_match_or_404(session, match_id)
                match.red_score = 0
                match.blue_score = 0
                match.winner = 0
                match.played = False
                match.point_breakdown = empty_breakdown()
                session.add(match)
                session.commit()
                session.refresh(match)

                initial_attacker = random.randint(0, 1)
                match_title = self._match_title(session, match)
                runtime = MatchRuntime(
                    match_id=match.id,
                    title=match_title,
                    initial_attacker=initial_attacker,
                    attacker_alliance=initial_attacker,
                    last_non_endgame_attacker=initial_attacker,
                )

                self._runtime = runtime
                self._runtime_token += 1
                token = self._runtime_token
                message = self._build_matchbar_message(session, match, runtime)
                runtime.task = asyncio.create_task(self._run_timer(token, match.id))

        await self._broadcast_message(message)

    async def force_end_match(self, match_id: int) -> None:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is None or runtime.match_id != match_id:
                raise HTTPException(status_code=409, detail="This match is not active")
            runtime.stop_event.set()

    async def replay_match(self, match_id: int) -> None:
        async with self._state_lock:
            if self._runtime is not None and self._runtime.task is not None and not self._runtime.task.done():
                raise HTTPException(status_code=409, detail="Cannot replay while another match is running")

            with Session(engine) as session:
                match = self._get_match_or_404(session, match_id)

                match.red_score = 0
                match.blue_score = 0
                match.winner = 0
                match.played = False
                match.point_breakdown = empty_breakdown()
                session.add(match)

                self._delete_referee_submissions(session, match.id)
                session.flush()
                self._recalculate_ranking_points(session)
                session.commit()

    async def delete_match(self, match_id: int) -> None:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is not None and runtime.match_id == match_id and runtime.task is not None and not runtime.task.done():
                raise HTTPException(status_code=409, detail="Cannot delete an active match")

            with Session(engine) as session:
                match = self._get_match_or_404(session, match_id)
                self._delete_referee_submissions(session, match.id)
                session.delete(match)
                session.flush()
                self._recalculate_ranking_points(session)
                session.commit()

    async def recalculate_ranking_points(self) -> None:
        async with self._state_lock:
            with Session(engine) as session:
                self._recalculate_ranking_points(session)
                session.commit()

    async def _run_timer(self, token: int, match_id: int) -> None:
        while True:
            async with self._state_lock:
                runtime = self._runtime
                if runtime is None or token != self._runtime_token:
                    return
                if runtime.stop_event.is_set():
                    break
                if runtime.prestart_countdown > 0:
                    stop_event = runtime.stop_event
                else:
                    if runtime.elapsed_seconds >= MATCH_DURATION_SECONDS:
                        break
                    stop_event = runtime.stop_event

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=1)
                if stop_event.is_set():
                    break
            except asyncio.TimeoutError:
                pass

            shift_changed = False
            async with self._state_lock:
                runtime = self._runtime
                if runtime is None or token != self._runtime_token:
                    return
                if runtime.stop_event.is_set():
                    break

                if runtime.prestart_countdown > 0:
                    runtime.prestart_countdown -= 1
                    with Session(engine) as session:
                        match = self._get_match_or_404(session, match_id)
                        message = self._build_matchbar_message(session, match, runtime)
                else:
                    runtime.elapsed_seconds += 1
                    runtime.remaining_seconds = MATCH_DURATION_SECONDS - runtime.elapsed_seconds

                    new_attacker = self._calculate_attacker(runtime.initial_attacker, runtime.elapsed_seconds)
                    if new_attacker != runtime.attacker_alliance:
                        runtime.attacker_alliance = new_attacker
                        if new_attacker in (0, 1):
                            runtime.last_non_endgame_attacker = new_attacker
                        shift_changed = True

                    with Session(engine) as session:
                        match = self._get_match_or_404(session, match_id)
                        message = self._build_matchbar_message(session, match, runtime)

            if shift_changed:
                await self._broadcast_message(message)
            await self._broadcast_message(message)

        await self._complete_match(token)

    async def _complete_match(self, token: int) -> None:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is None or token != self._runtime_token:
                return

            runtime.score_check_in_progress = True
            with Session(engine) as session:
                match = self._get_match_or_404(session, runtime.match_id)
                checking_message = self._build_matchbar_message(session, match, runtime)

        await self._broadcast_message(checking_message)
        await asyncio.sleep(SCORE_CHECK_DELAY_SECONDS)

        async with self._state_lock:
            runtime = self._runtime
            if runtime is None or token != self._runtime_token:
                return

            with Session(engine) as session:
                match = self._get_match_or_404(session, runtime.match_id)
                match.point_breakdown = normalize_breakdown(match.point_breakdown)
                match.winner = compute_winner(match.red_score, match.blue_score)
                match.played = True
                session.add(match)
                session.flush()
                self._recalculate_ranking_points(session)
                session.commit()
                session.refresh(match)

                postmatch_message = self._build_postmatch_message(session, match)

                self._runtime = None
                self._runtime_token += 1

        await self._broadcast_message(postmatch_message)

    async def apply_referee_submission(
        self,
        alliance: str,
        minor_faul: int,
        major_faul: int,
        fuel_count: int,
        climb_count: int,
        climb_selections: list[str | None] | None = None,
    ) -> dict[str, Any]:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is None:
                raise HTTPException(status_code=409, detail="No active match")
            if runtime.score_check_in_progress:
                raise HTTPException(status_code=409, detail="Score check phase is active")
            if runtime.prestart_countdown > 0:
                raise HTTPException(status_code=409, detail="Match countdown is in progress")

            own = "red" if alliance == "red" else "blue"
            opponent = "blue" if own == "red" else "red"

            shift_number = self._compute_shift_number(runtime.elapsed_seconds)
            previous = runtime.referee_counters[own]
            normalized_climb_selections = climb_selections if climb_selections is not None else previous.get(
                "climb_selections", [None, None, None]
            )
            if len(normalized_climb_selections) != 3:
                normalized_climb_selections = [None, None, None]
            if climb_selections is not None:
                climb_count = sum(1 for level in normalized_climb_selections if level is not None)
            current = {
                "minor_faul": minor_faul,
                "major_faul": major_faul,
                "fuel_count": fuel_count,
                "climb_count": climb_count,
                "climb_selections": list(normalized_climb_selections),
            }
            runtime.referee_counters[own] = current

            delta_minor_faul = current["minor_faul"] - previous["minor_faul"]
            delta_major_faul = current["major_faul"] - previous["major_faul"]
            delta_fuel_count = current["fuel_count"] - previous["fuel_count"]
            delta_climb_count = current["climb_count"] - previous["climb_count"]

            own_delta = (delta_fuel_count * 3) + (delta_climb_count * 10)
            foul_minor_delta = delta_minor_faul * 5
            foul_major_delta = delta_major_faul * 15
            opponent_delta = foul_minor_delta + foul_major_delta

            with Session(engine) as session:
                match = self._get_match_or_404(session, runtime.match_id)
                breakdown = normalize_breakdown(match.point_breakdown)

                if own == "red":
                    match.red_score += own_delta
                    match.blue_score += opponent_delta
                else:
                    match.blue_score += own_delta
                    match.red_score += opponent_delta

                breakdown[own]["FUEL"] += delta_fuel_count * 3
                breakdown[own]["CLIMB"] += delta_climb_count * 10
                breakdown[opponent]["MINOR FAUL"] += foul_minor_delta
                breakdown[opponent]["MAJOR FAUL"] += foul_major_delta

                match.point_breakdown = breakdown

                submission = RefereeSubmission(
                    match_id=runtime.match_id,
                    alliance=alliance,
                    minor_faul=minor_faul,
                    major_faul=major_faul,
                    fuel_count=fuel_count,
                    climb_count=climb_count,
                    shift_number=shift_number,
                )
                session.add(submission)
                session.add(match)
                session.commit()
                session.refresh(match)

                message = self._build_matchbar_message(session, match, runtime)
                response = {
                    "status": "ok",
                    "red_score": match.red_score,
                    "blue_score": match.blue_score,
                    "shift_number": shift_number,
                }

        await self._broadcast_message(message)
        return response

    async def apply_scorekeeper_submission(self, fuel_count: int) -> dict[str, Any]:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is None:
                raise HTTPException(status_code=409, detail="No active match")
            if runtime.score_check_in_progress:
                raise HTTPException(status_code=409, detail="Score check phase is active")
            if runtime.prestart_countdown > 0:
                raise HTTPException(status_code=409, detail="Match countdown is in progress")

            alliance = self._resolve_scorekeeper_alliance(runtime)
            old_count = runtime.fuel_counts[alliance]
            delta = fuel_count - old_count
            points_delta = delta * 3

            with Session(engine) as session:
                match = self._get_match_or_404(session, runtime.match_id)
                breakdown = normalize_breakdown(match.point_breakdown)

                if points_delta != 0:
                    if alliance == "red":
                        match.red_score += points_delta
                    else:
                        match.blue_score += points_delta
                    breakdown[alliance]["FUEL"] += points_delta
                    runtime.fuel_counts[alliance] = fuel_count

                match.point_breakdown = breakdown
                session.add(match)
                session.commit()
                session.refresh(match)

                message = self._build_matchbar_message(session, match, runtime)
                response = {
                    "status": "ok",
                    "alliance": alliance,
                    "fuel_count": fuel_count,
                    "delta": delta,
                    "red_score": match.red_score,
                    "blue_score": match.blue_score,
                }

        await self._broadcast_message(message)
        return response

    async def broadcast_leaderboard(self) -> None:
        with Session(engine) as session:
            teams = session.exec(select(Team).order_by(Team.ranking_points.desc(), Team.id.asc())).all()
            payload = {
                "teams": [
                    {
                        "id": str(team.id),
                        "name": team.name,
                        "score": str(team.ranking_points),
                    }
                    for team in teams
                ]
            }

        await self._broadcast_message({"page": "leaderboard", "data": payload})

    async def get_stream_settings(self) -> dict[str, Any]:
        async with self._state_lock:
            with Session(engine) as session:
                config = self._get_or_create_app_config(session)
                session.commit()
                return {
                    "stream_url": config.stream_url,
                    "stream_enabled": config.stream_enabled,
                }

    async def update_stream_settings(self, stream_url: str, stream_enabled: bool) -> dict[str, Any]:
        async with self._state_lock:
            with Session(engine) as session:
                config = self._get_or_create_app_config(session)
                config.stream_url = stream_url
                config.stream_enabled = stream_enabled
                session.add(config)
                session.commit()

                runtime = self._runtime
                if runtime is not None:
                    match = self._get_match_or_404(session, runtime.match_id)
                    message = self._build_matchbar_message(session, match, runtime)
                else:
                    message = None

        if message is not None and self.last_message.get("page") == "matchbar":
            await self._broadcast_message(message)

        return {
            "stream_url": stream_url,
            "stream_enabled": stream_enabled,
        }

    @staticmethod
    def _probe_stream_url(stream_url: str) -> dict[str, Any]:
        req = urlrequest.Request(stream_url, headers={"User-Agent": "MiniFRC-FMS/1.0"})
        try:
            with urlrequest.urlopen(req, timeout=3) as response:
                status_code = getattr(response, "status", 200)
                return {
                    "status": "ok",
                    "reachable": 200 <= status_code < 400,
                    "http_status": int(status_code),
                    "detail": "reachable" if 200 <= status_code < 400 else "unexpected status",
                }
        except urlerror.HTTPError as exc:
            return {
                "status": "ok",
                "reachable": False,
                "http_status": int(exc.code),
                "detail": str(exc.reason),
            }
        except Exception as exc:
            return {
                "status": "ok",
                "reachable": False,
                "http_status": None,
                "detail": str(exc),
            }

    async def probe_stream_status(self) -> dict[str, Any]:
        settings = await self.get_stream_settings()
        return await asyncio.to_thread(self._probe_stream_url, settings["stream_url"])

    async def broadcast_leaderboard_if_active(self) -> bool:
        async with self._state_lock:
            is_active = self.last_message.get("page") == "leaderboard"

        if not is_active:
            return False

        await self.broadcast_leaderboard()
        return True

    async def shutdown(self) -> None:
        async with self._state_lock:
            runtime = self._runtime
            if runtime is not None:
                runtime.stop_event.set()
                task = runtime.task
            else:
                task = None

        if task is not None:
            try:
                await task
            except Exception:
                pass
