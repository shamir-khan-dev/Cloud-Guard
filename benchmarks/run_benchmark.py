import time
import os
import sys
import json

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

# Ensure services/anomaly-detector is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "services", "anomaly-detector")))

from app.model import AnomalyDetectorModel

def run_performance_benchmarks():
    print("=" * 70)
    print("[BENCHMARK] CLOUDGUARD ANOMALY DETECTOR - HIGH-FREQUENCY SUITE")
    print("=" * 70)
    
    model = AnomalyDetectorModel()
    num_samples = 500
    
    # 1. Warmup
    print("\n[1/3] Warming up model with baseline streams...")
    for i in range(15):
        model.predict("aws", "EC2", 30.0 + i)
        model.predict_server("aws", "worker-01", cpu=30.0, ram=50.0, ssh=0)
    print("      Warmup complete.")

    # 2. Benchmark Server Health Telemetry Inference
    print(f"\n[2/3] Benchmarking multi-dimensional server telemetry inference ({num_samples} iterations)...")
    latencies_server = []
    
    start_total_server = time.perf_counter()
    for i in range(num_samples):
        cpu = float(30.0 + (i % 20))
        ram = float(50.0 + (i % 10))
        ssh = 0 if i % 50 != 0 else 18 # Injected attack
        
        t0 = time.perf_counter()
        model.predict_server("aws", f"worker-{i % 5}", cpu=cpu, ram=ram, ssh=ssh)
        t1 = time.perf_counter()
        latencies_server.append((t1 - t0) * 1000.0) # Convert to ms
        
    total_time_server = time.perf_counter() - start_total_server
    throughput_server = num_samples / total_time_server

    # 3. Benchmark Billing Anomaly Inference
    print(f"\n[3/3] Benchmarking financial spend stream inference ({num_samples} iterations)...")
    latencies_cost = []
    
    start_total_cost = time.perf_counter()
    for i in range(num_samples):
        cost = 35.0 + (i % 15)
        if i % 75 == 0:
            cost = 1450.0 # Spend spike
            
        t0 = time.perf_counter()
        model.predict("gcp", f"BigQuery-{i % 3}", cost)
        t1 = time.perf_counter()
        latencies_cost.append((t1 - t0) * 1000.0)
        
    total_time_cost = time.perf_counter() - start_total_cost
    throughput_cost = num_samples / total_time_cost

    # Compute percentiles
    p50_srv = np.percentile(latencies_server, 50)
    p95_srv = np.percentile(latencies_server, 95)
    p99_srv = np.percentile(latencies_server, 99)

    p50_cost = np.percentile(latencies_cost, 50)
    p95_cost = np.percentile(latencies_cost, 95)
    p99_cost = np.percentile(latencies_cost, 99)

    print("\n" + "=" * 70)
    print("BENCHMARK SCORECARD & LATENCY PERCENTILES")
    print("=" * 70)
    print(f"{'Pipeline':<28} | {'p50':<8} | {'p95':<8} | {'p99':<8} | {'Throughput':<14}")
    print("-" * 70)
    print(f"{'Server Health / Security':<28} | {p50_srv:6.2f}ms | {p95_srv:6.2f}ms | {p99_srv:6.2f}ms | {throughput_server:8.1f} ops/sec")
    print(f"{'Billing Spend Anomaly':<28} | {p50_cost:6.2f}ms | {p95_cost:6.2f}ms | {p99_cost:6.2f}ms | {throughput_cost:8.1f} ops/sec")
    print("=" * 70)

    # Save benchmark report to JSON for CI/README reference
    report = {
        "num_samples": num_samples,
        "server_telemetry": {
            "p50_ms": round(float(p50_srv), 2),
            "p95_ms": round(float(p95_srv), 2),
            "p99_ms": round(float(p99_srv), 2),
            "throughput_ops_per_sec": round(float(throughput_server), 1)
        },
        "billing_telemetry": {
            "p50_ms": round(float(p50_cost), 2),
            "p95_ms": round(float(p95_cost), 2),
            "p99_ms": round(float(p99_cost), 2),
            "throughput_ops_per_sec": round(float(throughput_cost), 1)
        }
    }
    
    out_path = os.path.join(os.path.dirname(__file__), "benchmark_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Benchmark results saved to: {out_path}\n")

if __name__ == "__main__":
    run_performance_benchmarks()
