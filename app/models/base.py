from contextvars import ContextVar
from datetime import datetime, timezone

from sqlalchemy import DateTime, event, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


_current_user_var: ContextVar[str] = ContextVar("current_user", default="system")


def set_current_user(user: str):
    """Set the current user for audit columns. Returns a token for reset."""
    return _current_user_var.set(user)


def _current_user():
    """Return the current user from the context var for column defaults."""
    return _current_user_var.get()


class Base(DeclarativeBase):
    pass


class AuditMixin:
    """Mixin that adds created/updated audit columns to any model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_by: Mapped[str] = mapped_column(String(100), default=_current_user)
    updated_by: Mapped[str] = mapped_column(String(100), default=_current_user)


@event.listens_for(Base, "before_update", propagate=True)
def _set_updated_by(mapper, connection, target):
    """Set updated_by to the current user before any AuditMixin update."""
    if isinstance(target, AuditMixin):
        target.updated_by = _current_user_var.get()
