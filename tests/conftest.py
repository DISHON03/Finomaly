import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.user import User
from backend.app.models.account import Account
from backend.app.models.budget import Budget
from backend.app.models.transaction import Transaction
from backend.app.models.savings_goal import SavingsGoal
from backend.app.models.user_preference import UserPreference
from backend.app.utils.security import hash_password, create_access_token

# Use in-memory SQLite database for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db_engine():
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    user = User(
        email="testuser@finomaly.io",
        hashed_password=hash_password("password123"),
        full_name="Test Financial Analyst",
        is_demo=False
    )
    db.add(user)
    db.flush()
    pref = UserPreference(user_id=user.id, theme="dark", currency_symbol="$", monthly_savings_target_pct=20.0)
    db.add(pref)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user2(db):
    user = User(
        email="otheruser@finomaly.io",
        hashed_password=hash_password("password123"),
        full_name="Second Isolated User",
        is_demo=False
    )
    db.add(user)
    db.flush()
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_headers2(test_user2):
    token = create_access_token(data={"sub": str(test_user2.id), "email": test_user2.email})
    return {"Authorization": f"Bearer {token}"}
