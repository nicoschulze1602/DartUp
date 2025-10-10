from typing import List, Optional
from datetime import datetime, UTC

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.game_mode import GameMode
from app.schemas.game_schemas import GameCreate, GameOut, ParticipantInGame
from app.services.game_statistics_service import GameStatisticsService
from app.services.checkout_service import get_checkout_suggestion


# ----------------------------------------------------------
# 🆕 GAME ERSTELLEN
# ----------------------------------------------------------
async def create_game(db: AsyncSession, game_data: GameCreate, current_user: User) -> Game:
    """
    Neues Spiel in der DB anlegen + alle Participants erzeugen.
    """
    result = await db.execute(select(GameMode).where(GameMode.id == game_data.game_mode_id))
    mode: Optional[GameMode] = result.scalars().first()
    if not mode:
        raise ValueError("Invalid game_mode_id")

    # Spiel-Objekt anlegen
    new_game: Game = Game(
        user_id=current_user.id,
        game_mode_id=game_data.game_mode_id,
        status="ongoing",
    )
    db.add(new_game)
    await db.flush()  # damit new_game.id schon existiert

    # Participants (Host + Gegner)
    participants: list[GameParticipant] = [
        GameParticipant(
            game_id=new_game.id,
            user_id=current_user.id,
            starting_score=mode.starting_score,
            current_score=mode.starting_score,
        )
    ]

    for opp_id in game_data.opponent_ids:
        participants.append(
            GameParticipant(
                game_id=new_game.id,
                user_id=opp_id,
                starting_score=mode.starting_score,
                current_score=mode.starting_score,
            )
        )

    db.add_all(participants)
    await db.commit()

    # Game inkl. Participants & User laden
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user)
        )
        .where(Game.id == new_game.id)
    )
    return result.scalars().first()


# ----------------------------------------------------------
# 🧩 EINZELNES SPIEL LADEN
# ----------------------------------------------------------
async def get_game(db: AsyncSession, game_id: int) -> Optional[GameOut]:
    """
    Hole ein einzelnes Spiel per ID (inkl. Teilnehmer + Statistiken).
    Gibt ein GameOut-Schema zurück.
    """
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.throws),
            selectinload(Game.game_mode),
        )
        .where(Game.id == game_id)
    )
    game: Optional[Game] = result.scalars().first()
    if not game:
        return None

    # Teilnehmer in Schema-Objekte umwandeln
    participants_out: list[ParticipantInGame] = []
    for p in game.participants:
        stats = GameStatisticsService.calculate_live_stats(p, p.throws or [])
        participants_out.append(
            ParticipantInGame(
                participant_id=p.id,
                user_id=p.user.id,
                username=p.user.username,
                current_score=p.current_score,
                new_score=p.current_score,
                checkout_suggestion=(
                    get_checkout_suggestion(p.current_score)
                    if p.current_score <= 170
                    else None
                ),
                **stats,
            )
        )

    # Rückgabe als GameOut
    return GameOut(
        id=game.id,
        status=game.status,
        start_time=game.start_time,
        end_time=game.end_time,
        first_shot=game.first_shot,
        first_to=game.first_to,
        current_turn_user_id=game.current_turn_user_id,
        participants=participants_out,
    )


# ----------------------------------------------------------
# 🎯 ALLE SPIELE EINES USERS LADEN
# ----------------------------------------------------------
async def get_games_by_user(db: AsyncSession, user_id: int) -> List[GameOut]:
    """
    Holt alle Spiele eines Users inkl. Teilnehmerdaten und Würfen.
    """
    result = await db.execute(
        select(Game)
        .options(
            selectinload(Game.participants).selectinload(GameParticipant.user),
            selectinload(Game.participants).selectinload(GameParticipant.throws),
        )
        .where(Game.user_id == user_id)
    )
    games: list[Game] = result.scalars().unique().all()

    game_out_list: list[GameOut] = []

    for game in games:
        participants_out: list[ParticipantInGame] = []
        for p in game.participants:
            stats = GameStatisticsService.calculate_live_stats(p, p.throws or [])
            participants_out.append(
                ParticipantInGame(
                    participant_id=p.id,
                    user_id=p.user.id,
                    username=p.user.username,
                    current_score=p.current_score,
                    new_score=p.current_score,
                    checkout_suggestion=(
                        get_checkout_suggestion(p.current_score)
                        if p.current_score <= 170
                        else None
                    ),
                    **stats,
                )
            )

        game_out_list.append(
            GameOut(
                id=game.id,
                status=game.status,
                start_time=game.start_time,
                end_time=game.end_time,
                first_shot=game.first_shot,
                first_to=game.first_to,
                current_turn_user_id=game.current_turn_user_id,
                participants=participants_out,
            )
        )

    return game_out_list


# ----------------------------------------------------------
# 🏁 SPIEL BEENDET MARKIEREN
# ----------------------------------------------------------
async def finish_game(db: AsyncSession, game_id: int) -> Optional[Game]:
    """
    Beende ein Spiel (setzt end_time + Status).
    Gibt das aktualisierte Game-Objekt zurück.
    """
    result = await db.execute(select(Game).where(Game.id == game_id))
    game: Optional[Game] = result.scalars().first()
    if not game:
        return None

    game.end_time = datetime.now(UTC)
    game.status = "finished"

    await db.commit()
    await db.refresh(game)
    return game