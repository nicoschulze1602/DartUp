# 🎯 DartUp Backend

Das **DartUp Backend** ist die serverseitige API für eine moderne Dart-Trainingsapp mit Nutzerprofilen, umfangreichen Statistiken und etlichen Spielmodi.  
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
    git clone https://github.com/DEINUSERNAME/dartup-backend.git
    cd dartup-backend


### 2. Virtuelle Umgebung & Dependencies
    python -m venv venv
    source venv/bin/activate   # macOS/Linux
    venv\Scripts\activate      # Windows

    pip install -r requirements.txt

### 3. Environment Variablen
Erstelle eine .env-Datei im Projekt-Root:
    DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@localhost:5432/dartup
    SECRET_KEY=supergeheimerschluessel123
    ENV=development

### 4. Server starten (lokal)
    uvicorn app.main:app --reload
    -> und öffne dann im Browser: 'http://127.0.0.1:8000/docs'

### 5. Deployment auf Render
Step by step:
	1.	Repo zu GitHub pushen
	2.	Auf render.com einloggen
	3.	„New → Web Service“ → Repository auswählen
	4.	Konfiguration:
                Environment: Python
                Build Command: pip install -r requirements.txt
                Start Command: uvicorn app.main:app --host 0.0.0.0 --port 10000
    5.	PostgreSQL-Service hinzufügen
	6.	Environment-Variablen setzen:
            bash:   DATABASE_URL=<Render-Postgres-URL>
                    SECRET_KEY=<geheimer Key>
                    ENV=production
    7.  Deploy startern
            die API ist anschließend erreichbar unter: 'https://dein-service-name.onrender.com/docs'

# API-Endpoints 🧩 (Auszug)
Route Beschreibung: POST /games/start
Neues Spiel starten: POST /games/{id}/simulate-turn
Einen kompletten Turn simulieren: POST /games/{id}/simulate-game
Komplettes Spiel simulieren: GET /games/{id}
Spielstatus & Scoreboard abrufen: GET /games
Alle Spiele eines 

# 🧠 Beispiel: Spielsimulation (Debug-Ausgabe)
🎮 --- Starte vollständige Simulation für Spiel 42 ---
🎯 Nico wirft 20x3 = 60 Punkte | Score: 501 → 441 (OK)
🎯 Nico wirft 19x3 = 57 Punkte | Score: 441 → 384 (OK)
🎯 Nico wirft 25x2 = 50 Punkte | Score: 384 → 334 (OK)
🔁 Nächster Spieler: John
...
🏆 Nico gewinnt das Spiel nach 14 Turns!
⸻

# 👥 Credits
Projekt: DartUp - Dart Counter 
Backend: Nico Schulze
Framework: FastAPI
Deployment: Render.com
⸻
🧩 To-Do / Ideen
	•	✅ Spielsimulation und Turn-Logik verbessern -> Spiele gegen Computer
	•	⚙️ Frontend-Verknüpfung / Eingabemaske
	•	📊 Erweiterte Statistiken (Checkout %, Best Legs)
	•	🧩 Authentifizierung & User-Sessions
	•	🌍 Leaderboards & Multiplayer-Sync
