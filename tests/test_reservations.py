from tests.helpers import create_authenticated_user


def test_create_reservation(client):
    headers = create_authenticated_user(client, "reserve")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2030-06-10T08:00:00Z",
            "end_datetime": "2030-06-10T10:00:00Z"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["space_name"] == "meeting_room_a"
    assert data["status"] == "active"


def test_get_my_reservations(client):
    headers = create_authenticated_user(client, "getres")

    reservations = [
        {
            "space_name": "desk_1",
            "start_datetime": "2030-06-11T08:00:00Z",
            "end_datetime": "2030-06-11T09:00:00Z"
        },
        {
            "space_name": "desk_1",
            "start_datetime": "2030-06-12T08:00:00Z",
            "end_datetime": "2030-06-12T09:00:00Z"
        }
    ]

    for reservation in reservations:
        response = client.post(
            "/reservations",
            headers=headers,
            json=reservation
        )
        assert response.status_code == 201

    response = client.get("/reservations", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_reservation(client):
    headers = create_authenticated_user(client, "update")

    create_response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2030-06-13T08:00:00Z",
            "end_datetime": "2030-06-13T09:00:00Z"
        }
    )

    assert create_response.status_code == 201
    reservation_id = create_response.json()["id"]

    response = client.put(
        f"/reservations/{reservation_id}",
        headers=headers,
        json={
            "space_name": "meeting_room_b"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["space_name"] == "meeting_room_b"


def test_cancel_reservation(client):
    headers = create_authenticated_user(client, "cancel")

    create_response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "conference_hall",
            "start_datetime": "2030-06-14T08:00:00Z",
            "end_datetime": "2030-06-14T10:00:00Z"
        }
    )

    assert create_response.status_code == 201
    reservation_id = create_response.json()["id"]

    response = client.delete(
        f"/reservations/{reservation_id}",
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"

    active_reservations = client.get(
        "/reservations",
        headers=headers
    )

    assert active_reservations.status_code == 200
    assert len(active_reservations.json()) == 0

    with_cancelled = client.get(
        "/reservations?include_cancelled=true",
        headers=headers
    )

    assert with_cancelled.status_code == 200
    assert len(with_cancelled.json()) == 1


def test_user_cannot_access_other_user_reservation(client):
    headers1 = create_authenticated_user(client, "user1")

    create_response = client.post(
        "/reservations",
        headers=headers1,
        json={
            "space_name": "desk_1",
            "start_datetime": "2030-06-15T08:00:00Z",
            "end_datetime": "2030-06-15T09:00:00Z"
        }
    )

    assert create_response.status_code == 201
    reservation_id = create_response.json()["id"]

    headers2 = create_authenticated_user(client, "user2")

    response = client.get(
        f"/reservations/{reservation_id}",
        headers=headers2
    )

    assert response.status_code == 404