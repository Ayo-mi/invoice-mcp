from collections.abc import Iterator
from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.models import Base
from app.db.repository import InvoiceRepository
from app.router import ToolRouter


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture
def seeded_session_factory(session_factory: sessionmaker[Session]) -> sessionmaker[Session]:
    session = session_factory()
    repo = InvoiceRepository(session)
    repo.add_invoice(
        user_id="user-1",
        vendor="Acme Corp",
        amount=100.0,
        invoice_date=date(2026, 4, 1),
        invoice_id="INV-100",
        currency="USD",
        raw_text="historical invoice",
    )
    repo.add_invoice(
        user_id="user-1",
        vendor="Acme Corp",
        amount=100.0,
        invoice_date=date(2026, 4, 5),
        invoice_id="INV-101",
        currency="USD",
        raw_text="historical invoice",
    )
    session.commit()
    session.close()
    return session_factory


@pytest.fixture
def router(session_factory: sessionmaker[Session]) -> ToolRouter:
    return ToolRouter(session_factory=session_factory)

