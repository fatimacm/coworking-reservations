def create_authenticated_user(client, email, username):
    client.post("/register", json={
        "email": email,
        "username": username,
        "password": "testpass123"
    })

    login = client.post("/login", data={
        "username": email,
        "password": "testpass123"
    })

    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_reject_overlap_same_space_different_user(client):
    headers_user_1 = create_authenticated_user(
        client,
        "space1@example.com",
        "spaceuser1"
    )

    headers_user_2 = create_authenticated_user(
        client,
        "space2@example.com",
        "spaceuser2"
    )

    first = client.post(
        "/reservations",
        headers=headers_user_1,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-20T10:00:00Z",
            "end_datetime": "2026-06-20T12:00:00Z"
        }
    )

    assert first.status_code == 201

    second = client.post(
        "/reservations",
        headers=headers_user_2,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-20T11:00:00Z",
            "end_datetime": "2026-06-20T13:00:00Z"
        }
    )

    assert second.status_code == 409
    assert second.json()["detail"] == "This space is already reserved during the selected time range."


def test_reject_overlap_same_user_different_space(client):
    headers = create_authenticated_user(
        client,
        "sameuser@example.com",
        "sameuser"
    )

    first = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-21T10:00:00Z",
            "end_datetime": "2026-06-21T12:00:00Z"
        }
    )

    assert first.status_code == 201

    second = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_b",
            "start_datetime": "2026-06-21T11:00:00Z",
            "end_datetime": "2026-06-21T13:00:00Z"
        }
    )

    assert second.status_code == 409
    assert second.json()["detail"] == "User already has another reservation during the selected time range."
    
    
def test_allow_consecutive_reservations(client):
    headers = create_authenticated_user(
        client,
        "consecutive@example.com",
        "consecutiveuser"
    )

    first = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-22T08:00:00Z",
            "end_datetime": "2026-06-22T12:00:00Z"
        }
    )

    assert first.status_code == 201

    second = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-22T12:00:00Z",
            "end_datetime": "2026-06-22T16:00:00Z"
        }
    )

    assert second.status_code == 201


def test_reject_daily_reservation_limit_exceeded(client):
    headers = create_authenticated_user(
        client,
        "daily@example.com",
        "dailyuser"
    )

    first = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_1",
            "start_datetime": "2026-06-23T08:00:00Z",
            "end_datetime": "2026-06-23T12:00:00Z"
        }
    )

    assert first.status_code == 201

    second = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_1",
            "start_datetime": "2026-06-23T14:00:00Z",
            "end_datetime": "2026-06-23T18:00:00Z"
        }
    )

    assert second.status_code == 201

    third = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_2",
            "start_datetime": "2026-06-23T18:00:00Z",
            "end_datetime": "2026-06-23T19:00:00Z"
        }
    )

    assert third.status_code == 409
    assert third.json()["detail"] == (
        "Daily reservation limit exceeded. Users cannot reserve more than 8 hours per day."
    )


def test_cancelled_reservations_do_not_count_toward_daily_limit(client):
    headers = create_authenticated_user(
        client,
        "cancelledlimit@example.com",
        "cancelledlimituser"
    )

    first = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "conference_hall",
            "start_datetime": "2026-06-24T08:00:00Z",
            "end_datetime": "2026-06-24T12:00:00Z"
        }
    )

    assert first.status_code == 201
    reservation_id = first.json()["id"]

    cancel_response = client.delete(
        f"/reservations/{reservation_id}",
        headers=headers
    )

    assert cancel_response.status_code == 200

    second = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "conference_hall",
            "start_datetime": "2026-06-24T12:00:00Z",
            "end_datetime": "2026-06-24T20:00:00Z"
        }
    )

    assert second.status_code == 201    