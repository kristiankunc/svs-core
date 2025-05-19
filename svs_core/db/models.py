from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional


def utc_now():
    return datetime.now(timezone.utc)


Base = declarative_base()


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False)
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(
            timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False)


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class User(IDMixin, TimestampMixin, Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    ssh_keys: Mapped[list["SSHKey"]] = relationship("SSHKey", back_populates="user")

    @classmethod
    def create(cls, name: str, *, ssh_keys: Optional[list["SSHKey"]] = None) -> "User":
        user = cls()
        user.name = name
        user.ssh_keys = ssh_keys or []
        return user


class SSHKey(IDMixin, TimestampMixin, Base):
    __tablename__ = "ssh_key"

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(String(4096), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["User"] = relationship(
        "User", back_populates="ssh_keys", foreign_keys=[user_id])

    @classmethod
    def create(cls, name: str, content: str, user: "User") -> "SSHKey":
        ssh_key = cls()
        ssh_key.name = name
        ssh_key.content = content
        ssh_key.user = user
        return ssh_key
