from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Manager
from leaguemanager.repository import ManagerSyncRepository
from leaguemanager.repository._async import ManagerAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["ManagerSyncService", "ManagerAsyncService"]


class ManagerSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for managers."""

    repository_type = ManagerSyncRepository


class ManagerAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles database operations for managers."""

    repository_type = ManagerAsyncRepository
