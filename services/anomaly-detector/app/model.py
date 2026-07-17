import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-model")

class AnomalyDetectorModel:
    def __init__(self):
        # 1. Billing cost histories & models
        self.history = {}
        self.models = {}
        
        # 2. Server health histories & models
        # history key: (provider, hostname), value list of [cpu, ram, ssh]
        self.server_history = {}
        self.server_models = {}
        
        self.min_train_points = 5

    # --- BILLING ANOMALY METHODS ---
    
    def add_history(self, provider: str, service_name: str, cost: float):
        key = (provider.lower(), service_name)
        if key not in self.history:
            self.history[key] = [cost * (0.9 + 0.02 * i) for i in range(8)]
        else:
            self.history[key].append(cost)
            if len(self.history[key]) > 100:
                self.history[key].pop(0)

    def train_model(self, provider: str, service_name: str):
        key = (provider.lower(), service_name)
        data = np.array(self.history[key]).reshape(-1, 1)
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(data)
        self.models[key] = clf

    def predict(self, provider: str, service_name: str, cost: float) -> dict:
        key = (provider.lower(), service_name)
        self.add_history(provider, service_name, cost)
        self.train_model(provider, service_name)
        
        history_data = self.history[key]
        avg_cost = sum(history_data) / len(history_data)
        
        model = self.models[key]
        prediction = model.predict([[cost]])[0]
        raw_score = model.decision_function([[cost]])[0]
        normalized_score = float(1.0 / (1.0 + np.exp(raw_score * 5.0)))
        
        is_anomaly = bool(prediction == -1)
        if is_anomaly and cost < avg_cost:
            is_anomaly = False
            
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": normalized_score,
            "expected_cost": float(avg_cost),
            "actual_cost": float(cost)
        }

    # --- SERVER HEALTH & SECURITY ANOMALY METHODS ---

    def add_server_history(self, provider: str, hostname: str, cpu: float, ram: float, ssh: int):
        key = (provider.lower(), hostname)
        if key not in self.server_history:
            # Seed with baseline CPU (30-40%), RAM (50-60%), SSH failures (0)
            self.server_history[key] = [
                [35.0 + i, 55.0 + (i * 0.5), 0] for i in range(8)
            ]
        else:
            self.server_history[key].append([cpu, ram, ssh])
            if len(self.server_history[key]) > 100:
                self.server_history[key].pop(0)

    def train_server_model(self, provider: str, hostname: str):
        key = (provider.lower(), hostname)
        data = np.array(self.server_history[key])
        
        # Train on multi-dimensional inputs: [CPU, RAM, SSH Failures]
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(data)
        self.server_models[key] = clf

    def predict_server(self, provider: str, hostname: str, cpu: float, ram: float, ssh: int) -> dict:
        key = (provider.lower(), hostname)
        
        # Add to history and train
        self.add_server_history(provider, hostname, cpu, ram, ssh)
        self.train_server_model(provider, hostname)
        
        history_data = self.server_history[key]
        avg_cpu = sum(h[0] for h in history_data) / len(history_data)
        avg_ssh = sum(h[2] for h in history_data) / len(history_data)
        
        model = self.server_models[key]
        prediction = model.predict([[cpu, ram, ssh]])[0]
        raw_score = model.decision_function([[cpu, ram, ssh]])[0]
        normalized_score = float(1.0 / (1.0 + np.exp(raw_score * 5.0)))
        
        is_anomaly = bool(prediction == -1)
        
        # Flag as threat if CPU utilization or SSH login failures are anomalously high
        is_threat = False
        threat_type = "none"
        
        if is_anomaly:
            if ssh > 5:
                is_threat = True
                threat_type = "ssh_brute_force"
            elif cpu > avg_cpu * 1.5 and cpu > 75.0:
                is_threat = True
                threat_type = "cpu_utilization_spike"
        
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": normalized_score,
            "is_threat": is_threat,
            "threat_type": threat_type,
            "metrics": {
                "cpu": cpu,
                "ram": ram,
                "ssh_failures": ssh
            },
            "baselines": {
                "avg_cpu": avg_cpu,
                "avg_ssh": avg_ssh
            }
        }

# Global singleton instance
detector = AnomalyDetectorModel()
