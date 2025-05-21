# TODO: maybe remove type: ignore[misc] punishment for using DeclarativeBase
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import DeclarativeBase


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):  # type: ignore[misc]
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )


class IDMixin:
    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class UserModel(IDMixin, TimestampMixin, Base):
    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    ssh_keys: Mapped[list["UserModel"]] = relationship(
        "UserModel", back_populates="user"
    )

    @classmethod
    def create(
        cls, name: str, *, ssh_keys: Optional[list["UserModel"]] = None
    ) -> "UserModel":
        user = cls()
        user.name = name
        user.ssh_keys = ssh_keys or []
        return user


class SSHKeyModel(IDMixin, TimestampMixin, Base):
    __tablename__ = "ssh_key"

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    content: Mapped[str] = mapped_column(String(4096), nullable=False)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="ssh_keys", foreign_keys=[user_id]
    )

    @classmethod
    def create(cls, name: str, content: str, user_id: int) -> "SSHKeyModel":
        ssh_key = cls()
        ssh_key.name = name
        ssh_key.content = content
        ssh_key.user_id = user_id
        return ssh_key
