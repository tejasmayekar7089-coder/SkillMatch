from app.database.database import check_database_connection


def test_api_health_endpoint(client):
    """Test /api/health endpoint verifying both backend status and database connectivity."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


def test_database_connectivity_helper():
    """Test raw database connectivity function."""
    assert check_database_connection() is True
