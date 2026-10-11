from backend.app.services.agent.orchestrator import extract_artifact

def test_artifact_crud(client):
    # 1. Create session for artifact
    s_res = client.post("/api/sessions", json={"title": "Artifact Session"})
    s_id = s_res.json()["id"]

    # 2. Create artifact
    art_payload = {
        "session_id": s_id,
        "title": "PLG Growth Loop Diagram",
        "artifact_type": "markdown",
        "content": "# Product Led Growth Loop\n1. Sign up\n2. Collaborate\n3. Invite peer",
    }
    create_res = client.post("/api/artifacts", json=art_payload)
    assert create_res.status_code == 201
    art_data = create_res.json()
    art_id = art_data["id"]
    assert art_data["title"] == "PLG Growth Loop Diagram"

    # 3. Retrieve artifact
    get_res = client.get(f"/api/artifacts/{art_id}")
    assert get_res.status_code == 200
    assert get_res.json()["content"] == art_payload["content"]

    # 4. Filter by session_id
    list_res = client.get(f"/api/artifacts?session_id={s_id}")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 5. Update artifact
    patch_res = client.patch(f"/api/artifacts/{art_id}", json={
        "title": "Updated PLG Loop",
        "content": "# Updated Content"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["title"] == "Updated PLG Loop"

    # 6. Delete artifact
    del_res = client.delete(f"/api/artifacts/{art_id}")
    assert del_res.status_code == 204

    # 7. Clean up session
    client.delete(f"/api/sessions/{s_id}")

def test_extract_artifact_parser():
    sample_llm_output = """Here is the breakdown you requested:

<<<ARTIFACT:ESSAY:title="The Law of Activation">>>
# The Law of Activation
Activation is the single most critical inflection point in the customer journey.
<<<END_ARTIFACT>>>

Let me know if you would like me to adjust any sections!"""

    artifact_data, cleaned_text = extract_artifact(sample_llm_output)
    assert artifact_data is not None
    assert artifact_data.title == "The Law of Activation"
    assert artifact_data.artifact_type == "essay"
    assert "# The Law of Activation" in artifact_data.content
    assert "Created artifact: **The Law of Activation**" in cleaned_text
