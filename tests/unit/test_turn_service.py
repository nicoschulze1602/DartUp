import pytest
from app.services.turn_service import TurnService
from app.models.throw import Throw

# Hilfsfunktion: erzeugt ein Fake-Throw-Objekt schnell
def make_throw(turn, number):
    class Dummy:
        turn_number = turn
        throw_number_in_turn = number
    return Dummy()

# ---------------------------------------------------------
# Test: erster Wurf → immer (1,1,1)
# ---------------------------------------------------------
def test_first_throw_position():
    result = TurnService.get_throw_position([])
    assert result == (1, 1, 1)

# ---------------------------------------------------------
# Test: zweiter Dart im selben Turn
# ---------------------------------------------------------
def test_second_throw_same_turn():
    prev = [make_throw(1, 1)]
    result = TurnService.get_throw_position(prev)
    assert result == (1, 2, 2)

# ---------------------------------------------------------
# Test: dritter Dart im selben Turn
# ---------------------------------------------------------
def test_third_throw_same_turn():
    prev = [make_throw(1, 1), make_throw(1, 2)]
    result = TurnService.get_throw_position(prev)
    assert result == (1, 3, 3)

# ---------------------------------------------------------
# Test: neuer Turn beginnt nach dem 3. Dart
# ---------------------------------------------------------
def test_new_turn_after_three_darts():
    prev = [make_throw(1, 1), make_throw(1, 2), make_throw(1, 3)]
    result = TurnService.get_throw_position(prev)
    assert result == (2, 1, 4)