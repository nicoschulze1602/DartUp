from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import throw_crud, game_crud, game_participant_crud
from app.services.turn_service import TurnService
from app.services.game_engine import GameEngine


class ThrowService:
    """
    Verwaltet den Ablauf eines einzelnen Wurfs.
    (Keine DB-Objekte direkt anfassen, nur CRUD nutzen.)
    """

    @staticmethod
    async def process_throw(
        db: AsyncSession,
        game_id: int,
        participant_id: int,
        value: int,
        multiplier: int
    ):
        """
        Führt einen neuen Wurf aus:
        - lädt game und participant
        - ermittelt die Turn-Position
        - erstellt den Throw
        - berechnet Spiellogik (Engine)
        - aktualisiert Score & Status
        - entscheidet Spielerwechsel
        """

        # 1️⃣ Spiel + Teilnehmer laden
        game = await game_crud.get_game(db, game_id)
        if not game:
            raise ValueError("Game not found")

        participant = await game_participant_crud.get_participant(db, participant_id)
        if not participant:
            raise ValueError("Participant not found")

        # 2️⃣ Bisherige Würfe laden
        previous_throws = await throw_crud.get_throws_for_participant(
            db, game_id, participant_id
        )

        # 3️⃣ Position im Turn berechnen
        turn_info = TurnService.get_throw_position(previous_throws)

        # turn_info enthält:
        # {
        #   "turn_number": int,
        #   "throw_number": int (1..3),
        #   "darts_thrown": int
        # }

        # 4️⃣ Throw speichern
        new_throw = await throw_crud.create_throw(
            db=db,
            game_id=game_id,
            participant_id=participant_id,
            value=value,
            multiplier=multiplier,
            turn_number=turn_info["turn_number"],
            throw_number_in_turn=turn_info["throw_number"],
            darts_thrown=turn_info["darts_thrown"],
            timestamp=datetime.now(UTC)
        )

        # 5️⃣ Spiellogik anwenden
        engine_result = GameEngine.apply_throw(
            game=game,
            participant=participant,
            throw=new_throw
        )
        # engine_result = { "status": "...", "remaining": ... }

        # 6️⃣ Bewertung des Turns → Spielerwechsel?
        next_player_name = TurnService.handle_player_switch(
            game=game,
            participant=participant,
            throw_result=engine_result["status"],
            throw_number_in_turn=turn_info["throw_number"]
        )

        # 7️⃣ Game speichern
        await game_crud.update_game(db, game)

        # 8️⃣ API-Response bauen
        return {
            "throw": new_throw,
            "player": participant.user.username,
            "remaining": participant.current_score,
            "status": engine_result["status"],
            "throw_in_turn": f"{turn_info['throw_number']}/3",
            "darts_thrown": turn_info["darts_thrown"],
            "next": next_player_name
        }