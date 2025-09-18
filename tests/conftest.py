import pytest, jsonschema
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from main import app
from database.database import Base, get_db

SCHEMAS = {
    "Answer": {
        "type": "object",
        "required": ["id", "question_id", "user_id", "text", "created_at"],
        "properties": {
            "id": {"type": "integer"},
            "question_id": {"type": "integer"},
            "user_id": {"type": "integer"},
            "text": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
        },
        "additionalProperties": True,
    },
    "Question": {
        "type": "object",
        "required": ["id", "text", "created_at"],
        "properties": {
            "id": {"type": "integer"},
            "text": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
        },
        "additionalProperties": True,
    },
    "QuestionDetail": {
        "type": "object",
        "required": ["id", "text", "created_at", "answers"],
        "properties": {
            "id": {"type": "integer"},
            "text": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"},
            "answers": {
                "type": "array",
                "items": {"$ref": "#/defs/Answer"}
            },
        },
        "additionalProperties": True,
        "defs": {
            "Answer": {
                "type": "object",
                "required": ["id", "question_id", "user_id", "text", "created_at"],
                "properties": {
                    "id": {"type": "integer"},
                    "question_id": {"type": "integer"},
                    "user_id": {"type": "integer"},
                    "text": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
                "additionalProperties": True,
            }
        }
    },
    "QuestionList": {
        "type": "array",
        "items": {"$ref": "#/defs/Question"},
        "defs": {
            "Question": {
                "type": "object",
                "required": ["id", "text", "created_at"],
                "properties": {
                    "id": {"type": "integer"},
                    "text": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
                "additionalProperties": True,
            }
        }
    },
    "Error": {
        "type": "object",
        "properties": {"detail": {}},
        "required": ["detail"],
        "additionalProperties": True,
    },
}


@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )

    @event.listens_for(engine, "connect")
    def _fk_pragma_on(dbapi_conn, conn_record):
        cur = dbapi_conn.cursor()
        cur.execute("PRAGMA foreign_keys=ON")
        cur.close()

    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine):
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def assert_status(resp, *codes):
    assert resp.status_code in codes, f"status={resp.status_code}, expected in {codes}"

def validate_schema(obj, schema_name):
    jsonschema.validate(instance=obj, schema=SCHEMAS[schema_name])

@pytest.fixture
def api():
    class API:
        def __init__(self, client):
            self.client = client

        def mk_question(self, text="Q", expected_codes=(200, 201)):
            r = self.client.post("/questions", json={"text": text})
            assert_status(r, *expected_codes)
            return r.json()

        def add_answer(self, qid: int, user_id: int, text: str, expected_codes=(200, 201)):
            r = self.client.post(f"/answers/{qid}/answers", json={"user_id": user_id, "text": text})
            assert_status(r, *expected_codes)
            return r.json()

        def get(self, path, expected_codes=(200,)):
            r = self.client.get(path)
            assert_status(r, *expected_codes)
            return r.json() if r.content else None

        def delete(self, path, expected_codes=(204,)):
            r = self.client.delete(path)
            assert_status(r, *expected_codes)
            return None

        def validate(self, obj, schema_name):
            validate_schema(obj, schema_name)

    def _factory(client):
        return API(client)

    return _factory
