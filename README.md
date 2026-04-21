# MFRC FMS26

Mini FRC yarışması için geliştirilen **Field Management System (FMS)** projesi.

Bu repo iki ana parçadan oluşur:

- `backend/`: FastAPI + SQLModel + SQLite tabanlı maç yönetim servisi
- `frontend/`: Nuxt 3 tabanlı ekranlar (izleyici, admin, referee, driver, leaderboard)

---

## 1) Ne İşe Yarar?

Sistem bir maçın tüm akışını yönetir:

- Takım ve maç oluşturma
- Prematch -> Match -> Score Check -> Postmatch akışı
- WebSocket ile tüm ekranlara anlık yayın
- Hakem/scorekeeper girişlerinden skor güncelleme
- Ranking Points (RP) hesaplama ve leaderboard
- Maç tekrarı/silme ile RP düzeltme
- Match video yayını URL yönetimi (admin üzerinden)

> Donanım bağlantısı yoktur (robot/field kontrol yok). Tüm puanlar manuel girilir.

---

## 2) Teknoloji

- **Backend**: Python, FastAPI, SQLModel, SQLite
- **Frontend**: Nuxt 3 (Vue 3), TailwindCSS, Pinia
- **Realtime**: WebSocket (`/audis/ws`)
- **Default backend port**: `5022`
- **Default frontend port**: `3000`

---

## 3) Dizin Yapısı

```text
MFRC_FMS26/
├─ backend/
│  ├─ main.py           # API + WS endpoint tanımları
│  ├─ service.py        # Maç state machine + broadcast + scoring logic
│  ├─ models.py         # SQLModel tabloları
│  ├─ schemas.py        # Request/response şemaları
│  ├─ db.py             # DB engine + session
│  └─ requirements.txt
├─ frontend/
│  ├─ pages/            # Ekranlar (admin, match, referee, driver, ...)
│  ├─ layouts/
│  ├─ stores/
│  ├─ composables/
│  ├─ types.ts
│  ├─ nuxt.config.ts
│  └─ package.json
└─ fms.db               # SQLite dosyası (default)
```

---

## 4) Kurulum ve Çalıştırma

## 4.1 Backend

```bash
cd /Users/tunaotlu/Desktop/MFRC_FMS26
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 5022
```

Health kontrol:

```bash
curl http://localhost:5022/health
```

---

## 4.2 Frontend

```bash
cd /Users/tunaotlu/Desktop/MFRC_FMS26/frontend
npm install
npm run dev
```

LAN’dan erişim için:

```bash
npm run dev:lan
```

---

## 4.3 Production (Frontend)

```bash
cd /Users/tunaotlu/Desktop/MFRC_FMS26/frontend
npm run build
npm run start
```

---

## 5) WebSocket Yayın Formatı

Endpoint:

- `ws://<backend-ip>:5022/audis/ws`

Mesaj formatı:

```json
{
  "page": "welcome|prematch|matchbar|postmatch|leaderboard",
  "data": {}
}
```

### `page = "welcome"`

```json
{ "page": "welcome", "data": null }
```

### `page = "prematch"`

```json
{
  "page": "prematch",
  "data": {
    "title": "Qualification 1 of 20",
    "redTeams": [{ "id": "3243", "name": "..." }],
    "blueTeams": [{ "id": "7742", "name": "..." }]
  }
}
```

### `page = "matchbar"`

```json
{
  "page": "matchbar",
  "data": {
    "title": "Qualification 1 of 20",
    "redTeamIDs": ["3243", "7382"],
    "blueTeamIDs": ["7742", "9483"],
    "redScore": "12",
    "blueScore": "8",
    "remainingTime": "3:10",
    "scoreCheckInProgress": false,
    "matchbarVisible": true,
    "attackerAlliance": 0,
    "preStartCountdown": null,
    "streamUrl": "http://localhost:8889/live/mfrc/",
    "streamEnabled": true,
    "refereeState": {
      "red": {
        "minorFaul": 0,
        "majorFaul": 1,
        "fuelCount": 6,
        "climbCount": 2,
        "climbSelections": ["L1", "L3", null]
      },
      "blue": {
        "minorFaul": 0,
        "majorFaul": 0,
        "fuelCount": 5,
        "climbCount": 1,
        "climbSelections": [null, "L2", null]
      }
    }
  }
}
```

### `page = "postmatch"`

```json
{
  "page": "postmatch",
  "data": {
    "title": "Qualification 1 of 20",
    "redTeams": [{ "id": "3243", "name": "..." }],
    "blueTeams": [{ "id": "7742", "name": "..." }],
    "pointTypes": ["FUEL", "CLIMB", "MINOR FAUL", "MAJOR FAUL"],
    "redPoints": ["30", "20", "5", "0"],
    "bluePoints": ["24", "10", "0", "15"],
    "redScore": "55",
    "blueScore": "49",
    "winner": 1
  }
}
```

### `page = "leaderboard"`

```json
{
  "page": "leaderboard",
  "data": {
    "teams": [
      { "id": "3243", "name": "A Team", "score": "12" }
    ]
  }
}
```

---

## 6) Maç Zamanlama ve Shift Kuralı

Backend `backend/service.py` üzerinden yönetilir.

