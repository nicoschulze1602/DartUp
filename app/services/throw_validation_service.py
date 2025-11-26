from fastapi import HTTPException, status


class ValidationService:
    """
    Enthält alle Validierungsregeln für Würfe und Spielzustände.
    Kein DB-Zugriff! Rein logische Prüfungen.
    """

    # ---------------------------------------------------------
    # Spielstatus prüfen
    # ---------------------------------------------------------
    @staticmethod
    def ensure_game_active(game):
        if game.status != "running":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Game is not active."
            )

    # ---------------------------------------------------------
    # Prüfen, ob der Spieler an der Reihe ist
    # ---------------------------------------------------------
    @staticmethod
    def ensure_player_turn(game, participant):
        if game.current_turn_user_id != participant.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="It is not your turn."
            )

    # ---------------------------------------------------------
    # Basisvalidierung der Wurfwerte
    # ---------------------------------------------------------
    @staticmethod
    def validate_throw_values(value: int, multiplier: int):
        if value < 0 or value > 20:
            if value != 25:  # Bullseye erlaubt
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Value must be between 0–20 or 25 for bullseye."
                )

        if multiplier not in (1, 2, 3):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Multiplier must be 1, 2 or 3."
            )

        # Bulls dürfen nicht triple sein
        if value == 25 and multiplier == 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bullseye cannot have multiplier 3."
            )

    # ---------------------------------------------------------
    # Double-Out prüfen (nur bei 501 / X01 relevant)
    # ---------------------------------------------------------
    @staticmethod
    def validate_double_out_rule(remaining_after, value, multiplier, checkout_rule):
        if checkout_rule != "double":
            return  # nicht relevant

        # Kein Double Out → ungültig
        if remaining_after == 0 and multiplier != 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Winning throw must be a double (Double-Out rule)."
            )

    # ---------------------------------------------------------
    # Gesamtvalidierung für den ThrowService
    # ---------------------------------------------------------
    @staticmethod
    def validate_throw(
        game,
        participant,
        value: int,
        multiplier: int,
        projected_score: int
    ):
        """
        Führt alle Prüfungen auf einmal durch.
        ThrowService ruft nur diese Methode auf.
        """

        # 1. Spiel aktiv?
        ValidationService.ensure_game_active(game)

        # 2. Spieler dran?
        ValidationService.ensure_player_turn(game, participant)

        # 3. Wurfwerte korrekt?
        ValidationService.validate_throw_values(value, multiplier)

        # 4. Double-Out / Straight-In etc.
        ValidationService.validate_double_out_rule(
            remaining_after=projected_score,
            value=value,
            multiplier=multiplier,
            checkout_rule=game.game_mode.checkout_rule
        )