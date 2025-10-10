from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.user import User
from app.models.game_mode import GameMode
from datetime import datetime, UTC
import random
from fastapi import HTTPException


async def start_game(
    db: AsyncSession,
    host: User,
    game_mode: GameMode,
    opponent_ids: list[int],
    first_to: int,
    first_shot: str
) -> Game:
    """
    Erstellt ein neues Spiel mit Host + Opponents + initialen Participants.
    Vollständig asynchron & Lazy-Load-sicher.
    """

    # -------------------------
    # 0️⃣ Opponenten bereinigen & prüfen
    # -------------------------
    # Entferne Duplikate und entferne evtl. Host-id aus Gegner-Liste
    unique_opponents: list[int] = []
    for oid in (opponent_ids or []):
        if oid not in unique_opponents and oid != host.id:
            unique_opponents.append(oid)

    # Prüfe, ob die angegebenen Opponent-User tatsächlich existieren
    if unique_opponents:
        result = await db.execute(select(User.id).where(User.id.in_(unique_opponents)))
        existing = {row[0] for row in result.all()}
        missing = [uid for uid in unique_opponents if uid not in existing]
        if missing:
            raise HTTPException(status_code=404, detail=f"Opponent user(s) not found: {missing}")

    # Zusammensetzen aller beteiligten User-IDs (Host zuerst)
    user_ids = [host.id] + unique_opponents

    # -------------------------
    # 1️⃣ Wer fängt an? (bestimme startende User-ID)
    # -------------------------
    if first_shot == "host":
        starting_user_id = host.id
    elif first_shot == "opponent" and unique_opponents:
        starting_user_id = unique_opponents[0]
    elif first_shot == "random":
        starting_user_id = random.choice(user_ids)
    else:
        starting_user_id = host.id

    # -------------------------
    # 2️⃣ Neues Spiel anlegen (current_turn_user_id = startende USER-ID)
    # -------------------------
    new_game = Game(
        game_mode_id=game_mode.id,
        user_id=host.id,
        start_time=datetime.now(UTC),
        status="ongoing",
        first_to=first_to,
        first_shot=first_shot,
        current_turn_user_id=starting_user_id,  # wichtig: USER-ID, nicht Participant-ID
    )
    db.add(new_game)
    await db.flush()  # Game.id verfügbar machen

    # -------------------------
    # 3️⃣ Teilnehmer (Host + Opponents) erstellen
    # -------------------------
    participants = [
        GameParticipant(
            game_id=new_game.id,
            user_id=uid,
            starting_score=game_mode.starting_score,
            current_score=game_mode.starting_score,
        )
        for uid in user_ids
    ]

    db.add_all(participants)
    await db.commit()

    # -------------------------
    # 4️⃣ Spiel vollständig laden (inkl. Teilnehmer + User)
    # -------------------------
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user)
        )
        .where(Game.id == new_game.id)
    )
    return result.scalars().first()