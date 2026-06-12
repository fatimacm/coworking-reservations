from tests.helpers import create_authenticated_user

def test_create_valid_reservation(client, auth_headers):
    response = client.post(
        "/reservations",
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2030-06-10T08:00:00Z",
            "end_datetime": "2030-06-10T09:00:00Z"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["space_name"] == "meeting_room_a"
    

def test_allow_minimum_duration_exactly_30_minutes(client):
    headers = create_authenticated_user(client, prefix="min30")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_1",
            "start_datetime": "2030-06-25T08:00:00Z",
            "end_datetime": "2030-06-25T08:30:00Z"
        }
    )

    assert response.status_code == 201


def test_allow_reservation_until_closing_time(client):
    headers = create_authenticated_user(client, prefix="closing")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_2",
            "start_datetime": "2030-06-26T19:30:00Z",
            "end_datetime": "2030-06-26T20:00:00Z"
        }
    )

    assert response.status_code == 201


def test_reject_reservation_before_opening_time(client):
    headers = create_authenticated_user(client, prefix="beforeopen")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "desk_3",
            "start_datetime": "2030-06-27T07:59:00Z",
            "end_datetime": "2030-06-27T08:30:00Z"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Reservations cannot start before 08:00."


def test_reject_reservation_after_closing_time(client):
    headers = create_authenticated_user(client, prefix="afterclose")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2030-06-28T19:30:00Z",
            "end_datetime": "2030-06-28T20:01:00Z"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Reservations cannot end after 20:00."


def test_allow_maximum_duration_exactly_8_hours(client):
    headers = create_authenticated_user(client, prefix="max8")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "meeting_room_b",
            "start_datetime": "2030-06-29T08:00:00Z",
            "end_datetime": "2030-06-29T16:00:00Z"
        }
    )

    assert response.status_code == 201


def test_reject_duration_over_8_hours(client):
    headers = create_authenticated_user(client, prefix="over8")

    response = client.post(
        "/reservations",
        headers=headers,
        json={
            "space_name": "conference_hall",
            "start_datetime": "2030-06-30T08:00:00Z",
            "end_datetime": "2030-06-30T16:01:00Z"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Maximum reservation duration is 8 hours."