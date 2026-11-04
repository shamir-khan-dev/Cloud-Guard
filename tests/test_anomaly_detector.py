import pytest
import os
import sys

# Ensure services/anomaly-detector is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "anomaly-detector")))

from app.model import AnomalyDetectorModel

@pytest.fixture
def fresh_model():
    """Returns an isolated instance of AnomalyDetectorModel for deterministic tests."""
    return AnomalyDetectorModel()

class TestBillingAnomalyDetector:
    def test_normal_cost_does_not_trigger_anomaly(self, fresh_model):
        """Gradual normal costs should not be flagged as critical spend spikes."""
        provider = "aws"
        service = "EC2"
        
        # Seed baseline history around $30 - $40
        for cost in [32.0, 35.5, 33.0, 34.2, 36.0, 33.8]:
            res = fresh_model.predict(provider, service, cost)
            
        assert not res["is_anomaly"], "Normal baseline variance should not trigger anomaly alert."
        assert res["expected_cost"] > 0
        assert res["actual_cost"] == 33.8

    def test_massive_cost_spike_triggers_anomaly(self, fresh_model):
        """A sudden 40x cost surge should be flagged as an anomaly with elevated anomaly score."""
        provider = "aws"
        service = "S3"
        
        # Establish stable baseline
        for cost in [10.0, 12.0, 11.5, 10.5, 11.0, 12.5]:
            fresh_model.predict(provider, service, cost)
            
        # Inject anomalous spike ($1,850 vs ~$11 average)
        res = fresh_model.predict(provider, service, 1850.0)
        
        assert res["is_anomaly"] is True, "Massive cost spike must be detected as anomaly."
        assert res["actual_cost"] == 1850.0
        assert res["anomaly_score"] > 0.5, "Anomaly score should reflect anomalous severity."

    def test_cost_reduction_not_flagged_as_threat(self, fresh_model):
        """A drop in costs (e.g. server shutdown) should not be treated as a negative financial threat."""
        provider = "gcp"
        service = "BigQuery"
        
        # Establish baseline around $500
        for cost in [500.0, 520.0, 490.0, 510.0, 505.0]:
            fresh_model.predict(provider, service, cost)
            
        # Cost drops to $20
        res = fresh_model.predict(provider, service, 20.0)
        assert res["is_anomaly"] is False, "Cost reduction below average should not trigger negative anomaly."


class TestServerHealthAndSecurityAnomalyDetector:
    def test_normal_server_telemetry_healthy(self, fresh_model):
        """Normal operational metrics (CPU 35%, RAM 55%, SSH 0) should report healthy."""
        provider = "aws"
        hostname = "prod-api-worker-01"
        
        # Send normal telemetry
        for _ in range(6):
            res = fresh_model.predict_server(provider, hostname, cpu=36.0, ram=54.0, ssh=0)
            
        assert not res["is_threat"], "Healthy server metrics should not be flagged as threat."
        assert res["threat_type"] == "none"

    def test_ssh_brute_force_attack_detection(self, fresh_model):
        """Spike in failed SSH logins must trigger an immediate ssh_brute_force threat alert."""
        provider = "aws"
        hostname = "bastion-host-01"
        
        # Normal baseline
        for _ in range(6):
            fresh_model.predict_server(provider, hostname, cpu=20.0, ram=40.0, ssh=0)
            
        # Attacker executes dictionary attack: 28 failed SSH attempts in 60s window
        res = fresh_model.predict_server(provider, hostname, cpu=28.0, ram=42.0, ssh=28)
        
        assert res["is_anomaly"] is True, "SSH spike must be detected as anomalous."
        assert res["is_threat"] is True, "SSH spike must be flagged as active threat."
        assert res["threat_type"] == "ssh_brute_force", "Threat type must be categorized as ssh_brute_force."
        assert res["metrics"]["ssh_failures"] == 28

    def test_extreme_cpu_exhaustion_detection(self, fresh_model):
        """Severe CPU utilization spike (e.g., runaway crypto-miner) must trigger cpu_utilization_spike threat."""
        provider = "gcp"
        hostname = "compute-node-42"
        
        # Normal baseline (CPU ~30%)
        for _ in range(6):
            fresh_model.predict_server(provider, hostname, cpu=32.0, ram=50.0, ssh=0)
            
        # Sudden CPU saturation to 98.5%
        res = fresh_model.predict_server(provider, hostname, cpu=98.5, ram=88.0, ssh=0)
        
        assert res["is_anomaly"] is True
        assert res["is_threat"] is True
        assert res["threat_type"] == "cpu_utilization_spike"
        assert res["metrics"]["cpu"] == 98.5

