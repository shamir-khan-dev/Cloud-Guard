from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.model import detector
import json
import os
import threading
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-main")

app = FastAPI(title="CloudGuard Anomaly Detector API")

class CostMetricPayload(BaseModel):
    provider: str
    accountId: str
    serviceName: str
    costUsd: float
    region: str = "us-east-1"
    usageAmount: float = 0.0
    usageUnit: str = "Units"

class ServerMetricPayload(BaseModel):
    provider: str
    hostname: str
    cpuUtilization: float
    ramUtilization: float
    sshAuthFailures: int

# Kafka configuration
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
MOCK_MODE = os.getenv("MOCK_MODE", "true").lower() == "true"

producer = None

def init_kafka_producer():
    global producer
    if MOCK_MODE:
        logger.info("🧠 Running in Mock Kafka Mode. Alerts will be logged to stdout.")
        return
    try:
        from confluent_kafka import Producer
        producer = Producer({"bootstrap.servers": KAFKA_BROKERS})
        logger.info(f"🔌 Connected Python Kafka Producer to: {KAFKA_BROKERS}")
    except Exception as e:
        logger.error(f"❌ Failed to connect Kafka Producer: {e}. Falling back to Mock Mode.")

init_kafka_producer()

def publish_alert(alert_payload: dict):
    topic = "anomaly-alerts"
    payload_str = json.dumps(alert_payload)
    
    if MOCK_MODE or producer is None:
        logger.info(f"[MOCK KAFKA PY] -> Topic: {topic} | Payload: {payload_str}")
        return
        
    try:
        producer.produce(topic, key=alert_payload["provider"], value=payload_str)
        producer.flush()
        logger.info(f"✅ Published alert to Kafka topic '{topic}': {alert_payload['serviceName']} spike")
    except Exception as e:
        logger.error(f"❌ Failed to publish Kafka message: {e}")

@app.get("/")
def read_root():
    return {"status": "UP", "message": "CloudGuard Anomaly Detector ML service is online!"}

