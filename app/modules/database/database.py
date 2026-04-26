from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.env import settings


class Base(DeclarativeBase):
    pass


def get_sqlite_file_path() -> Path | None:
    database_url = settings.DATABASE_URL

    if not database_url.startswith("sqlite:///"):
        return None

    raw_path = database_url.replace("sqlite:///", "", 1)
    return Path(raw_path).resolve()


sqlite_file_path = get_sqlite_file_path()

if sqlite_file_path is not None:
    sqlite_file_path.parent.mkdir(parents=True, exist_ok=True)


connect_args = {}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}


engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
)


def init_db() -> None:
    from app.modules.database import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    from app.modules.database.models import (
        ConversationModel,
        CustomerModel,
        InventoryItemModel,
        InventoryMovementModel,
        LeadModel,
        MessageModel,
        QuoteDraftModel,
        QuoteModel,
        TicketModel,
    )

    with SessionLocal() as session:
        session.query(InventoryMovementModel).delete()
        session.query(InventoryItemModel).delete()
        session.query(QuoteModel).delete()
        session.query(QuoteDraftModel).delete()
        session.query(LeadModel).delete()
        session.query(TicketModel).delete()
        session.query(MessageModel).delete()
        session.query(ConversationModel).delete()
        session.query(CustomerModel).delete()
        session.commit()
