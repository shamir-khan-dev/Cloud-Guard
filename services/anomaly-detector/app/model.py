import numpy as np
from sklearn.ensemble import IsolationForest
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-model")

class AnomalyDetectorModel:
    def __init__(self):
        # Dictionary storing history for each (provider, service_name)
        # e.g., { ("aws", "EC2 Compute Engine"): [15.2, 14.8, 15.6, ...] }
        self.history = {}
        # Trained IsolationForest models for each combination
        self.models = {}
        # Minimum data points needed to run ML prediction (fallback to standard deviation rule if less)
        self.min_train_points = 5

    def add_history(self, provider: str, service_name: str, cost: float):
        key = (provider.lower(), service_name)
        if key not in self.history:
            # Seed with some realistic base history to avoid cold start issues
            # We seed with 8 points close to the cost to establish a baseline
            self.history[key] = [cost * (0.9 + 0.05 * i) for i in range(8)]
        else:
            self.history[key].append(cost)
            # Keep history capped at 100 points for memory efficiency
            if len(self.history[key]) > 100:
                self.history[key].pop(0)

    def train_model(self, provider: str, service_name: str):
        key = (provider.lower(), service_name)
        data = np.array(self.history[key]).reshape(-1, 1)
        
        # Train IsolationForest model
        # contamination represents expected anomaly rate (e.g. 5%)
        clf = IsolationForest(contamination=0.05, random_state=42)
        clf.fit(data)
        self.models[key] = clf
        logger.info(f" Trained IsolationForest model for {provider} - {service_name} with {len(data)} points.")

    def predict(self, provider: str, service_name: str, cost: float) -> dict:
        key = (provider.lower(), service_name)
        
        # Ensure we have history for this service
        self.add_history(provider, service_name, cost)
        
        # Always retrain to adapt to rolling window changes
        self.train_model(provider, service_name)
        
        history_data = self.history[key]
        avg_cost = sum(history_data) / len(history_data)
        
        model = self.models[key]
        prediction = model.predict([[cost]])[0] # Returns 1 for normal, -1 for anomaly
        
        # Calculate raw anomaly score (higher means more anomalous/outlier)
        # decision_function returns negative values for anomalies, positive for normals
        raw_score = model.decision_function([[cost]])[0]
        # Map raw score to a 0.0 - 1.0 probability range for dashboard usability
        normalized_score = float(1.0 / (1.0 + np.exp(raw_score * 5.0))) # Sigmoid mapping
        
        is_anomaly = bool(prediction == -1)
        
        # Double-check: Anomaly must be a spike (cost higher than average), not a cost reduction!
        if is_anomaly and cost < avg_cost:
            is_anomaly = False # Cost reductions are not alerts
            
        return {
            "is_anomaly": is_anomaly,
            "anomaly_score": normalized_score,
            "expected_cost": float(avg_cost),
            "actual_cost": float(cost)
        }

# Global singleton instance
detector = AnomalyDetectorModel()
