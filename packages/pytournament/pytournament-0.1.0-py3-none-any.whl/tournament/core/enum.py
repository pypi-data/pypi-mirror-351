from enum import StrEnum
from typing import Optional


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class GameType(StrEnum):
    STANDARD = "standard"
    MULTIGAME = "multi"


class Category(StrEnum):
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"
    PREVIA = "previa"
    PREPREVIA = "preprevia"

    def __lt__(self, other: object) -> bool:
        _order = {"preprevia": 0, "previa": 1, "bronze": 2, "silver": 3, "gold": 4}

        if not isinstance(other, Category):
            raise ValueError(f"Cannot compare Category with {type(other)}")
        return _order[self.value] < _order[other.value]


class Round(StrEnum):
    UNKNOWN = ""
    R1 = "round1"
    R2 = "round2"
    R3 = "round3"
    R4 = "round4"
    R5 = "round5"
    R6 = "round6"
    SIXTEENTH = "ko16"
    EIGHT = "ko8"
    QUARTER = "ko4"
    SEMI = "ko2"
    third_position = "pos3"
    FINAL = "ko1"

    def __lt__(self, other: object) -> bool:
        _order = {
            "": 0,
            "round1": 1,
            "round2": 2,
            "round3": 3,
            "round4": 4,
            "round5": 5,
            "round6": 6,
            "ko16": 7,
            "ko8": 8,
            "ko4": 9,
            "ko2": 10,
            "pos3": 11,
            "ko1": 12,
        }
        if not isinstance(other, Round):
            raise ValueError(f"Cannot compare Round with {type(other)}")
        return _order[self.value] < _order[other.value]


class Stage(StrEnum):
    LIGA = "liga"
    POOL = "pool"
    POOLA = "poola"
    POOLB = "poolb"
    POOLC = "poolc"
    POOLD = "poold"
    POOLE = "poole"
    POOLF = "poolf"
    POOLY = "pooly"
    POOLZ = "poolz"
    PLAYOFFS = "playoffs"

    def __lt__(self, other: object) -> bool:
        _order = {
            "liga": 0,
            "pool": 1,
            "poola": 2,
            "poolb": 3,
            "poolc": 4,
            "poold": 5,
            "poole": 6,
            "poolf": 7,
            "pooly": 8,
            "poolz": 9,
            "playoffs": 10,
        }
        if not isinstance(other, Stage):
            raise ValueError(f"Cannot compare Stage with {type(other)}")
        return _order[self.value] < _order[other.value]


def string_to_gender(value: Optional[str]) -> Optional[Gender]:
    # Check if the input value is None
    if value is None:
        return None

    gender_map = {
        "MO": "male",
        "WO": "female",
    }

    # Get the mapped value or return None if not found
    gender_value = gender_map.get(value.upper())
    if gender_value is None:
        return None

    # Return the corresponding Gender enum member
    return Gender(gender_value)
