from s_usd_service.config import get_settings


def test_health(client):
    settings = get_settings()
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": settings.service_name,
        "version": settings.service_version
    }