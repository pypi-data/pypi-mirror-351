from datetime import date
from typing import Tuple

import pytest

from tournament.core.enum import Category, Gender, Round, Stage
from tournament.core.models import (
    Game,
    GamePhase,
    GameScore,
    Player,
    Team,
    TennisScore,
    TennisSet,
    TieBreak,
    Tournament,
    lt__dates,
    lt_strings,
)


def test_lt_strings() -> None:
    # Test cases where both strings are None
    assert lt_strings(None, None) is None  # Both are None, treated as equal

    # Test cases where one string is None
    assert lt_strings(None, "apple") is True  # None is less than any value
    assert lt_strings("apple", None) is False  # Any value is greater than None

    # Test cases where strings are equal
    assert lt_strings("apple", "apple") is None  # Equal strings, treated as equal
    assert lt_strings("APPLE", "apple") is None  # Case-insensitive equality

    # Test cases where strings are different
    assert lt_strings("apple", "banana") is True  # "apple" < "banana"
    assert lt_strings("banana", "apple") is False  # "banana" > "apple"

    # Test cases with case-insensitive comparison
    assert (
        lt_strings("Apple", "banana") is True
    )  # "apple" < "banana" (case-insensitive)
    assert (
        lt_strings("Banana", "apple") is False
    )  # "banana" > "apple" (case-insensitive)


def test_lt_dates() -> None:
    # Create Tournament instances with different dates
    tournament1 = Tournament(name="Tournament A", dates={date(2023, 1, 1)})
    tournament2 = Tournament(name="Tournament B", dates={date(2023, 2, 1)})
    tournament3 = Tournament(name="Tournament C", dates=None)
    tournament4 = Tournament(name="Tournament E", dates=None)
    tournament5 = Tournament(name="Tournament D", dates=set())
    tournament6 = Tournament(name="Tournament F", dates=set())
    tournament7 = Tournament(name="Tournament G", dates={date(2023, 1, 1)})

    assert lt__dates(tournament1.dates, tournament2.dates) is True  # Earlier date
    assert lt__dates(tournament2.dates, tournament1.dates) is False  # Later date
    assert lt__dates(tournament3.dates, tournament1.dates) is True  # None < any date
    assert lt__dates(tournament1.dates, tournament3.dates) is False  # Any date > None
    assert (
        lt__dates(tournament3.dates, tournament4.dates) is None
    )  # equality with None  returns None
    assert (
        lt__dates(tournament4.dates, tournament3.dates) is None
    )  # equality with None returns None
    assert (
        lt__dates(tournament5.dates, tournament6.dates) is None
    )  # equality with empty sets returns None
    assert (
        lt__dates(tournament6.dates, tournament5.dates) is None
    )  # equality with empty sets returns None
    assert (
        lt__dates(tournament1.dates, tournament5.dates) is False
    )  # Any date < empty set
    assert (
        lt__dates(tournament5.dates, tournament1.dates) is True
    )  # Empty set > any date
    assert lt__dates(tournament1.dates, tournament7.dates) is None  # Same date
    assert lt__dates(tournament7.dates, tournament1.dates) is None  # Same date
    # assert lt__dates(tournament3.dates, tournament5.dates) is False  # None == empty
    # assert lt__dates(tournament5.dates, tournament3.dates) is False  # Empty == None


