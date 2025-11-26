import pytest
from app.services.game_engine import GameEngine

class MockGameMode:
    """Simuliert das GameMode-Modell für die Regeln."""

    def __init__(self, scoring_type, checkout_rule=None):
        self.scoring_type = scoring_type
        self.checkout_rule = checkout_rule  # z.B. "double" für 501


class MockThrow:
    """Simuliert einen Wurf (Throw-Modell)."""

    def __init__(self, value, multiplier):
        self.value = value  # z.B. 20
        self.multiplier = multiplier  # z.B. 3 (Triple)


class MockGameParticipant:
    """Simuliert einen Teilnehmer (GameParticipant-Modell)."""

    def __init__(self, initial_score):
        self.current_score = initial_score


class MockGame:
    """Simuliert das Game-Modell."""

    def __init__(self, game_mode):
        self.game_mode = game_mode


# --------------------------------------------------------------------------
# 2. Pytest Fixtures
# Fixtures sind Funktionen, die Testdaten für mehrere Tests bereitstellen.
# --------------------------------------------------------------------------

@pytest.fixture
def participant_501():
    """Teilnehmer-Fixture für 501 (Subtract Mode) mit Double-Out."""
    return MockGameParticipant(initial_score=501)


@pytest.fixture
def participant_cricket():
    """Teilnehmer-Fixture für Cricket (Add Mode)."""
    return MockGameParticipant(initial_score=0)


@pytest.fixture
def game_501_double_out():
    """Spiel-Fixture: 501 mit Double-Out-Regel."""
    mode = MockGameMode(scoring_type="subtract", checkout_rule="double")
    return MockGame(game_mode=mode)


@pytest.fixture
def game_cricket():
    """Spiel-Fixture: Cricket (Add Mode)."""
    mode = MockGameMode(scoring_type="add")
    return MockGame(game_mode=mode)


# --------------------------------------------------------------------------
# 3. Unit Tests für GameEngine.apply_throw (Subtract Mode)
# --------------------------------------------------------------------------

def test_subtract_mode_ok_hit(game_501_double_out, participant_501):
    """Testet einen normalen Treffer im 501-Modus."""
    # Start: 501, Wurf: Triple 20 (60 Punkte)
    throw = MockThrow(value=20, multiplier=3)

    result = GameEngine.apply_throw(game_501_double_out, participant_501, throw)

    # Erwartungen prüfen
    assert result["status"] == "OK"
    assert result["remaining"] == 441  # 501 - 60 = 441
    assert participant_501.current_score == 441  # Prüfen, ob der Score im Objekt aktualisiert wurde


def test_subtract_mode_win_double_out(game_501_double_out):
    """Testet den korrekten Gewinnwurf (Ende auf 0 mit Double)."""
    participant = MockGameParticipant(initial_score=40)
    # Wurf: Double 20 (40 Punkte)
    throw = MockThrow(value=20, multiplier=2)

    result = GameEngine.apply_throw(game_501_double_out, participant, throw)

    # Erwartungen prüfen
    assert result["status"] == "WIN"
    assert result["remaining"] == 0
    assert participant.current_score == 0


def test_subtract_mode_bust_below_zero(game_501_double_out):
    """Testet den Bust, wenn der Score unter Null fällt."""
    participant = MockGameParticipant(initial_score=50)
    # Wurf: Triple 20 (60 Punkte) -> 50 - 60 = -10 (Bust)
    throw = MockThrow(value=20, multiplier=3)

    original_score = participant.current_score
    result = GameEngine.apply_throw(game_501_double_out, participant, throw)

    # Erwartungen prüfen: Status BUST, Score bleibt beim ursprünglichen Wert
    assert result["status"] == "BUST"
    assert result["remaining"] == original_score
    assert participant.current_score == original_score


def test_subtract_mode_bust_score_one(game_501_double_out):
    """Testet den Bust, wenn der resultierende Score 1 wäre."""
    participant = MockGameParticipant(initial_score=21)
    # Wurf: Single 20 (20 Punkte) -> 21 - 20 = 1 (Bust)
    throw = MockThrow(value=20, multiplier=1)

    original_score = participant.current_score
    result = GameEngine.apply_throw(game_501_double_out, participant, throw)

    # Erwartungen prüfen: Status BUST, Score bleibt beim ursprünglichen Wert
    assert result["status"] == "BUST"
    assert result["remaining"] == original_score
    assert participant.current_score == original_score


def test_subtract_mode_bust_win_on_single(game_501_double_out):
    """Testet den Bust, wenn exakt 0 erreicht wird, aber nicht mit Double."""
    participant = MockGameParticipant(initial_score=20)
    # Wurf: Single 20 (20 Punkte) -> 20 - 20 = 0, aber kein Double! (Bust)
    throw = MockThrow(value=20, multiplier=1)

    original_score = participant.current_score
    result = GameEngine.apply_throw(game_501_double_out, participant, throw)

    # Erwartungen prüfen: Status BUST, Score bleibt beim ursprünglichen Wert
    assert result["status"] == "BUST"
    assert result["remaining"] == original_score
    assert participant.current_score == original_score


# --------------------------------------------------------------------------
# 4. Unit Tests für GameEngine.apply_throw (Add Mode)
# --------------------------------------------------------------------------

def test_add_mode_initial_hit(game_cricket, participant_cricket):
    """Testet den ersten Wurf im Add-Modus (z.B. Cricket)."""
    # Start: 0, Wurf: Triple 19 (57 Punkte)
    throw = MockThrow(value=19, multiplier=3)

    result = GameEngine.apply_throw(game_cricket, participant_cricket, throw)

    # Erwartungen prüfen
    assert result["status"] == "OK"
    assert result["remaining"] == 57
    assert participant_cricket.current_score == 57


def test_add_mode_subsequent_hit(game_cricket):
    """Testet einen Folgewurf im Add-Modus."""
    participant = MockGameParticipant(initial_score=100)
    # Wurf: Double Bull (50 Punkte) ->