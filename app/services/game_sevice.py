import random
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game
from app.models.game_participant import GameParticipant
from app.models.game_mode import GameMode
from app.models.user import User
from app.schemas.game_schemas import GameCreate


async def create_game(db: AsyncSession, game_data: GameCreate, current_user: User) -> Game:
    """
    Erstellt ein neues Spiel + automatisch die Participants (Host + Opponents).
    """
    # 1. GameMode laden
    game_mode = await db.get(GameMode, game_data.game_mode_id)
    if not game_mode:
        raise ValueError("GameMode not found")

    # 2. Gegner validieren
    opponents = []
    for opp_id in game_data.opponent_ids:
        opponent = await db.get(User, opp_id)
        if not opponent:
            raise ValueError(f"Opponent with id {opp_id} not found")
        if opponent.id == current_user.id:
            raise ValueError("Host cannot be their own opponent")
        opponents.append(opponent)

    # 3. Game erstellen
    game = Game(
        game_mode_id=game_mode.id,
        user_id=current_user.id,  # Host
        status="running",
        start_time=datetime.now(UTC),
        first_to=game_data.first_to
    )
    db.add(game)
    await db.flush()  # sorgt dafür, dass game.id sofort verfügbar ist

    # 4. Participants erstellen (Host + Opponents)
    participants = []

    host_participant = GameParticipant(
        game_id=game.id,
        user_id=current_user.id,
        starting_score=game_mode.starting_score,
        current_score=game_mode.starting_score,
    )
    participants.append(host_participant)

    for opp in opponents:
        participants.append(
            GameParticipant(
                game_id=game.id,
                user_id=opp.id,
                starting_score=game_mode.starting_score,
                current_score=game_mode.starting_score,
            )
        )

    db.add_all(participants)

    # 5. First-Shot bestimmen
    if game_data.first_shot == "host":
        game.current_turn_user_id = current_user.id
    elif game_data.first_shot == "random":
        chosen = random.choice([p.user_id for p in participants])
        game.current_turn_user_id = chosen
    else:
        # Default = Host
        game.current_turn_user_id = current_user.id

    await db.commit()
    await db.refresh(game)

    return game