class TestPlayer:
    def test_full_name(self) -> None:
        player = Player(first_name="John", last_name="Doe")
        assert player.full_name == "John Doe"
        assert player.full_name_reverse == "Doe,  John"

    def test_equality_and_hash(self) -> None:
        p1 = Player(first_name="Anna", last_name="Smith", gender=Gender.FEMALE)
        p2 = Player(first_name="Anna", last_name="Smith", gender=Gender.FEMALE)
        p3 = Player(first_name="Anna", last_name="Smith", gender=Gender.MALE)
        players = sorted([p2, p1])
        assert players[0] == p1
        assert p1 == p2
        assert p1 == p3
        assert hash(p1) == hash(p2)
        assert hash(p1) == hash(p3)

    def test_instance_check(self) -> None:
        player1 = Player(first_name="Paquito", last_name="Navarro", gender=Gender.MALE)
        with pytest.raises(NotImplementedError):
            assert player1 == "Not a Player"

    def test_player_sorting_and_equality(self) -> None:
        p1 = Player(first_name="Alice", last_name="Smith", gender=Gender.FEMALE)
        p2 = Player(first_name="Alice", last_name="Smith", gender=Gender.FEMALE)
        players = sorted([p2, p1])
        assert players[0] == p1

    @pytest.fixture
    def players(self) -> Tuple:
        player1 = Player(first_name="Paquito", last_name="Navarro", gender=Gender.MALE)
        player2 = Player(first_name="Juan", last_name="Lebrón", gender=Gender.MALE)
        player3 = Player(first_name="Gemma", last_name="Triay", gender=Gender.FEMALE)
        player4 = Player(
            first_name="Alejandra", last_name="Salazar", gender=Gender.FEMALE
        )
        player5 = Player(
            first_name="Mapi", last_name="Sanchez Alayeto", gender=Gender.FEMALE
        )
        player6 = Player(
            first_name="Majo", last_name="Sanchez Alayeto", gender=Gender.FEMALE
        )
        player7 = Player(first_name="Django", last_name="Unchained", gender=None)
        player8 = Player(first_name="Tarantino", last_name="Unchained", gender=None)
        return player1, player2, player3, player4, player5, player6, player7, player8

    def test_compare_names(self, players: Tuple) -> None:
        player1, player2, player3, player4, player5, player6, _, _ = players

        # Compare last_name
        assert player1._compare_names(player2) is False
        assert player2._compare_names(player1) is True
        assert player1._compare_names(player3) is True
        assert player4._compare_names(player1) is False
        # Compare first_name
        assert player5._compare_names(player6) is False

    def test_lt(self, players: Tuple) -> None:
        player1, player2, player3, player4, _, _, player7, player8 = players

        # assert player1 > player7

        # Test gender comparison
        assert player1 > player4  # MALE < FEMALE
        assert not player4 > player1  # FEMALE > MALE

        # Test None gender comparison
        assert player7 < player1  # None < MALE
        assert not player1 < player2  # MALE > None
        assert player3 > player7  # FEMALE > None
        assert player7 < player4  # None < FEMALE
        assert player8 > player7  # None < None
        assert player1 > player7
        assert not player7 > player1

        # Test same gender comparison
        assert player1 > player2  # Compare by names


