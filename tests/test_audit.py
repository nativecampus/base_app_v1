from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import set_current_user, _current_user_var, AuditMixin, Base


class _DummyModel(AuditMixin, Base):
    __tablename__ = "_test_audit_dummy"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


async def test_audit_mixin_sets_created_by(db):
    token = set_current_user("alice")
    try:
        obj = _DummyModel(name="test")
        db.add(obj)
        await db.flush()
        assert obj.created_by == "alice"
        assert obj.updated_by == "alice"
    finally:
        _current_user_var.reset(token)


async def test_audit_mixin_defaults_to_system(db):
    obj = _DummyModel(name="test2")
    db.add(obj)
    await db.flush()
    assert obj.created_by == "system"


async def test_audit_created_at_is_set(db):
    obj = _DummyModel(name="test3")
    db.add(obj)
    await db.flush()
    assert obj.created_at is not None
    assert obj.updated_at is not None
