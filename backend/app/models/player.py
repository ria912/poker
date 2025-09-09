# server/app/models/user.py
import uuid
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    is_ai: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # UserとGamePlayerのリレーションシップ
    # このユーザーが参加しているゲームの情報を参照できるようにする
    games = relationship("GamePlayer", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', is_ai={self.is_ai})>"
