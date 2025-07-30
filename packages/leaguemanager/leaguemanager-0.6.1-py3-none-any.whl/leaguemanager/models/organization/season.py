from datetime import UTC, datetime

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, String, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

if TYPE_CHECKING:
    from .league import League


@define(slots=False)
class Season(UUIDAuditBase):
    """A season defines an overall period of time in which a league or leagues are active."""

    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(120)))
    active: bool = field(default=True)
    start_date: str | None = field(default=None)
    end_date: str | None = field(default=None)

    # leagues: list["League"] = field(default=list)


# SQLAlchemy Imperative Mappings

season = Table(
    "season",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column(
        "name",
        String(80),
        nullable=False,
        unique=True,
    ),
    Column("description", String(120), nullable=True),
    Column("active", Boolean, default=True),
    Column("start_date", String(10), nullable=True, default=None),
    Column("end_date", DateTime(), nullable=True, default=None),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Season,
    season,
    properties={
        "leagues": relationship("League", back_populates="season", lazy="selectin"),
        "schedules": relationship("Schedule", back_populates="season"),
    },
)
