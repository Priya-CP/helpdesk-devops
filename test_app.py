from app import app, TICKETS


def setup_function():
    TICKETS.clear()


def test_home():
    assert app.test_client().get("/").status_code == 200


def test_create_ticket():
    client = app.test_client()
    response = client.post(
        "/new",
        data={"name": "Asha", "category": "Wi-Fi", "description": "Hostel Wi-Fi down"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Asha" in response.data
    assert b"Hostel Wi-Fi down" in response.data


def test_resolve_ticket():
    client = app.test_client()
    client.post(
        "/new",
        data={"name": "Ravi", "category": "Software", "description": "MATLAB error"},
    )
    response = client.post("/resolve/1", follow_redirects=True)
    assert b"Resolved" in response.data


def test_health():
    assert app.test_client().get("/health").get_json()["status"] == "ok"