class TestTeam:
    def test_team_equality_and_hash(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        p2 = Player(first_name="C", last_name="D")
        team1 = Team(name="Team1", players={p1, p2}, division="MO")
        team2 = Team(name="Team1", players={p1, p2}, division="MO")
        assert team1 == team2
        assert hash(team1) == hash(team2)

    def test_instance_check(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        p2 = Player(first_name="C", last_name="D")
        team1 = Team(name="Team1", players={p1, p2}, division="MO")
        with pytest.raises(NotImplementedError):
            assert team1 == "team2"

    def test_add_player(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        p2 = Player(first_name="C", last_name="D")
        p3 = Player(first_name="E", last_name="F")
        p4 = Player(first_name="G", last_name="H")
        team = Team(name="Team1", players={p1}, division="MO")

        assert team.add_player(p2)
        assert len(team.players) == 2
        assert p1 == team.players[0]  # Assuming players are stored in a sorted order
        assert p2 == team.players[1]

        assert team.add_player(p4)
        assert len(team.players) == 3
        assert p1 == team.players[0]
        assert p2 == team.players[1]
        assert p4 == team.players[2]

        assert team.add_player(p3)
        assert len(team.players) == 4
        assert p1 == team.players[0]
        assert p2 == team.players[1]
        assert p3 == team.players[2]
        assert p4 == team.players[3]

    def test_add_duplicate_player(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        team = Team(name="Team1", players={p1}, division="MO")

        # Adding the same player again should not change the team
        assert not team.add_player(p1)
        assert len(team.players) == 1

    @pytest.mark.skip
    def test_add_player_with_different_case(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        p2 = Player(first_name="a", last_name="b")
        team = Team(name="Team1", players={p1}, division="MO")
        # Adding a player with the same name but different case
        # should not change the team
        assert not team.add_player(p2)

    def test_add_invalid_player(self) -> None:
        p1 = Player(first_name="A", last_name="B")
        team = Team(name="Team1", players={p1}, division="MO")

        # Adding a non-Player object should raise an error
        with pytest.raises(TypeError):
            team.add_player("Not a Player")  # type: ignore


class TestTieBreak:
    def test_valid_tie_break(self) -> None:
        tb = TieBreak(home_score=7, away_score=5)
        assert tb.home_score == 7

    def test_negative_score(self) -> None:
        with pytest.raises(ValueError):
            TieBreak(home_score=-1, away_score=5)

    def test_equal_scores_invalid(self) -> None:
        with pytest.raises(ValueError):
            TieBreak(home_score=7, away_score=7)


class TestTennisSet:
    def test_valid_set(self) -> None:
        s = TennisSet(home_score=6, away_score=4)
        assert s.tie_break is None

    def test_invalid_draw_without_tiebreak(self) -> None:
        with pytest.raises(ValueError):
            TennisSet(home_score=6, away_score=6)

    def test_valid_draw_with_tiebreak(self) -> None:
        tb = TieBreak(home_score=7, away_score=5)
        s = TennisSet(home_score=6, away_score=6, tie_break=tb)
        assert s.tie_break == tb

    def test_negative_set(self) -> None:
        with pytest.raises(ValueError):
            TennisSet(home_score=6, away_score=-4)
        with pytest.raises(ValueError):
            TennisSet(home_score=-6, away_score=4)
        with pytest.raises(ValueError):
            TennisSet(home_score=-6, away_score=-4)


class TestTennisScore:
    def test_valid_score_creation(self) -> None:
        sets = [TennisSet(home_score=6, away_score=4) for _ in range(2)]
        score = TennisScore.create(sets)
        assert score.home_score == 2
        assert score.away_score == 0

    def test_draw_score_invalid(self) -> None:
        sets = [
            TennisSet(home_score=6, away_score=4),
            TennisSet(home_score=4, away_score=6),
        ]
        with pytest.raises(ValueError):
            TennisScore.create(sets)

    def test_score_mismatch(self) -> None:
        sets = [
            TennisSet(home_score=6, away_score=4),
            TennisSet(home_score=6, away_score=4),
        ]
        score = TennisScore.create(sets)
        score.home_score += 1  # corrupting
        with pytest.raises(ValueError):
            TennisScore(**score.model_dump())


class TestTournament:
    @pytest.fixture
    def tournament(self) -> Tournament:
        return Tournament(
            name="Capital Cup",
            teams={Team(name="Touch Berlin"), Team(name="Touch Munich")},
        )

    def test_valid_country(self) -> None:
        t = Tournament(
            name="Open Cup",
            dates={date.today()},
            teams=set(),
            division="A",
            country="US",
        )
        assert t.country == "US"

    def test_invalid_country(self) -> None:
        with pytest.raises(ValueError):
            Tournament(
                name="Open Cup",
                division="MO",
                dates=set(),
                teams=set(),
                country="Invalidia",
            )

    def test_equality_and_hash(self, tournament: Tournament) -> None:
        t2 = Tournament(name="Capital Cup", teams=[])
        t3 = Tournament(name="Touch and Tapas", teams=[])
        t4 = Tournament(name="Capital Cup", teams=[], division="MO")
        assert tournament == t2
        assert tournament != t3
        assert hash(tournament) == hash(t2)
        assert tournament != t4
        assert hash(tournament) != hash(t4)

    def test_instance_check(self) -> None:
        t1 = Tournament(name="Capital Cup", teams=[])
        with pytest.raises(NotImplementedError):
            assert t1 == "tournament 2"

    def test_update_dates_when_dates_are_none(self, tournament: Tournament) -> None:
        # Initially, dates should be None
        assert tournament.dates is None

        # Update with new dates
        new_dates = {date(2023, 6, 1), date(2023, 6, 2)}
        tournament.update_dates(new_dates)

        # Check that dates are updated correctly
        assert tournament.dates == new_dates

    def test_update_dates_when_dates_exist(self, tournament: Tournament) -> None:
        # Set initial dates
        initial_dates = {date(2023, 6, 1)}
        tournament.dates = initial_dates

        # New dates to add
        new_dates = {date(2023, 6, 2), date(2023, 6, 3)}
        tournament.update_dates(new_dates)

        # Check that dates are updated correctly
        assert tournament.dates == {
            date(2023, 6, 1),
            date(2023, 6, 2),
            date(2023, 6, 3),
        }

    def test_update_dates_with_empty_set(self, tournament: Tournament) -> None:
        # Set initial dates
        initial_dates = {date(2023, 6, 1)}
        tournament.dates = initial_dates

        # Update with an empty set
        tournament.update_dates(set())

        # Check that dates remain unchanged
        assert tournament.dates == initial_dates

    def test_tournament_lt(self) -> None:
        # Create Tournament instances with different attributes
        tournament1 = Tournament(
            name="Tournament A",
            dates={date(2023, 1, 1)},
            country="Germany",
            series="Series 1",
            division="Division 1",
        )
        tournament2 = Tournament(
            name="Tournament B",
            dates={date(2023, 2, 1)},
            country="France",
            series="Series 2",
            division="Division 2",
        )
        tournament3 = Tournament(
            name="Tournament C",
            dates=None,
            country=None,
            series=None,
            division=None,
        )
        tournament4 = Tournament(
            name="Tournament A",
            dates={date(2023, 1, 1)},
            country="Netherlands",
            series="Series 1",
            division="Division 1",
        )
        tournament6 = Tournament(
            name="Tournament A",
            dates={date(2023, 1, 1)},
            country="Germany",
            series="Series 1",
            division="Division 2",
        )
        tournament7 = Tournament(
            name="Tournament A",
            dates={date(2023, 1, 1)},
            country="Germany",
            series="Series 2",
            division="Division 1",
        )
        tournament8 = Tournament(
            name="Tournament B",
            dates={date(2023, 1, 1)},
            country="Germany",
            series="Series 1",
            division="Division 1",
        )

        # Test dates comparison
        assert tournament1 < tournament2  # Compare by dates
        assert tournament3 < tournament1  # Compare any date > None
        assert tournament1 > tournament3  # Any date > None
        assert not (tournament2 < tournament1)  # Reverse comparison

        # Test countries comparison
        assert tournament1 < tournament4  # Germany < Netherlands
        assert not (tournament4 < tournament1)  # Reverse comparison

        # Test series comparison
        assert tournament1 < tournament6  # Division 1 < Division 2
        assert not (tournament6 < tournament1)  # Reverse comparison

        # Test series comparison with different series
        assert tournament1 < tournament7  # Series 1 < Series 2
        assert not (tournament7 < tournament1)  # Reverse comparison

        # Test names comparison
        assert tournament1 < tournament8  # Tournament A < Tournament B
        assert not (tournament8 < tournament1)  # Reverse comparison

        # Test wrong arguments
        with pytest.raises(ValueError):
            assert (
                tournament1 < "not a tournament"
            )  # Invalid comparison raises ValueError


def test_game_score_and_phase() -> None:
    p1 = Player(first_name="A", last_name="B")
    p2 = Player(first_name="C", last_name="D")
    team1 = Team(name="T1", players={p1}, division="Pro")
    team2 = Team(name="T2", players={p2}, division="Pro")
    score = GameScore(home_score=2, away_score=3)

    game = Game(
        tournament=None,
        date=None,
        home_team=team1,
        away_team=team2,
        score=score,
        phase=GamePhase(stage=Stage.POOLA, round=Round.R1),
    )

    assert game.home_score == 2
    assert game.away_score == 3


class TestGameScore:
    def test_negative_score(self) -> None:
        with pytest.raises(ValueError):
            GameScore(home_score=6, away_score=-4)
        with pytest.raises(ValueError):
            GameScore(home_score=-6, away_score=4)
        with pytest.raises(ValueError):
            GameScore(home_score=-6, away_score=-4)


class TestGamePhase:
    def test_equality_and_hash(self) -> None:
        phase1 = GamePhase(
            category=Category.GOLD, stage=Stage.PLAYOFFS, round=Round.SEMI
        )
        phase2 = GamePhase(
            category=Category.GOLD, stage=Stage.PLAYOFFS, round=Round.SEMI
        )
        phase3 = GamePhase(
            category=Category.GOLD, stage=Stage.PLAYOFFS, round=Round.FINAL
        )

        # __eq__
        assert phase1 == phase2
        assert phase1 != phase3
        assert phase1 != "not a GamePhase"

        # __hash__
        assert hash(phase1) == hash(phase2)
        assert hash(phase1) != hash(phase3)

    def test_defaults(self) -> None:
        phase = GamePhase(stage=Stage.POOLA)
        assert phase.category == Category.GOLD
        assert phase.round == Round.UNKNOWN

    def test_invalid_comparison(self) -> None:
        phase1 = GamePhase(stage=Stage.PLAYOFFS, round=Round.R1)

        with pytest.raises(ValueError):
            assert phase1 < "not a GamePhase"  # Should raise ValueError

    def test_lt(self) -> None:
        phase1 = GamePhase(
            category=Category.GOLD, stage=Stage.PLAYOFFS, round=Round.SEMI
        )
        phase2 = GamePhase(
            category=Category.GOLD, stage=Stage.PLAYOFFS, round=Round.FINAL
        )
        phase3 = GamePhase(
            category=Category.SILVER, stage=Stage.PLAYOFFS, round=Round.FINAL
        )
        phase4 = GamePhase(category=Category.GOLD, stage=Stage.POOLA, round=Round.R1)
        phase5 = GamePhase(category=Category.GOLD, stage=Stage.POOLB, round=Round.R1)

        # Round comparison
        assert phase1 < phase2
        assert not phase2 < phase1

        # Category comparison
        assert phase3 < phase1
        assert not phase1 < phase3

        # Stage comparison
        assert phase4 < phase5  # POOLA < POOLB
        assert not phase5 < phase4  # POOLB > POOLA


class TestGame:
    def make_team(self, name: str, player_name: str) -> Team:
        player = Player(first_name=player_name, last_name=player_name)
        return Team(name=name, players={player}, division=None)

    def test_tennis_score(self) -> None:
        team1 = self.make_team("T1", "A")
        team2 = self.make_team("T2", "B")
        sets = [
            TennisSet(home_score=6, away_score=4),
            TennisSet(home_score=6, away_score=4),
        ]
        score = TennisScore.create(sets)
        game = Game(
            tournament=None,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=GamePhase(stage=Stage.POOLA, round=Round.R1),
            score=score,
        )

        assert game.home_score == 2
        assert game.away_score == 0

    def test_gamescore(self) -> None:
        team1 = self.make_team("T1", "A")
        team2 = self.make_team("T2", "B")
        score = GameScore(home_score=3, away_score=1)
        game = Game(
            tournament=None,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=GamePhase(stage=Stage.PLAYOFFS),
            score=score,
        )

        assert game.home_score == 3
        assert game.away_score == 1

    def test_equality_and_hash(self) -> None:
        team1 = self.make_team("T1", "A")
        team2 = self.make_team("T2", "B")
        phase = GamePhase(stage=Stage.PLAYOFFS)
        tournament = Tournament(name="Championship", teams={team1, team2})
        date_played = date(2024, 5, 1)
        score = GameScore(home_score=2, away_score=1)

        game1 = Game(
            tournament=tournament,
            date=date_played,
            home_team=team1,
            away_team=team2,
            phase=phase,
            score=score,
        )
        game2 = Game(
            tournament=tournament,
            date=date_played,
            home_team=team1,
            away_team=team2,
            phase=phase,
            score=score,
        )
        new_tournament = Tournament(name="La liga")
        game3 = Game(
            tournament=new_tournament,  # different tournament
            date=date_played,
            home_team=team1,
            away_team=team2,
            phase=phase,
            score=score,
        )

        assert game1 == game2
        assert hash(game1) == hash(game2)
        assert game1 != game3
        assert hash(game1) != hash(game3)

    def test_eq_with_invalid_object(self) -> None:
        team1 = self.make_team("T1", "A")
        team2 = self.make_team("T2", "B")
        game = Game(
            tournament=None,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=GamePhase(stage=Stage.PLAYOFFS),
            score=GameScore(home_score=1, away_score=1),
        )

        with pytest.raises(NotImplementedError):
            assert game == "not a game"

    def test_lt(self) -> None:
        team1 = self.make_team("T1", "A")
        team2 = self.make_team("T2", "B")
        score = GameScore(home_score=1, away_score=2)
        phase1 = GamePhase(stage=Stage.PLAYOFFS, round=Round.SEMI)
        phase2 = GamePhase(stage=Stage.PLAYOFFS, round=Round.FINAL)
        tournament1 = Tournament(name="Championship", teams={team1, team2})
        tournament2 = Tournament(name="League", teams={team1, team2})

        game1 = Game(
            tournament=None,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=phase1,
            score=score,
        )
        game2 = Game(
            tournament=None,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=phase2,
            score=score,
        )
        game3 = Game(
            tournament=tournament1,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=phase1,
            score=score,
        )
        game4 = Game(
            tournament=tournament2,
            date=None,
            home_team=team1,
            away_team=team2,
            phase=phase1,
            score=score,
        )
        game5 = Game(
            tournament=None,
            date=date(2024, 5, 1),
            home_team=team1,
            away_team=team2,
            phase=phase1,
            score=score,
        )
        game6 = Game(
            tournament=None,
            date=date(2024, 6, 1),
            home_team=team1,
            away_team=team2,
            phase=phase1,
            score=score,
        )

        assert game2 > game1  # phase2 > phase1
        assert game1 < game2  # phase1 < phase2
        assert not game1 > game2  # phase2 > phase1

        assert game1 < game3  # game1 < game3 (different tournament)
        assert not game3 < game1  # game3 > game1 (different tournament)
        assert game1 == game1  # game1 == game1 (same game)

        # Tournament comparison
        assert game3 < game4  # tournament1 < tournament2
        assert not game4 < game3

        # Date comparison
        assert game1 < game5
        assert not game5 < game1
        assert game5 < game6
        assert not game6 < game5

        with pytest.raises(ValueError):
            assert game1 < "not a game"
