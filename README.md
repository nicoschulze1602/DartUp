
# 🏹 DartUp – Backend API

**DartUp** ist eine moderne, leichtgewichtige Dart Counter App für Hobby-Spieler – mit Fokus auf Spaß, Spiellogik und umfangreichen Statistiken.

Dieses Backend-Projekt wurde mit [Dart Frog](https://dartfrog.vgv.dev/) aufgebaut und stellt eine RESTful API zur Verfügung, die Spielverläufe, Nutzerprofile und Punktestände verwaltet.

---
## 🚀 Key-Functions

- Nutzerregistrierung & Login (JWT-Auth)
- Spiele mit verschiedenen Modi (z. B. 501, 301)
- Eingabe von Würfen (mit Bust-/Checkout-Logik)
- Legs & Sets Verwaltung
- Spielhistorie & Auswertung
- Erweiterbar für Freunde, Heatmaps, u.v.m.

---
## 🧱 Projektstruktur (vereinfacht)
dartup_backend/
├── routes/           → API-Endpunkte
├── models/           → Datenmodelle (User, Game, Throw)
├── services/         → Spiellogik, Auth, Statistiken
├── data/             → DB-Verbindung & Queries
├── utils/            → Helferfunktionen
└── bin/server.dart   → Einstiegspunkt für den Server

---
## ⚙️ Setup

Voraussetzungen:
- Dart SDK (≥3.0)
- PostgreSQL (optional: Supabase)
- Dart Frog CLI

```bash
# Dart Frog installieren (falls noch nicht vorhanden)
dart pub global activate dart_frog_cli

# Projekt starten
dart_frog dev