from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Account(Base):
    __tablename__ = "account_v1"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    ident: Mapped[str] = mapped_column(String(8), unique=True)
    created_at: Mapped[int] = mapped_column()

    cultivation: Mapped[float] = mapped_column(default=0)
    spirit_stone: Mapped[int] = mapped_column(default=0)


class Practice(Base):
    __tablename__ = "practice_v1"
    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("account_v1.user_id"))
    start_at: Mapped[int] = mapped_column()
    end_at: Mapped[int] = mapped_column(nullable=True)


class SignIn(Base):
    __tablename__ = "sign_in_v1"
    ID: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("account_v1.user_id"))
    day: Mapped[int] = mapped_column()
    luck: Mapped[int] = mapped_column()


db = SQLAlchemy(model_class=Base)
