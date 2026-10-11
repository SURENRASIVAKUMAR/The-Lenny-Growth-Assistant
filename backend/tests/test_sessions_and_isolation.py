def test_session_lifecycle_and_isolation(client):
    # 1. Create Session A
    res_a = client.post("/api/sessions", json={"title": "Session Alpha"})
    assert res_a.status_code == 201
    session_a = res_a.json()
    id_a = session_a["id"]

    # 2. Create Session B
    res_b = client.post("/api/sessions", json={"title": "Session Beta"})
    assert res_b.status_code == 201
    session_b = res_b.json()
    id_b = session_b["id"]

    # 3. Add message to Session A
    msg_a = client.post(f"/api/sessions/{id_a}/messages", json={
        "role": "user",
        "content": "Message for Alpha"
    })
    assert msg_a.status_code == 201

    # 4. Add message to Session B
    msg_b = client.post(f"/api/sessions/{id_b}/messages", json={
        "role": "user",
        "content": "Message for Beta"
    })
    assert msg_b.status_code == 201

    # 5. Verify isolation: Session A only contains its own message
    list_a = client.get(f"/api/sessions/{id_a}/messages").json()
    assert len(list_a) == 1
    assert list_a[0]["content"] == "Message for Alpha"
    assert list_a[0]["session_id"] == id_a

    # Verify isolation: Session B only contains its own message
    list_b = client.get(f"/api/sessions/{id_b}/messages").json()
    assert len(list_b) == 1
    assert list_b[0]["content"] == "Message for Beta"
    assert list_b[0]["session_id"] == id_b

    # 6. Rename Session A
    patch_res = client.patch(f"/api/sessions/{id_a}", json={"title": "Renamed Alpha"})
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Renamed Alpha"

    # 7. Delete Session A
    del_res = client.delete(f"/api/sessions/{id_a}")
    assert del_res.status_code == 204

    # Session A messages should now be gone (cascade delete)
    get_a = client.get(f"/api/sessions/{id_a}")
    assert get_a.status_code == 404

    # Session B should remain intact
    get_b = client.get(f"/api/sessions/{id_b}")
    assert get_b.status_code == 200
    assert get_b.json()["title"] == "Session Beta"

    # Clean up Session B
    client.delete(f"/api/sessions/{id_b}")
