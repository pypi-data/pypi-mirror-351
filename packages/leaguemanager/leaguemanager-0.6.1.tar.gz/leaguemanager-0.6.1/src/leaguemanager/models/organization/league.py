from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata
from leaguemanager.models.enums import Category, Division, MatchDay

if TYPE_CHECKING:
    from .schedule import Schedule
    from .season import Season
    from .team import Team


@define(slots=False)
class League(UUIDAuditBase):
    """Defines a league with certain rules, as well as divisions and categories.

    TODO: Add a way to create custom ruleset that applies to league."""

    season_id: UUID | None = field(default=None)

    active: bool = field(default=True)
    category: Category | None = field(
        default=None, validator=validators.optional(validators.in_([v.name for v in Category]))
    )
    division: Division | None = field(
        default=None, validator=validators.optional(validators.in_([v.name for v in Division]))
    )
    match_day: MatchDay | None = field(
        default=None, validator=validators.optional(validators.in_([v.name for v in MatchDay]))
    )

    name: str | None = field(default=None, validator=validators.max_len(80))
    team_size: int | None = field(default=11)

    age_rule: bool = field(default=False)
    age_rule_min: int | None = field(default=None)
    age_rule_max: int | None = field(default=None)

    m_age_rule_min: int | None = field(default=None)
    m_age_rule_max: int | None = field(default=None)
    f_age_rule_min: int | None = field(default=None)
    f_age_rule_max: int | None = field(default=None)

    # season: "Season" | None = field(default=None)


# SQLAlchemy Imperative Mapping

league = Table(
    "league",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id")),
    Column("name", String(80), nullable=False, unique=True),
    Column("category", String(20), nullable=True),
    Column("division", String(20), nullable=True),
    Column("match_day", String(20), nullable=True),
    Column("team_size", Integer, nullable=True),
    Column("active", Boolean, nullable=False),
    Column("age_rule", Boolean, nullable=False),
    Column("age_rule_min", Integer, nullable=True),
    Column("age_rule_max", Integer, nullable=True),
    Column("m_age_rule_min", Integer, nullable=True),
    Column("m_age_rule_max", Integer, nullable=True),
    Column("f_age_rule_min", Integer, nullable=True),
    Column("f_age_rule_max", Integer, nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    League,
    league,
    properties={
        "season": relationship("Season", back_populates="leagues", lazy="selectin"),
        "schedule": relationship("Schedule", back_populates="league", uselist=False, lazy="selectin"),
        "teams": relationship("Team", back_populates="league", lazy="selectin"),
    },
)
