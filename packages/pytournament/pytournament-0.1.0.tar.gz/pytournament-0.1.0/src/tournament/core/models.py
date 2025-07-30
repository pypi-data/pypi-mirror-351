import bisect
from datetime import date
from typing import List, Optional, Self, Set, Tuple, Union

import pycountry
from pydantic import BaseModel, field_validator, model_validator

from tournament.core.enum import Category, GameType, Gender, Round, Stage


def lt_strings(str1: Optional[str], str2: Optional[str]) -> Optional[bool]:
    if str1 is None and str2 is None:
        return None  # Treat as equal
    if str1 is None:
        return True  # None is considered less than any value
    if str2 is None:
        return False  # Any value is greater than None
    if str1 == str2:
        return None
    if str1.lower() == str2.lower():
        return None

    return str1.lower() < str2.lower()


def lt__dates(
    dates1: Optional[set[date]],
    dates2: Optional[set[date]],
) -> Optional[bool]:
    # convert None to empty set for comparison, otherwise the comparison will get
    # very complex with the branch of len(dates1) == 0 or len(dates2) == 0
    new_dates1 = None if dates1 is None or len(dates1) == 0 else dates1
    new_dates2 = None if dates2 is None or len(dates2) == 0 else dates2

    if not new_dates1 and not new_dates2:
        return None
    if not new_dates1:
        return True
    if not new_dates2:
        return False

    # Compare by the earliest date in the set of dates
    self_min_date = min(new_dates1)
    other_min_date = min(new_dates2)
    if self_min_date != other_min_date:
        return self_min_date < other_min_date
    else:
        return None  # Dates are equal, cannot determine order based on dates alone


class Player(BaseModel):
    first_name: str
    last_name: str
    gender: Optional[Gender] = None  # Gender can be None if not specified

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name_reverse(self) -> str:
        return f"{self.last_name},  {self.first_name}"

    def _compare_names(self, other: Self) -> bool:
        """Compare players by last name, then by first name."""
        if self.last_name == other.last_name:
            return self.first_name < other.first_name
        return self.last_name < other.last_name

    def __lt__(self, other: Self) -> bool:
        """Compare players first by gender, then by names."""
        g1, g2 = self.gender, other.gender
        if g1 is None and g2 is None:  # Compare names if genders are the None
            return self._compare_names(other)
        if g1 is None:
            return True  # Treat None as "less than" any other gender
        if g2 is None:
            return False  # Treat any gender as "greater than" None

        # Compare genders if both are not None
        if g1 == g2:
            return self._compare_names(other)  # Compare names if genders are the same
        return g1 < g2  # Assuming genders are orderable

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            raise NotImplementedError
        return (self.first_name, self.last_name) == (other.first_name, other.last_name)

    def __hash__(self) -> int:
        return hash((self.first_name, self.last_name))


class Team(BaseModel):
    name: str
    players: List[Player] = []
    division: Optional[str] = None

    def add_player(self, player: Player) -> bool:
        if not isinstance(player, Player):
            raise TypeError("Expected a Player instance but got: " + str(type(player)))
        # Find the insertion point
        index = bisect.bisect_left(self.players, player)
        # Check if the item already exists
        if index < len(self.players) and self.players[index] == player:
            return False  # player already exists, do not insert (behave like a set)
        self.players.insert(index, player)
        return True  # Player was added successfully

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Team):
            raise NotImplementedError
        return (self.name, self.division) == (
            other.name,
            other.division,
        )

    def __hash__(self) -> int:
        return hash((self.name, self.division))


class TieBreak(BaseModel):
    home_score: int
    away_score: int

    @field_validator("home_score", "away_score")
    def check_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Tie break score must be non-negative")
        return value

    @model_validator(mode="after")
    def check_non_equal(self) -> Self:
        if self.home_score == self.away_score:
            raise ValueError("Tie bread score must be non-equal")
        return self


class TennisSet(BaseModel):
    home_score: int
    away_score: int
    tie_break: Optional[TieBreak] = None

    @field_validator("home_score", "away_score")
    def check_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Set must be non-negative")
        return value

    @model_validator(mode="after")
    def check_tie_break(self) -> Self:
        if self.home_score == self.away_score and not self.tie_break:
            raise ValueError("A set draw must have a tie break")
        return self


class GameScore(BaseModel):
    home_score: int
    away_score: int

    @field_validator("home_score", "away_score")
    def check_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Score must be non-negative")
        return value

    def to_csv(self) -> List[str]:
        # Return the scores as strings for CSV output
        return [str(self.home_score), str(self.away_score)]


class TennisScore(GameScore):
    sets: List[TennisSet]

    @model_validator(mode="after")
    def check_no_draw(self) -> Self:
        if self.home_score == self.away_score:
            raise ValueError("A tennis alike score cannot end in a draw.")
        return self

    @model_validator(mode="after")
    def check_final_score(self) -> Self:
        if self.home_score + self.away_score != len(self.sets):
            raise ValueError(
                f"The final score {self.home_score}:{self.away_score} "
                f"does not match the number of played sets {len(self.sets)}."
            )
        return self

    @classmethod
    def final_score(cls, sets: List[TennisSet]) -> Tuple[int, int]:
        home_score = sum(1 for s in sets if s.home_score > s.away_score)
        home_score += sum(
            1
            for s in sets
            if s.tie_break and s.tie_break.home_score > s.tie_break.away_score
        )
        away_score = sum(1 for s in sets if s.away_score > s.home_score)
        away_score += sum(
            1
            for s in sets
            if s.tie_break and s.tie_break.away_score > s.tie_break.home_score
        )
        return home_score, away_score

    @classmethod
    def create(cls, sets: List[TennisSet]) -> "TennisScore":
        home_score, away_score = TennisScore.final_score(sets)
        return cls(home_score=home_score, away_score=away_score, sets=sets)

    def to_csv(self) -> List[str]:
        scores: List[str] = []
        for tennis_set in self.sets:
            scores.append(str(tennis_set.home_score))
            scores.append(str(tennis_set.away_score))
        return scores