@app.post("/predict")
def predict_metric_anomaly(payload: CostMetricPayload):
    try:
        # Run ML model prediction
        result = detector.predict(
            provider=payload.provider,
            service_name=payload.serviceName,
            cost=payload.costUsd
        )
        
        # If model flags anomaly, build and publish alert payload
        if result["is_anomaly"]:
            actual = result["actual_cost"]
            expected = result["expected_cost"]
            ratio = actual / expected if expected > 0 else 1.0
            
            # Determine severity based on spike ratio
            if ratio >= 3.0:
                severity = "critical"
            elif ratio >= 2.0:
                severity = "high"
            elif ratio >= 1.5:
                severity = "medium"
            else:
                severity = "low"
                
            alert = {
                "provider": payload.provider,
                "accountId": payload.accountId,
                "serviceName": payload.serviceName,
                "anomalyScore": result["anomaly_score"],
                "expectedCost": expected,
                "actualCost": actual,
                "message": f"Unusual spend spike detected in {payload.provider.upper()} {payload.serviceName}. Cost is ${actual:.2f} (Expected: ${expected:.2f}).",
                "severity": severity
            }
            
            # Publish alert asynchronously to Kafka
            publish_alert(alert)
            
        return {
            "provider": payload.provider,
            "serviceName": payload.serviceName,
            "costUsd": payload.costUsd,
            "prediction": result
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/server")
def predict_server_anomaly(payload: ServerMetricPayload):
    try:
        # Run ML model prediction on multi-dimensional inputs [cpu, ram, ssh]
        result = detector.predict_server(
            provider=payload.provider,
            hostname=payload.hostname,
            cpu=payload.cpuUtilization,
            ram=payload.ramUtilization,
            ssh=payload.sshAuthFailures
        )
        
        # If threat detected (e.g. brute force scan or high CPU), construct alert payload
        if result["is_threat"]:
            threat_type = result["threat_type"]
            if threat_type == "ssh_brute_force":
                msg = f"🚨 SECURITY WARNING: SSH login brute-force attack suspected on host '{payload.hostname}' ({payload.provider.uppercase()}). {payload.sshAuthFailures} failed login attempts in 60s."
                severity = "critical"
                service = "SSH Intrusion Guard"
            else:
                msg = f"⚠️ SYSTEM ALERT: Extreme CPU load spike detected on server '{payload.hostname}' ({payload.provider.uppercase()}). CPU is at {payload.cpuUtilization:.1f}%."
                severity = "high"
                service = "Server CPU Guard"
                
            alert = {
                "provider": payload.provider,
                "accountId": "server-guard",
                "serviceName": service,
                "anomalyScore": result["anomaly_score"],
                "expectedCost": 0.0,
                "actualCost": 0.0,
                "message": msg,
                "severity": severity
            }
            # Publish alert asynchronously to Kafka
            publish_alert(alert)
            
        return {
            "provider": payload.provider,
            "hostname": payload.hostname,
            "prediction": result
        }
    except Exception as e:
        logger.error(f"Server health prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background thread to simulate consuming metrics stream from 'aggregated-costs'
# in local mock mode, ensuring end-to-end flow is fully testable offline
def simulate_kafka_consumer():
    logger.info("📡 Background Kafka Consumer loop initiated.")
    while True:
        # Every 30s, simulate checking incoming data for anomalous spikes
        # Occasionally generate a spike to trigger alerts and test the system
        time.sleep(30)
        try:
            # We randomly simulate a cost metric event or server health event
            import random
            event_type = random.choice(["cost", "security"])
            
            if event_type == "cost":
                is_spike = random.random() < 0.3
                cost = 1500.00 if is_spike else random.uniform(10.0, 50.0)
                
                # Run cost prediction
                result = detector.predict("aws", "EC2 Compute Engine", cost)
                if result["is_anomaly"]:
                    alert = {
                        "provider": "aws",
                        "accountId": "123456789012",
                        "serviceName": "EC2 Compute Engine",
                        "anomalyScore": result["anomaly_score"],
                        "expectedCost": result["expected_cost"],
                        "actualCost": result["actual_cost"],
                        "message": f"Real-time background alert: AWS EC2 Compute Engine cost spike. Actual cost: ${cost:.2f}.",
                        "severity": "critical" if cost > 1000 else "high"
                    }
                    publish_alert(alert)
            else:
                # Simulate SSH Intrusion or CPU spike
                is_hack = random.random() < 0.3
                ssh_failures = random.randint(15, 30) if is_hack else 0
                cpu = random.uniform(85.0, 99.0) if is_hack else random.uniform(10.0, 45.0)
                
                # Run server prediction
                result = detector.predict_server("aws", "aws-prod-instance", cpu, 60.0, ssh_failures)
                if result["is_threat"]:
                    threat_type = result["threat_type"]
                    alert = {
                        "provider": "aws",
                        "accountId": "server-guard",
                        "serviceName": "SSH Intrusion Guard" if threat_type == "ssh_brute_force" else "Server CPU Guard",
                        "anomalyScore": result["anomaly_score"],
                        "expectedCost": 0.0,
                        "actualCost": 0.0,
                        "message": f"🚨 SECURITY WARNING: SSH login brute-force attack suspected on host 'aws-prod-instance' (AWS). {ssh_failures} failed login attempts in 60s." if threat_type == "ssh_brute_force" else f"⚠️ SYSTEM ALERT: Extreme CPU load spike detected on server 'aws-prod-instance' (AWS). CPU is at {cpu:.1f}%.",
                        "severity": "critical" if threat_type == "ssh_brute_force" else "high"
                    }
                    publish_alert(alert)
        except Exception as e:
            logger.error(f"Consumer simulation warning: {e}")

# Start background simulation thread
threading.Thread(target=simulate_kafka_consumer, daemon=True).start()