- Toplam maç süresi: **210 sn** (`3:30`)
- Aktif saldırı fazı: **180 sn**
- Shift süresi: **30 sn**
- Toplam shift: **6**
- Son **30 sn**: `ENDGAME` (`attackerAlliance = 2`)
- Maç öncesi countdown: **3 sn**
- Maç sonu score check bekleme: **3 sn**

Shift dizisi:

- İlk saldıran ittifak rastgele (red/blue)
- Her 30 saniyede bir ittifak değişir
- Son 30 saniyede iki ittifak da aktif (`2`)

---

## 7) Skorlama Kuralları

Backendte kullanılan puanlar:

- `FUEL`: +3 (kendi ittifaka)
- `CLIMB`: +10 (kendi ittifaka)
- `MINOR FAUL`: +5 (rakibe)
- `MAJOR FAUL`: +15 (rakibe)

Kazanan ve RP:

- `winner = 1` -> kırmızı kazanır -> RP: red `+2`, blue `+0`
- `winner = 2` -> mavi kazanır -> RP: red `+0`, blue `+2`
- `winner = 0` -> beraberlik -> RP: iki taraf `+1`

---

## 8) HTTP API

Base URL:

- `http://localhost:5022`

### 8.1 Game Endpoints

- `POST /game/referee`
- `POST /game/scorekeeper?fuel=<int>`

Referee body örneği:

```json
{
  "alliance": "red",
  "minorFaul": 1,
  "majorFaul": 0,
  "seasonSpecificValues": [5, 2],
  "climbSelections": ["L1", "L2", null]
}
```

### 8.2 Admin Endpoints

- `POST /admin/teams`
- `GET /admin/teams`
- `PUT /admin/teams/{team_id}`
- `DELETE /admin/teams/{team_id}`
- `POST /admin/matches`
- `GET /admin/matches`
- `POST /admin/matches/{match_id}/prematch`
- `POST /admin/matches/{match_id}/start`
- `POST /admin/matches/{match_id}/force-end`
- `POST /admin/matches/{match_id}/replay`
- `DELETE /admin/matches/{match_id}`
- `POST /admin/leaderboard/broadcast`
- `GET /admin/leaderboard`
- `POST /admin/welcome`
- `GET /admin/messages/current`
- `POST /admin/reset-ranking`
- `POST /admin/recalculate-ranking`
- `GET /admin/stream-settings`
- `PUT /admin/stream-settings`
- `GET /admin/stream-status`

---

## 9) Frontend Route’lar

Ana ekranlar:

- `/` -> welcome
- `/prematch`
- `/match`
- `/winner-load`
- `/postmatch`
- `/leaderboard`
- `/admin`

Hakem ekranları:

- `/refereered`
- `/refereeblue`

Driver ekranları:

- `/driverred`
- `/driverblue`

Scorekeeper:

- `/scorekeeper`

---

## 10) Veritabanı

Tablolar (`backend/models.py`):

- `Team`
  - `id`, `name`, `ranking_points`
- `Match`
  - `id`, `match_type`, `red_team_ids(JSON)`, `blue_team_ids(JSON)`, `red_score`, `blue_score`, `winner`, `played`, `point_breakdown(JSON)`
- `RefereeSubmission`
  - `match_id`, `alliance`, `minor_faul`, `major_faul`, `fuel_count(legacy column: mercan_count)`, `climb_count`, `shift_number`, `created_at`
- `AppConfig`
  - `stream_url`, `stream_enabled`

---

## 11) OBS / Yayın Entegrasyonu

Match ekranı `streamUrl` değerini iframe ile açar.

Varsayılan:

- `http://localhost:8889/live/mfrc/`

Admin panelden:

- Yayın URL güncellenebilir
- Yayın aç/kapat yapılabilir
- URL erişim kontrolü (`/admin/stream-status`) alınabilir

---

## 12) Çoklu Hakem Canlı Senkronizasyonu

Aynı alliance için birden fazla hakem ekranı açıksa:

- Referee girişleri backend’e gönderilir
- Backend `matchbar.refereeState` içine canlı sayaçları ekler
- Tüm referee ekranları WebSocket üzerinden aynı state’i anlık alır

Bu sayede aynı renkteki tabletler eşzamanlı çalışır.

---

## 13) Sık Görülen Hatalar

### `#internal/nuxt/paths` veya `#app-manifest` hatası

Sebep:

- Yanlış dosya (`.nuxt/dist/server/server.mjs`) elle çalıştırılıyor
- veya eski cache

Çözüm:

```bash
cd frontend
rm -rf .nuxt .output node_modules/.vite
npm install
npm run dev
```

> Dev için `npm run dev` / `npm run dev:lan`, production için `npm run build && npm run start` kullanın.

### Port dolu

Nuxt bazen 3000 doluysa 3001/3002’ye çıkar.

---

## 14) Geliştirme Notları

- CORS backendte tüm originlere açık (`allow_origins=["*"]`)
- Aynı anda tek aktif maç kuralı backend lock ile korunur
- Yeni WS bağlantısı geldiğinde son yayın (`last_message`) anında gönderilir
- Bu repo lokal ağ yarışma kurulumu için optimize edilmiştir

---

## 15) Lisans

Bu proje kök dizindeki `LICENSE` dosyasına tabidir.

