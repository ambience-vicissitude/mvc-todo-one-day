from tests.conftest import make_user

# TRIMMED: service and repository unit tests; these API tests exercise all layers end to end.


def test_task_crud_lifecycle(client):
    alice = make_user(client, "alice")

    created = client.post("/api/tasks", json={"title": "Write README"}, headers=alice)
    assert created.status_code == 201
    task = created.json()
    assert task["status"] == "todo"

    updated = client.patch(f"/api/tasks/{task['id']}", json={"status": "doing"}, headers=alice)
    assert updated.status_code == 200
    assert updated.json()["status"] == "doing"
    assert updated.json()["title"] == "Write README"

    assert client.get("/api/tasks", headers=alice).json()[0]["id"] == task["id"]
    assert client.delete(f"/api/tasks/{task['id']}", headers=alice).status_code == 204
    assert client.get("/api/tasks", headers=alice).json() == []


def test_users_cannot_see_or_change_each_others_tasks(client):
    alice = make_user(client, "alice")
    bob = make_user(client, "bob")
    task_id = client.post("/api/tasks", json={"title": "private"}, headers=alice).json()["id"]

    assert client.get("/api/tasks", headers=bob).json() == []
    assert client.get(f"/api/tasks/{task_id}", headers=bob).status_code == 404
    assert client.delete(f"/api/tasks/{task_id}", headers=bob).status_code == 404


def test_filter_by_status(client):
    alice = make_user(client, "alice")
    client.post("/api/tasks", json={"title": "a"}, headers=alice)
    client.post("/api/tasks", json={"title": "b", "status": "done"}, headers=alice)

    done = client.get("/api/tasks", params={"status": "done"}, headers=alice).json()
    assert [t["title"] for t in done] == ["b"]


def test_rejects_past_due_date_and_blank_title(client):
    alice = make_user(client, "alice")

    past = client.post("/api/tasks", json={"title": "x", "due_date": "2000-01-01"}, headers=alice)
    assert past.status_code == 422
    blank = client.post("/api/tasks", json={"title": "   "}, headers=alice)
    assert blank.status_code == 422


def test_requires_known_user(client):
    assert client.get("/api/tasks").status_code == 401
    assert client.get("/api/tasks", headers={"X-User-Id": "999"}).status_code == 401


def test_duplicate_user_name_conflicts(client):
    make_user(client, "alice")
    assert client.post("/api/users", json={"name": "alice"}).status_code == 409


def test_health_endpoints(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    assert client.get("/api/health/ready").json() == {"status": "ready"}
