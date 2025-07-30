import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from leaguemanager.core.toolbox import clear_table
from leaguemanager.models import League, Season
from leaguemanager.services import LeagueSyncService, SeasonSyncService


def test_create_league(session, league_service) -> None:
    new_league = League(name="Test Create League", category="MEN", division="A", match_day="SUN")
    test_league = league_service.create(new_league)
    assert test_league.name == "Test Create League"
    clear_table(session, League)


def test_create_many_leagues(session, league_service) -> None:
    new_leagues_data = [
        {
            "name": "Test Create League",
            "category": "MEN",
            "division": "A",
            "match_day": "SUN",
        },
        {
            "name": "Test Create League 2",
            "category": "WOMEN",
            "division": "B",
            "match_day": "MON",
        },
    ]

    _ = league_service.create_many(new_leagues_data)

    assert league_service.count() == 2
    clear_table(session, League)


def test_append_league_to_season(session, season_service, league_service) -> None:
    season_data = {
        "name": "SZNZ 2",
        "description": "I Want A Dog",
        "start_date": "2025-01-01",
    }
    league_data = {
        "name": "Songs 2",
        "category": "MEN",
        "division": "A",
        "match_day": "SUN",
    }

    season = season_service.create(data=season_data, auto_commit=True)
    league = league_service.create(data=league_data, auto_commit=True)

    season.leagues.append(league)

    season_service.update(season, auto_commit=True)

    new_season_call = season_service.get_one_or_none(name="SZNZ 2")
    assert new_season_call.leagues[0].name == "Songs 2"

    clear_table(session, League)
    clear_table(session, Season)


def test_delete_league(league_service) -> None:
    new_league = League(name="Test Delete League 2", category="MEN", division="A", match_day="SUN")
    test_league = league_service.create(new_league)
    league_service.delete(test_league.id)
    assert league_service.get_one_or_none(name="Test Delete League 2") is None
