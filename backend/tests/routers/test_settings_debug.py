"""
Tests for settings_debug router

Tests health checks, API settings management, and debug endpoints
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestHealthEndpoints:
    """Test health check and root endpoints"""

    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint returns API information"""
        response = test_client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "Gun Del Sol API"
        assert data["version"] == "2.0.0"
        assert "endpoints" in data
        assert "health" in data["endpoints"]

    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "FastAPI Gun Del Sol (Modular)"
        assert data["version"] == "2.0.0"
        assert data["architecture"] == "modular"
        assert data["endpoints"] == 46
        assert "websocket_connections" in data


@pytest.mark.unit
class TestDebugEndpoints:
    """Test debug configuration endpoints"""

    def test_get_debug_mode(self, test_client: TestClient):
        """Test getting debug mode status"""
        response = test_client.get("/api/debug-mode")
        assert response.status_code == 200

        data = response.json()
        assert "debug_mode" in data
        assert isinstance(data["debug_mode"], bool)

    def test_get_debug_config(self, test_client: TestClient):
        """Test getting debug config for frontend"""
        response = test_client.get("/api/debug/config")
        assert response.status_code == 200

        data = response.json()
        assert "debug" in data
        assert data["debug"] in ["true", "false"]


@pytest.mark.unit
class TestAPISettings:
    """Test API settings management"""

    def test_get_api_settings(self, test_client: TestClient):
        """Test retrieving API settings"""
        response = test_client.get("/api/settings")
        assert response.status_code == 200

        data = response.json()
        assert "transactionLimit" in data
        assert "minUsdFilter" in data
        assert "walletCount" in data
        assert "apiRateDelay" in data
        assert "maxCreditsPerAnalysis" in data
        assert "maxRetries" in data
        assert "maxWalletsToStore" in data

        # Check default values
        assert data["transactionLimit"] >= 1
        assert data["minUsdFilter"] >= 0
        assert data["walletCount"] >= 1

    def test_update_api_settings(self, test_client: TestClient):
        """Test updating API settings"""
        new_settings = {
            "transactionLimit": 1000,
            "walletCount": 20,
            "minUsdFilter": 100.0
        }

        response = test_client.post("/api/settings", json=new_settings)
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "success"
        assert "settings" in data

        settings = data["settings"]
        assert settings["transactionLimit"] == 1000
        assert settings["walletCount"] == 20
        assert settings["minUsdFilter"] == 100.0

    def test_update_settings_with_invalid_values(self, test_client: TestClient):
        """Test updating settings with invalid values"""
        invalid_settings = {
            "transactionLimit": -1,  # Should be >= 1
        }

        response = test_client.post("/api/settings", json=invalid_settings)
        assert response.status_code == 422  # Validation error

    def test_update_settings_empty_payload(self, test_client: TestClient):
        """Test updating settings with empty payload"""
        response = test_client.post("/api/settings", json={})
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "noop"
        assert "settings" in data

    def test_settings_persistence(self, test_client: TestClient):
        """Test that settings persist across requests"""
        # Update settings
        new_settings = {"walletCount": 15}
        response = test_client.post("/api/settings", json=new_settings)
        assert response.status_code == 200

        # Retrieve settings
        response = test_client.get("/api/settings")
        assert response.status_code == 200

        data = response.json()
        assert data["walletCount"] == 15

    def test_update_all_settings(self, test_client: TestClient):
        """Test updating all settings at once"""
        all_settings = {
            "transactionLimit": 750,
            "minUsdFilter": 75.0,
            "walletCount": 25,
            "apiRateDelay": 150,
            "maxCreditsPerAnalysis": 1500,
            "maxRetries": 5
        }

        response = test_client.post("/api/settings", json=all_settings)
        assert response.status_code == 200

        data = response.json()
        settings = data["settings"]

        assert settings["transactionLimit"] == 750
        assert settings["minUsdFilter"] == 75.0
        assert settings["walletCount"] == 25
        assert settings["apiRateDelay"] == 150
        assert settings["maxCreditsPerAnalysis"] == 1500
        assert settings["maxRetries"] == 5