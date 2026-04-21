# Mini FRC FMS Backend

## Run

From repository root:

```bash
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 5022
```

## Key Routes

- `WS /audis/ws`
- `POST /game/referee`
- `POST /game/scorekeeper?fuel=<int>`
- `POST /admin/teams`
- `GET /admin/teams`
- `PUT /admin/teams/{team_id}`
- `DELETE /admin/teams/{team_id}`
- `POST /admin/matches`
- `GET /admin/matches`
- `POST /admin/matches/{match_id}/prematch`
- `POST /admin/matches/{match_id}/start`
- `POST /admin/matches/{match_id}/force-end`
- `POST /admin/leaderboard/broadcast`
- `POST /admin/welcome`
