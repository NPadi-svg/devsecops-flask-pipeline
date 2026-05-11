import pytest
from app.main import app, init_db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

def test_create_and_list_todo(client):
    r = client.post("/todos", json={"title": "Learn DevSecOps"})
    assert r.status_code == 201
    r = client.get("/todos")
    assert r.status_code == 200
    assert any(t["title"] == "Learn DevSecOps" for t in r.get_json())

def test_delete_todo(client):
    client.post("/todos", json={"title": "To delete"})
    todos = client.get("/todos").get_json()
    todo_id = todos[0]["id"]
    r = client.delete(f"/todos/{todo_id}")
    assert r.status_code == 200