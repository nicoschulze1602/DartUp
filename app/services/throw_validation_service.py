class ValidationService:
    """
    Enthält Validierungen für Dart-Würfe und andere Spielregeln.
    """
    @staticmethod
    def validate_throw(value: int, multiplier: int) -> None:
        """
        Prüft, ob ein Wurf gültig ist.
        - value muss 1–20 oder 25 (Bull) sein
        - multiplier muss 1, 2 oder 3 sein
        - Bull (25) darf nur Single oder Double sein
        """
        if value not in list(range(1, 21)) + [25]:
            raise ValueError("Wurf muss zwischen 1–20 oder 25 (Bull) liegen")

        if multiplier not in [1, 2, 3]:
            raise ValueError("Multiplier muss 1 (Single), 2 (Double) oder 3 (Triple) sein")

        if value == 25 and multiplier == 3:
            raise ValueError("Bull (25) darf kein Triple haben")