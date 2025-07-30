import csv
import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from pydantic import ValidationError

from tournament.core.enum import Gender, string_to_gender
from tournament.core.models import (
    Game,
    GamePhase,
    Player,
    Team,
    TennisScore,
    TennisSet,
    Tournament,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CsvConfigPadel:
    encoding: str = "utf-8"
    delimiter: str = ";"
    skip_header: bool = False
    date_format: str = "%d.%m.%Y"
    # csv indexes
    country_index: int = 0
    tournament_name_index: int = 1
    tournament_series_index: int = 2
    division_index: int = 3
    date_index: int = 4
    game_type_index: int = 5
    category_index: int = 6
    stage_index: int = 7
    round_index: int = 8
    player_start_index: int = 9
    start_score_index: int = 17


def add_or_update_player(
    player: Player,
    players: Set[Player],
    conflicting_players: List[Player],
) -> None:
    if player in players:
        for p in players:
            if (
                p == player
                and p.gender != player.gender
                and p.gender is not None
                and player.gender is not None
            ):
                conflicting_players.append(player)
                logger.warning(
                    f"Found player with same name and different gender: {p} vs {player}"
                )
    else:
        players.add(player)


def create_and_add_player(
    row: List[str],
    index: int,
    players: Set[Player],
    conflicting_players: List[Player],
    gender: Optional[Gender] = None,
) -> Player:
    last_name = row[index]
    first_name = row[index + 1]
    player = Player(first_name=first_name, last_name=last_name, gender=gender)
    add_or_update_player(player, players, conflicting_players)
    return player


def add_or_update_tournament(
    tournament: Tournament, tournaments: Dict[int, Tournament]
) -> None:
    key = hash(Tournament)
    if key in tournaments:
        if tournament.dates:
            existing_tournament = tournaments[key]
            existing_tournament.update_dates(tournament.dates)
    else:
        tournaments[key] = tournament


def format_team_name_padel(last_name1: str, last_name2: str) -> str:
    if last_name1 <= last_name2:
        return f"{last_name1} - {last_name2}"
    else:
        return f"{last_name2} - {last_name1}"


def create_tennis_score(scores: list[str]) -> TennisScore:
    if len(scores) % 2 != 0:
        raise ValueError(f"Wrong scores length: {len(scores)}")

    sets: List[TennisSet] = []
    for i in range(0, len(scores), 2):
        tennisSet = TennisSet(home_score=scores[i], away_score=scores[i + 1])
        sets.append(tennisSet)

    result = TennisScore.create(sets=sets)
    return result


def process_row(
    row: List[str],
    games: Set[Game],
    tournaments: Dict[int, Tournament],
    players: Set[Player],
    conflicting_players: List[Player],
    teams: Set[Team],
    config: CsvConfigPadel,
) -> None:
    # Create tournament
    tournament_name: str = row[config.tournament_name_index]
    division: str = row[config.division_index]
    tournament_date: date = datetime.strptime(
        row[config.date_index], config.date_format
    ).date()
    game_type = row[config.game_type_index].lower()
    country: str = row[config.country_index]
    series: str = row[config.tournament_series_index]
    tournament = Tournament(
        name=tournament_name,
        dates=[tournament_date],
        division=division,
        game_type=game_type,
        country=country,
        teams=teams,
        series=series,
    )
    add_or_update_tournament(tournament=tournament, tournaments=tournaments)

    # Create players from the row
    gender = string_to_gender(division)
    p1 = create_and_add_player(
        row=row,
        index=config.player_start_index,
        players=players,
        conflicting_players=conflicting_players,
        gender=gender,
    )
    p2 = create_and_add_player(
        row=row,
        index=config.player_start_index + 2,
        players=players,
        conflicting_players=conflicting_players,
        gender=gender,
    )
    p3 = create_and_add_player(
        row=row,
        index=config.player_start_index + 4,
        players=players,
        conflicting_players=conflicting_players,
        gender=gender,
    )
    p4 = create_and_add_player(
        row=row,
        index=config.player_start_index + 6,
        players=players,
        conflicting_players=conflicting_players,
        gender=gender,
    )

    # Create a team
    team_name1 = format_team_name_padel(p1.last_name, p2.last_name)
    team_name2 = format_team_name_padel(p3.last_name, p4.last_name)
    home_team = Team(division=division, name=team_name1)
    away_team = Team(division=division, name=team_name2)
    home_team.add_player(p1)
    home_team.add_player(p2)
    away_team.add_player(p3)
    away_team.add_player(p4)
    teams.update([home_team, away_team])

    # Create Score
    score = create_tennis_score(row[config.start_score_index :])

    # Create phase
    phase = GamePhase(
        category=row[config.category_index].lower(),
        stage=row[config.stage_index].lower(),
        round=row[config.round_index].lower(),
    )

    # Create game
    game = Game(
        tournament=tournament,
        date=tournament_date,
        home_team=home_team,
        away_team=away_team,
        phase=phase,
        score=score,
    )
    games.add(game)


def read_games_padel_standard(csv_file: Path) -> Tuple[Set[Game], List[Player]]:
    """
    Reads a CSV file containing padel tournament data and
    returns a set of games and a list of conflicting players.

    :param csv_file: Path to the CSV file.
    :return: A tuple containing a set of Game objects
        and a list of Player objects with conflicting data.
    """
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_file}")
    if not csv_file.is_file():
        raise ValueError(f"Path is not a file: {csv_file}")
    if csv_file.suffix.lower() != ".csv":
        raise ValueError(f"File is not a CSV: {csv_file}")
    if csv_file.stat().st_size == 0:
        raise ValueError(f"CSV file is empty: {csv_file}")
    if csv_file.stat().st_size < 100:
        raise ValueError(
            f"CSV file is too small to be valid: "
            f"{csv_file} with size {csv_file.stat().st_size} bytes"
        )
    if csv_file.stat().st_size > 10 * 1024 * 1024:  # 10 MB
        raise ValueError(
            f"CSV file is too large: {csv_file} "
            f"with size {csv_file.stat().st_size} bytes"
        )

    config = CsvConfigPadel()

    with open(csv_file, newline="", encoding=config.encoding) as file:
        reader = csv.reader(file, delimiter=config.delimiter)

        # init data structures
        tournaments: Dict[int, Tournament] = dict()
        players: Set[Player] = set()
        conflicting_players: List[Player] = list()
        teams: Set[Team] = set()
        games: Set[Game] = set()

        # iterate the rows
        for row in reader:
            try:
                process_row(
                    row=row,
                    games=games,
                    tournaments=tournaments,
                    players=players,
                    conflicting_players=conflicting_players,
                    teams=teams,
                    config=config,
                )
            except ValidationError as e:
                logger.error(f"Validation error creating model: {e}")
                raise e
            except Exception as e:
                logger.error(f"Error processing row {row}: {e}")
                raise e
        return games, conflicting_players


