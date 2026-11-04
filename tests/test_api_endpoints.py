import pytest
import os
import sys
from fastapi.testclient import TestClient

# Ensure services/anomaly-detector is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "anomaly-detector")))

# Set mock mode before importing index
os.environ["MOCK_MODE"] = "true"
from index import app

client = TestClient(app)

class TestAnomalyDetectorAPI:
    def test_health_check_endpoint(self):
        """GET / returns 200 OK and status UP."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "UP"
        assert "online" in data["message"]

    def test_predict_billing_normal_payload(self):
        """POST /predict processes normal cost without internal server errors."""
        payload = {
            "provider": "azure",
            "accountId": "sub-987654",
            "serviceName": "Virtual Machines",
            "costUsd": 45.50,
            "region": "eastus",
            "usageAmount": 100.0,
            "usageUnit": "Hours"
        }
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["provider"] == "azure"
        assert data["serviceName"] == "Virtual Machines"
        assert "prediction" in data
        assert "is_anomaly" in data["prediction"]

    def test_predict_billing_spike_alert_generation(self):
        """POST /predict handles extreme cost spike and triggers alert dispatch path."""
        # Baseline calls
        for cost in [10.0, 11.0, 10.5, 12.0, 11.5]:
            client.post("/predict", json={
                "provider": "aws",
                "accountId": "acc-112233",
                "serviceName": "DynamoDB",
                "costUsd": cost
            })
            
        # Extreme spike
        response = client.post("/predict", json={
            "provider": "aws",
            "accountId": "acc-112233",
            "serviceName": "DynamoDB",
            "costUsd": 4200.00
        })
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"]["is_anomaly"] is True

    def test_predict_server_ssh_intrusion_alert(self):
        """POST /predict/server detects SSH brute-force attack and formats alert correctly."""
        # Baseline calls
        for _ in range(5):
            client.post("/predict/server", json={
                "provider": "aws",
                "hostname": "auth-gateway-01",
                "cpuUtilization": 25.0,
                "ramUtilization": 45.0,
                "sshAuthFailures": 0
            })
            
        # Attack payload
        response = client.post("/predict/server", json={
            "provider": "aws",
            "hostname": "auth-gateway-01",
            "cpuUtilization": 32.0,
            "ramUtilization": 48.0,
            "sshAuthFailures": 35
        })
        assert response.status_code == 200
        data = response.json()
        pred = data["prediction"]
        assert pred["is_threat"] is True
        assert pred["threat_type"] == "ssh_brute_force"

    def test_invalid_payload_validation(self):
        """Malformed requests should be rejected with 422 Unprocessable Entity."""
        response = client.post("/predict", json={"invalidField": "corrupted"})
        assert response.status_code == 422