class Tournament(BaseModel):
    name: str
    dates: Optional[Set[date]] = None
    teams: Set[Team] = set()
    game_type: GameType = GameType.STANDARD
    division: Optional[str] = None
    country: Optional[str] = None  # Country will be validated using pycountry
    series: Optional[str] = None

    @field_validator("country")
    def validate_country(cls, value: str) -> str:
        if not value:
            return value  # Allow empty country
        # Check if the country is valid using pycountry
        if not any(
            country.name == value
            or country.alpha_2 == value
            or country.alpha_3 == value
            for country in pycountry.countries
        ):
            raise ValueError(f"Invalid country: {value}")
        return value

    def update_dates(self, new_dates: Set[date]) -> None:
        if self.dates is None:
            self.dates = set()
        self.dates.update(new_dates)

    def __hash__(self) -> int:
        return hash((self.name, self.division))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Tournament):
            raise NotImplementedError
        return (self.name, self.division) == (other.name, other.division)

    def __lt__(self, other: object) -> bool:
        # Compare tournaments by dates, country, series, division, and name
        if not isinstance(other, Tournament):
            raise ValueError("Cannot compare Tournament with non-Tournament object")

        result = lt__dates(self.dates, other.dates)
        if result is not None:
            return result

        result = lt_strings(self.country, other.country)
        if result is not None:
            return result

        result = lt_strings(self.division, other.division)
        if result is not None:
            return result

        result = lt_strings(self.series, other.series)
        if result is not None:
            return result
        # Compare by name

        return self.name < other.name


class GamePhase(BaseModel):
    category: Category = Category.GOLD
    stage: Stage
    round: Round = Round.UNKNOWN

    def __hash__(self) -> int:
        return hash((self.category, self.stage, self.round))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GamePhase):
            return NotImplemented
        return (
            self.category == other.category
            and self.stage == other.stage
            and self.round == other.round
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, GamePhase):
            raise ValueError(
                f"Cannot compare GamePhase with non-GamePhase object: ${str(other)}"
            )

        # Compare by category first
        if self.category != other.category:
            return self.category < other.category

        # If categories are equal, compare by stage
        if self.stage != other.stage:
            return self.stage < other.stage

        # If stages are also equal, compare by round
        return self.round < other.round


class Game(BaseModel):
    tournament: Optional[Tournament]
    date: Optional[date]
    home_team: Team
    away_team: Team
    phase: GamePhase
    score: Union[GameScore, TennisScore]

    @property
    def home_score(self) -> int:
        return self.score.home_score

    @property
    def away_score(self) -> int:
        return self.score.away_score

    def __hash__(self) -> int:
        return hash(
            (
                self.tournament,
                self.date,
                self.home_team,
                self.away_team,
                self.phase,
            )
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Game):
            raise NotImplementedError
        return (
            self.tournament == other.tournament
            and self.date == other.date
            and self.home_team == other.home_team
            and self.away_team == other.away_team
            and self.phase == other.phase
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Game):
            raise ValueError("Cannot compare Game with non-Game object: " + str(other))

        # Compare tournament
        result = self._compare_tournament(other)
        if result is not None:
            return result

        # Compare date
        result = self._compare_date(other)
        if result is not None:
            return result

        # Compare phase
        result = self._compare_phase(other)
        if result is not None:
            return result

        # Compare home team and away team
        return self._compare_teams(other)

    def _compare_tournament(self, other: Self) -> Optional[bool]:
        if self.tournament is None and other.tournament is None:
            return None
        elif self.tournament is None:
            return True  # None is considered less than any value
        elif other.tournament is None:
            return False  # Any value is greater than None
        elif self.tournament == other.tournament:
            return None
        return self.tournament < other.tournament

    def _compare_date(self, other: Self) -> Optional[bool]:
        if self.date == other.date:
            return None  # Treat as equal, move to the next comparison
        elif self.date is None:
            return True  # None is considered less than any value
        elif other.date is None:
            return False  # Any value is greater than None

        return self.date < other.date

    def _compare_phase(self, other: Self) -> Optional[bool]:
        if self.phase != other.phase:
            return self.phase < other.phase
        return None  # Treat as equal, move to the next comparison

    def _compare_teams(self, other: Self) -> bool:
        if self.home_team != other.home_team:
            return self.home_team.name < other.home_team.name
        return self.away_team.name < other.away_team.name

    """
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Game):
            raise ValueError("Cannot compare Game with non-Game object: " + str(other))

        # Handle None values for tournaments
        if self.tournament is None and other.tournament is None:
            pass  # Treat as equal, move to the next comparison
        elif self.tournament is None:
            return True  # None is considered less than any value
        elif other.tournament is None:
            return False  # Any value is greater than None
        elif self.tournament != other.tournament:
            return self.tournament < other.tournament

        # Handle None values for dates
        if self.date is None and other.date is None:
            pass
        elif self.date is None:
            return True  # None is considered less than any value
        elif other.date is None:
            return False  # Any value is greater than None
        elif self.date != other.date:
            return self.date < other.date

        if self.phase == other.phase:
            # If phases are equal, compare by home team
            if self.home_team != other.home_team:
                return self.home_team.name < other.home_team.name
            # If home teams are also equal, compare by away team
            return self.away_team.name < other.away_team.name
        # If phases are not equal, compare by phase
        return self.phase < other.phase
    """
