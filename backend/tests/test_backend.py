import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.session import Base, get_db
from app.services import orders, tickets
from app.models.user import User
from app.models.order import Order

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    response = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login_user():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_order_services():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test@example.com").first()
    
    # Manually insert an order for testing
    order = Order(user_id=user.id, product_name="Test Product", status="shipped", tracking_number="TRK123")
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Test get_orders_by_user
    user_orders = orders.get_orders_by_user(db, user.id)
    assert len(user_orders) == 1
    
    # Test refund_order
    refunded_order = orders.refund_order(db, order.id)
    assert refunded_order.status == "refunded"

def test_ticket_services():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "test@example.com").first()
    
    # Test create_ticket
    ticket = tickets.create_ticket(db, user_id=user.id, issue="My product is broken")
    assert ticket.id is not None
    assert ticket.issue == "My product is broken"
    assert ticket.status == "open"
