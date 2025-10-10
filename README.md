# 🎯 DartUp Backend

Das **DartUp Backend** ist die serverseitige API für eine moderne Dart-Trainings- und Statistik-App.  
Es wurde mit **FastAPI** und **SQLAlchemy (Async)** entwickelt und simuliert vollständige Dartspiele (z. B. *501 Double Out*) inklusive Spiel-, Wurf- und Statistik-Logik.

---

## 🚀 Features

- **Spielmodi & Simulation**
  - Vollständige Spielsimulation (Turn-basiert, Double-Out-Regeln)
  - Wurf-Validierung & Turnwechsel-Logik
  - Realistische Checkout-Empfehlungen

- **Statistiken**
  - Laufende Spiel- und Wurfstatistiken pro Spieler
  - Automatische Berechnung von 3-Dart-Averages, Highscores usw.

- **Persistenz**
  - PostgreSQL-Datenbank mit SQLAlchemy (Async)
  - Datenbankmigrationen via Alembic (optional)

- **API**
  - OpenAPI/Swagger-Dokumentation automatisch unter `/docs`
  - JSON-Schemas für Games, Participants, Throws etc.

---

## 🧱 Technologie-Stack

| Komponente | Technologie |
|-------------|--------------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) |
| Datenbank | PostgreSQL (lokal oder Render Cloud) |
| ORM | SQLAlchemy (Async) |
| Server | Uvicorn |
| Deployment | Render.com |
| Sprache | Python 3.11+ |

---

## ⚙️ Lokale Entwicklung

### 1. Projekt klonen

```bash
git clone https://github.com/DEINUSERNAME/dartup-backend.git
cd dartup-backend
