from uuid import uuid4


def unique_email(prefix="user"):
    return f"{prefix}_{uuid4().hex[:8]}@example.com"


def unique_username(prefix="user"):
    return f"{prefix}_{uuid4().hex[:6]}"


def create_authenticated_user(
    client,
    prefix: str = "test",
    email: str | None = None,
    username: str | None = None,
    password: str = "testpass123"
):
    email = email or unique_email(prefix)
    username = username or unique_username(prefix)

    register_response = client.post("/register", json={
        "email": email,
        "username": username,
        "password": password
    })

    assert register_response.status_code == 201

    login_response = client.post("/login", data={
        "username": email,
        "password": password
    })

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }