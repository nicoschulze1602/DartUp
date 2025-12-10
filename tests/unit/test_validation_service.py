import pytest
from fastapi import HTTPException

from app.services.throw_validation_service import ValidationService


# ------------------------------------------
# VALUE + MULTIPLIER VALIDATION
# ------------------------------------------
def test_validate_throw_values_valid():
    # 20 single
    assert ValidationService.validate_throw_values(20, 1) is None

    # Bull (25) double
    assert ValidationService.validate_throw_values(25, 2) is None


def test_validate_throw_values_invalid_negative():
    with pytest.raises(HTTPException):
        ValidationService.validate_throw_values(-5, 1)


def test_validate_throw_values_too_high():
    with pytest.raises(HTTPException):
        ValidationService.validate_throw_values(210, 1)


def test_validate_throw_values_invalid_multiplier_zero():
    with pytest.raises(HTTPException):
        ValidationService.validate_throw_values(20, 0)


def test_validate_throw_values_invalid_multiplier_high():
    with pytest.raises(HTTPException):
        ValidationService.validate_throw_values(20, 5)


def test_validate_throw_values_bull_triple_illegal():
    with pytest.raises(HTTPException):
        ValidationService.validate_throw_values(25, 3)


# ------------------------------------------
# DOUBLE OUT RULE
# ------------------------------------------
def test_double_out_valid_double_finish():
    # 40 → 0 via double 20 → legal
    assert ValidationService.validate_double_out_rule(
        remaining_after=0,
        value=20,
        multiplier=2,
        checkout_rule="double"
    ) is None


def test_double_out_invalid_if_not_double():
    with pytest.raises(HTTPException):
        ValidationService.validate_double_out_rule(
            remaining_after=0,
            value=20,
            multiplier=1,
            checkout_rule="double"
        )


def test_double_out_ignored_if_rule_not_double():
    # Straight out → niemals Fehler
    assert ValidationService.validate_double_out_rule(
        remaining_after=0,
        value=20,
        multiplier=1,
        checkout_rule="straight"
    ) is None