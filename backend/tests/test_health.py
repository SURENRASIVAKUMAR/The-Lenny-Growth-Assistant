def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert "database" in data
    assert data["database"]["database_name"] == "lenny_growth_assistant"
    assert data["database"]["status"] == "connected"
    assert "active_provider" in data

def test_config_status_endpoint(client):
    response = client.get("/api/config/status")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data
    assert "database_status" in data
    assert data["database_status"] == "connected"
    assert data["rag_sources_count"] >= 4
    assert data["rag_chunks_count"] >= 20
