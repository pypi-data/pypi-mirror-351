import filecmp
import os
from pathlib import Path
from typing import List, Set

import pytest
from pydantic import ValidationError

from tournament.core.enum import Gender
from tournament.core.models import Game, Player, TennisScore
from tournament.csv.csv import (
    CsvConfigPadel,
    add_or_update_player,
    create_tennis_score,
    print_games_to_csv,
    read_games_padel_standard,
)


def test_add_or_update_player_conflicting_gender() -> None:
    player1 = Player(first_name="Alex", last_name="Smith", gender=Gender.MALE)
    player2 = Player(first_name="Alex", last_name="Smith", gender=Gender.FEMALE)

    players: Set[Player] = set()
    conflicting_players: List[Player] = []
    add_or_update_player(
        player=player1, players=players, conflicting_players=conflicting_players
    )
    assert 0 == len(conflicting_players)
    add_or_update_player(
        player=player2, players=players, conflicting_players=conflicting_players
    )
    assert 1 == len(conflicting_players)


@pytest.mark.parametrize(
    "file_path, total_games, total_conflicts",
    [
        ("tests/fixtures/GER_tournaments_2015_utf8.csv", 7, 0),
        ("tests/fixtures/GER_tournaments_2016_utf8.csv", 434, 5),
    ],
)
def test_read_games_padel_standard_parse_games(
    file_path: str,
    total_games: int,
    total_conflicts: int,
) -> None:
    csv_path = Path(file_path)
    games, conflicting_payers = read_games_padel_standard(csv_path)

    # Check the types
    assert isinstance(games, set)
    assert isinstance(conflicting_payers, list)
    assert all(isinstance(game, Game) for game in games)
    assert all(isinstance(player, Player) for player in conflicting_payers)

    # You can optionally check known values
    # (assuming you know what data is in the CSV)
    assert len(games) > 0
    assert len(games) == total_games
    assert len(conflicting_payers) == total_conflicts
    first_game = next(iter(games))
    assert first_game.home_team is not None
    assert first_game.away_team is not None
    assert first_game.score.home_score != first_game.score.away_score


@pytest.mark.parametrize(
    "scores, sets, home_score, away_score",
    [
        (["6", "4", "3", "6", "7", "5", "6", "3"], 4, 3, 1),
        (["6", "4", "3", "6", "7", "5"], 3, 2, 1),
    ],
)
def test_create_tennis_score_valid(
    scores: List[str], sets: int, home_score: int, away_score: int
) -> None:
    result: TennisScore = create_tennis_score(scores)
    assert isinstance(result, TennisScore)
    assert len(result.sets) == sets
    assert result.home_score == home_score
    assert result.away_score == away_score


def test_create_tennis_score_empty_scores() -> None:
    scores: List[str] = []
    with pytest.raises(ValueError, match="A tennis alike score cannot end in a draw."):
        create_tennis_score(scores)


def test_create_tennis_score_invalid_length() -> None:
    scores = ["6", "4", "3", "6", "7"]  # Odd number of scores
    with pytest.raises(ValueError, match="Wrong scores length: 5"):
        create_tennis_score(scores)


def test_create_tennis_score_with_empty_set_scores() -> None:
    scores = ["6", "", "6", "1"]
    with pytest.raises(ValidationError):
        create_tennis_score(scores)


# TODO: test a draw!!


def test_print_games_to_csv_sorted() -> None:
    # Paths for input and output files
    input_dir = Path("tests/fixtures/")
    input_files: List[Path] = [
        Path(input_dir / "GER_tournaments_2015_utf8.csv"),
        Path(input_dir / "GER_tournaments_2016_utf8.csv"),
    ]
    output_dir = Path("tests/fixtures/output")
    # Ensure the output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file in input_files:
        # Define the output file name based on the input file name
        output_file = output_dir / f"{Path(input_file).stem}_sorted_generated.csv"
        sorted_file = output_dir / f"{Path(input_file).stem}_sorted.csv"

        games, _ = read_games_padel_standard(input_file)
        sorted_games = sorted(games)

        # Ensure the output file does not exist before the test
        if output_file.exists():
            os.remove(output_file)

        # Call the method to generate the CSV file
        print_games_to_csv(
            games=sorted_games, output_file=output_file, config=CsvConfigPadel()
        )

        # Compare the generated file with the sorted reference file
        assert filecmp.cmp(output_file, sorted_file)
        # delete the generated file after the test
        if output_file.exists():
            os.remove(output_file)


def test_csv_file_not_found() -> None:
    # Test for FileNotFoundError when the file does not exist
    non_existent_file = Path("non_existent_file.csv")
    with pytest.raises(
        FileNotFoundError, match=f"CSV file not found: {non_existent_file}"
    ):
        read_games_padel_standard(non_existent_file)


def test_csv_file_is_not_a_file() -> None:
    # Test for ValueError when the path is not a file (e.g., a directory)
    directory_path = Path("tests/fixtures")
    with pytest.raises(ValueError, match=f"Path is not a file: {directory_path}"):
        read_games_padel_standard(directory_path)


def test_csv_file_wrong_extension() -> None:
    # Test for ValueError when the file does not have a .csv extension
    wrong_extension_file = Path("tests/fixtures/file.txt")
    with pytest.raises(ValueError, match=f"File is not a CSV: {wrong_extension_file}"):
        read_games_padel_standard(wrong_extension_file)


def test_csv_file_empty() -> None:
    # Test for ValueError when the file is empty
    empty_file = Path("tests/fixtures/empty.csv")
    empty_file.touch()  # Create an empty file
    with pytest.raises(ValueError, match=f"CSV file is empty: {empty_file}"):
        read_games_padel_standard(empty_file)


def test_csv_file_too_small() -> None:
    # Test for ValueError when the file is too small to be valid
    small_file = Path("tests/fixtures/small.csv")
    small_file.write_text("small content")  # Write small content to the file
    with pytest.raises(
        ValueError, match=f"CSV file is too small to be valid: {small_file}"
    ):
        read_games_padel_standard(small_file)


def test_csv_file_too_large(tmp_path: Path) -> None:
    # Create a temporary file with content larger than 10 MB
    large_file = tmp_path / "large.csv"
    large_file.write_text(
        "a" * (10 * 1024 * 1024 + 1)
    )  # Write content larger than 10 MB

    # Test for ValueError when the file is too large
    with pytest.raises(ValueError, match=f"CSV file is too large: {large_file}"):
        read_games_padel_standard(large_file)
