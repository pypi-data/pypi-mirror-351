import pytest

from tournament.core.enum import Category, Gender, Round, Stage, string_to_gender


def test_string_to_gender() -> None:
    # Test cases for valid inputs
    assert string_to_gender("MO") == Gender.MALE
    assert string_to_gender("WO") == Gender.FEMALE

    # Test cases for invalid inputs
    assert string_to_gender("MALE") is None
    assert string_to_gender("FEMALE") is None
    assert string_to_gender("UNKNOWN") is None
    # assert string_to_gender("") is None

    # Test cases for None input
    assert string_to_gender(None) is None

    # Test cases for case insensitivity
    assert string_to_gender("mo") == Gender.MALE
    assert string_to_gender("wo") == Gender.FEMALE

    # Test cases for invalid enum conversion
    assert string_to_gender("M") is None
    assert string_to_gender("W") is None


def test_category_lt() -> None:
    # Test valid comparisons
    assert Category.PREPREVIA < Category.PREVIA
    assert Category.PREVIA < Category.BRONZE
    assert Category.BRONZE < Category.SILVER
    assert Category.SILVER < Category.GOLD

    # Test invalid type comparison
    with pytest.raises(ValueError, match="Cannot compare Category with <class 'str'>"):
        assert Category.GOLD < "invalid"


def test_round_lt() -> None:
    # Test valid comparisons
    assert Round.R1 < Round.R2
    assert Round.R2 < Round.R3
    assert Round.SIXTEENTH < Round.EIGHT
    assert Round.QUARTER < Round.SEMI
    assert Round.SEMI < Round.FINAL

    # Test invalid type comparison
    with pytest.raises(ValueError, match="Cannot compare Round with <class 'int'>"):
        assert Round.FINAL < 42


def test_stage_lt() -> None:
    # Test valid comparisons
    assert Stage.LIGA < Stage.POOL
    assert Stage.POOL < Stage.POOLA
    assert Stage.POOLA < Stage.POOLB
    assert Stage.POOLB < Stage.POOLC
    assert Stage.POOLC < Stage.POOLD
    assert Stage.POOLD < Stage.POOLE
    assert Stage.POOLE < Stage.POOLF
    assert Stage.POOLF < Stage.POOLY
    assert Stage.POOLY < Stage.POOLZ
    assert Stage.POOLZ < Stage.PLAYOFFS

    # Test invalid type comparison
    with pytest.raises(ValueError, match="Cannot compare Stage with <class 'str'>"):
        assert Stage.LIGA < "invalid"

    with pytest.raises(ValueError, match="Cannot compare Stage with <class 'int'>"):
        assert Stage.PLAYOFFS < 42


# To run the tests, use the following command in the terminal:
# pytest -v test_enum.py
