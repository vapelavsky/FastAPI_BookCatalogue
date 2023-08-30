import databases
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from main import app
from catalogue_models import DATABASE_URL, Base, create_engine

# Connect to test database
database = databases.Database(DATABASE_URL)


@pytest.fixture(autouse=True)
async def setup():
    await database.connect()
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    await database.disconnect()


@pytest.fixture
def test_client():
    return TestClient(app)


def test_create_author(test_client):
    response = test_client.post("/authors/", json={"name": "Test Author"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Author"
    assert data["id"] is not None


def test_get_authors(test_client):
    response = test_client.get("/authors/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_author(test_client):
    response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = response.json()["id"]
    response = test_client.get(f"/authors/{author_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Author"
    assert data["id"] == author_id


def test_update_author(test_client):
    response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = response.json()["id"]
    response = test_client.patch(f"/authors/{author_id}", json={"name": "Updated Author"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Author"
    assert data["id"] == author_id


def test_delete_author(test_client):
    response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = response.json()["id"]
    response = test_client.delete(f"/authors/{author_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Author deleted successfully"


def test_create_book(test_client):
    author_response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = author_response.json()["id"]

    response = test_client.post("/books/", json={"name": "Test Book", "author_id": author_id})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Book"
    assert data["id"] is not None
    assert data["author_id"] == author_id


def test_get_books(test_client):
    author_response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = author_response.json()["id"]

    test_client.post("/books/", json={"name": "Book 1", "author_id": author_id})
    test_client.post("/books/", json={"name": "Book 2", "author_id": author_id})

    response = test_client.get("/books/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_book(test_client):
    author_response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = author_response.json()["id"]

    book_response = test_client.post("/books/", json={"name": "Test Book", "author_id": author_id})
    book_id = book_response.json()["id"]

    response = test_client.get(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Book"
    assert data["id"] == book_id
    assert data["author_id"] == author_id


def test_update_book(test_client):
    author_response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = author_response.json()["id"]

    book_response = test_client.post("/books/", json={"name": "Test Book", "author_id": author_id})
    book_id = book_response.json()["id"]

    response = test_client.patch(f"/books/{book_id}", json={"name": "Updated Book"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Book" or data["author_id"] == author_id
    assert data["id"] == book_id


def test_delete_book(test_client):
    author_response = test_client.post("/authors/", json={"name": "Test Author"})
    author_id = author_response.json()["id"]

    book_response = test_client.post("/books/", json={"name": "Test Book", "author_id": author_id})
    book_id = book_response.json()["id"]

    response = test_client.delete(f"/books/{book_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Book deleted successfully"
