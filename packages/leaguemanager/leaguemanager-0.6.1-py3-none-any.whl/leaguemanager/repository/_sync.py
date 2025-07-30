from advanced_alchemy.repository import (
    SQLAlchemySyncRepository,
    SQLAlchemySyncSlugRepository,
)

from leaguemanager import models

__all__ = [
    "FixtureTeamSyncRepository",
    "FixtureSyncRepository",
    "LeagueSyncRepository",
    "ManagerSyncRepository",
    "PlayerSyncRepository",
    "RefereeSyncRepository",
    "RoleSyncRepository",
    "ScheduleSyncRepository",
    "SeasonSyncRepository",
    "TeamSyncRepository",
    "StandingsSyncRepository",
    "UserRoleSyncRepository",
    "UserSyncRepository",
]


class FixtureTeamSyncRepository(SQLAlchemySyncRepository[models.FixtureTeam]):
    """FixtureTeam repository."""

    model_type = models.FixtureTeam


class FixtureSyncRepository(SQLAlchemySyncRepository[models.Fixture]):
    """Fixture repository."""

    model_type = models.Fixture


class LeagueSyncRepository(SQLAlchemySyncSlugRepository[models.League]):
    """League repository."""

    model_type = models.League


class ManagerSyncRepository(SQLAlchemySyncRepository[models.Manager]):
    """Manager repository."""

    model_type = models.Manager


class PlayerSyncRepository(SQLAlchemySyncRepository[models.Player]):
    """Player repository."""

    model_type = models.Player


class RefereeSyncRepository(SQLAlchemySyncRepository[models.Referee]):
    """Referee repository."""

    model_type = models.Referee


class RoleSyncRepository(SQLAlchemySyncSlugRepository[models.Role]):
    """Role repository."""

    model_type = models.Role


class ScheduleSyncRepository(SQLAlchemySyncRepository[models.Schedule]):
    """Schedule repository."""

    model_type = models.Schedule


class SeasonSyncRepository(SQLAlchemySyncSlugRepository[models.Season]):
    """Season repository."""

    model_type = models.Season


class StandingsSyncRepository(SQLAlchemySyncRepository[models.Standings]):
    """Standings repository."""

    model_type = models.Standings


class TeamSyncRepository(SQLAlchemySyncSlugRepository[models.Team]):
    """Team repository."""

    model_type = models.Team


class UserRoleSyncRepository(SQLAlchemySyncRepository[models.UserRole]):
    """UserRole repository."""

    model_type = models.UserRole


class UserSyncRepository(SQLAlchemySyncRepository[models.User]):
    """User repository."""

    model_type = models.User
