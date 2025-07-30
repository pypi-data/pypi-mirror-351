from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository,
    SQLAlchemyAsyncSlugRepository,
)

from leaguemanager import models

__all__ = [
    "FixtureTeamAsyncRepository",
    "FixtureAsyncRepository",
    "LeagueAsyncRepository",
    "ManagerAsyncRepository",
    "PlayerAsyncRepository",
    "RefereeAsyncRepository",
    "RoleAsyncRepository",
    "ScheduleAsyncRepository",
    "SeasonAsyncRepository",
    "StandingsAsyncRepository",
    "TeamAsyncRepository",
    "UserAsyncRepository",
    "UserRoleAsyncRepository",
]


class FixtureTeamAsyncRepository(SQLAlchemyAsyncRepository[models.FixtureTeam]):
    """FixtureTeam repository."""

    model_type = models.FixtureTeam


class FixtureAsyncRepository(SQLAlchemyAsyncRepository[models.Fixture]):
    """Fixture repository."""

    model_type = models.Fixture


class LeagueAsyncRepository(SQLAlchemyAsyncSlugRepository[models.League]):
    """League repository."""

    model_type = models.League


class ManagerAsyncRepository(SQLAlchemyAsyncRepository[models.Manager]):
    """Manager repository."""

    model_type = models.Manager


class PlayerAsyncRepository(SQLAlchemyAsyncRepository[models.Player]):
    """Player repository."""

    model_type = models.Player


class RefereeAsyncRepository(SQLAlchemyAsyncRepository[models.Referee]):
    """Referee repository."""

    model_type = models.Referee


class RoleAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Role]):
    """Role repository."""

    model_type = models.Role


class ScheduleAsyncRepository(SQLAlchemyAsyncRepository[models.Schedule]):
    """Schedule repository."""

    model_type = models.Schedule


class SeasonAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Season]):
    """Season repository."""

    model_type = models.Season


class StandingsAsyncRepository(SQLAlchemyAsyncRepository[models.Standings]):
    """Standings repository."""

    model_type = models.Standings


class TeamAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Team]):
    """Team repository."""

    model_type = models.Team


class UserRoleAsyncRepository(SQLAlchemyAsyncRepository[models.UserRole]):
    """UserRole repository."""

    model_type = models.UserRole


class UserAsyncRepository(SQLAlchemyAsyncRepository[models.User]):
    """User repository."""

    model_type = models.User
