from sqlalchemy import inspect

from app.modules.database.database import engine, get_sqlite_file_path, init_db
from app.modules.tools.internal_store import InternalPersistentStore, internal_store


def test_sqlite_database_file_and_tables_exist():
    init_db()

    sqlite_path = get_sqlite_file_path()

    assert sqlite_path is not None
    assert sqlite_path.exists()

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    assert "conversations" in table_names
    assert "messages" in table_names
    assert "leads" in table_names
    assert "tickets" in table_names
    assert "quote_drafts" in table_names


def test_internal_store_persists_data_in_sqlite_between_instances():
    internal_store.reset()

    conversation = internal_store.upsert_conversation(
        customer_id="cliente_sqlite",
        channel="web",
        last_intent="cotizacion_mayoreo",
    )

    internal_store.create_message(
        conversation_id=conversation.id,
        role="user",
        content="Quiero 50 frascos de miel de maguey",
    )

    internal_store.create_lead(
        conversation_id=conversation.id,
        customer_id="cliente_sqlite",
        product_id="miel_maguey",
        quantity=50,
        customer_type="mayoreo",
        priority="media",
        missing_data=[],
    )

    another_store = InternalPersistentStore()

    conversations = another_store.list_conversations()
    messages = another_store.list_messages()
    leads = another_store.list_leads()

    assert len(conversations) == 1
    assert len(messages) == 1
    assert len(leads) == 1

    assert conversations[0].customer_id == "cliente_sqlite"
    assert messages[0].content == "Quiero 50 frascos de miel de maguey"
    assert leads[0].product_id == "miel_maguey"
    assert leads[0].quantity == 50

    internal_store.reset()
