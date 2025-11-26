from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.crud.game_crud import (
    create_game,
    get_game_raw,
    finish_game as finish_game_crud,
)
from app.crud.game_participant_crud import (
    get_participant_by_game_and_user,
)
from app.models.user import User
from app.models.game_mode import GameMode


class GameService:

    # ---------------------------------------------------------
    # SPIEL STARTEN
    # ---------------------------------------------------------
    @staticmethod
    async def start_game(
        db: AsyncSession,
        host: User,
        game_mode: GameMode,
        opponent_ids: list[int],
        first_to: int,
        first_shot: int
    ):
        """
        Erstellt ein Game + Participants über CRUD.
        """

        return await create_game(
            db=db,
            host_id=host.id,
            game_mode_id=game_mode.id,
            opponent_ids=opponent_ids,
            first_to=first_to,
            first_shot=first_shot,
            starting_user_id=host.id
        )

    # ---------------------------------------------------------
    # SPIEL LADEN
    # ---------------------------------------------------------
    @staticmethod
    async def load_game(
        db: AsyncSession,
        game_id: int,
        user_id: int
    ):
        """
        Lädt Game + Teilnehmer, prüft, dass der User mitspielt.
        """
        game = await get_game_raw(db, game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )

        participant = await get_participant_by_game_and_user(db, game_id, user_id)
        if not participant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not participant of this game"
            )

        return game, participant

    # ---------------------------------------------------------
    # SPIEL BEENDEN
    # ---------------------------------------------------------
    @staticmethod
    async def finish_game(db: AsyncSession, game_id: int):
        game = await finish_game_crud(db, game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Game not found"
            )
        return game