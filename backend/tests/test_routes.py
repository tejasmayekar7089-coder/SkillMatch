from fastapi.testclient import TestClient


def test_prepared_routes_mounted(client: TestClient):
    """Verify all prepared /api/* router prefixes are mounted and respond."""
    endpoints = [
        ("/api/health", 200),
        ("/api/opportunities", 200),
        ("/api/recommendations", 200),
        ("/api/skill-gap", 200),
        ("/api/resume/status", 200),
        ("/api/dashboard/metrics", 200),
        # Protected endpoints require auth and return 401 when unauthenticated
        ("/api/auth/me", 401),
        ("/api/profile", 401),
        ("/api/saved", 401),
        ("/api/applications", 401),
        ("/api/notifications", 401),
        ("/api/admin/stats", 401),
    ]

    for path, expected_status in endpoints:
        resp = client.get(path)
        assert resp.status_code == expected_status, f"Route {path} returned {resp.status_code}, expected {expected_status}"