def print_games_to_csv(
    games: List[Game], output_file: Path, config: CsvConfigPadel
) -> None:
    with open(output_file, mode="w", newline="", encoding=config.encoding) as file:
        writer = csv.writer(file, delimiter=config.delimiter)

        # Write game data
        for game in games:
            home_players = list(game.home_team.players)
            away_players = list(game.away_team.players)

            row = [
                game.tournament.country if game.tournament else "",
                game.tournament.name if game.tournament else "",
                game.tournament.series if game.tournament else "",
                game.home_team.division if game.home_team else "",
                game.date.strftime(config.date_format) if game.date else "",
                game.tournament.game_type if game.tournament else "",
                game.phase.category,
                game.phase.stage,
                game.phase.round,
                home_players[0].last_name if len(home_players) > 0 else "",
                home_players[0].first_name if len(home_players) > 0 else "",
                home_players[1].last_name if len(home_players) > 1 else "",
                home_players[1].first_name if len(home_players) > 1 else "",
                away_players[0].last_name if len(away_players) > 0 else "",
                away_players[0].first_name if len(away_players) > 0 else "",
                away_players[1].last_name if len(away_players) > 1 else "",
                away_players[1].first_name if len(away_players) > 1 else "",
                *game.score.to_csv(),
            ]
            writer.writerow(row)
