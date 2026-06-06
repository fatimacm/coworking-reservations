def test_create_valid_reservation(client, auth_headers):
    response = client.post(
        "/reservations",
        json={
            "space_name": "meeting_room_a",
            "start_datetime": "2026-06-10T08:00:00Z",
            "end_datetime": "2026-06-10T09:00:00Z"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["space_name"] == "meeting_room_a"