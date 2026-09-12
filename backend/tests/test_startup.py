def test_fastapi_startup(client):
    """Test that the FastAPI application starts and serves root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Welcome to the SkillMatch API"
    assert "docs" in data
    assert "health" in data


def test_docs_and_openapi(client):
    """Verify OpenAPI documentation endpoints (/docs, /redoc, /openapi.json)."""
    docs_resp = client.get("/docs")
    assert docs_resp.status_code == 200

    redoc_resp = client.get("/redoc")
    assert redoc_resp.status_code == 200

    openapi_resp = client.get("/openapi.json")
    assert openapi_resp.status_code == 200
    spec = openapi_resp.json()
    assert spec["info"]["title"] == "SkillMatch API"
    assert "/api/health" in spec["paths"]
    assert "/api/opportunities" in spec["paths"]
    assert "/api/applications" in spec["paths"]
