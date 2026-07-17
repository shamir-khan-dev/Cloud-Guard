# CloudGuard: Distributed Multi-Cloud Cost Optimization Platform

> **Production-Grade Microservices System:** A distributed cost intelligence and anomaly detection engine that monitors multi-cloud spending across **AWS**, **Azure**, and **GCP** in real-time, leveraging machine learning to flag cost spikes and dispatch automated alerts.

[![Spring Boot](https://img.shields.io/badge/Gateway-Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)](https://spring.io/projects/spring-boot)
[![FastAPI](https://img.shields.io/badge/ML_API-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Apache Spark](https://img.shields.io/badge/Streaming-Apache_Spark-E25A29?style=flat-square&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Kafka](https://img.shields.io/badge/Broker-Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?style=flat-square&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![Next.js](https://img.shields.io/badge/Dashboard-Next.js-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)

---

## 🛠️ Microservices Architecture

CloudGuard is structured as a modular, containerized monorepo with 5 independent services connected via an event bus:

```
                  ┌───────────────────────────────┐
                  │ C++ Cost Scraper Agent        │
                  │ (AWS / Azure / GCP APIs)      │
                  └──────────────┬────────────────┘
                                 │
                         [ Topic: raw-metrics ]
                                 │
                          ┌──────▼──────┐
                          │ Apache Kafka│
                          └──────┬──────┘
                                 │
                      [ Topic: raw-metrics ]
                                 │
                  ┌──────────────▼────────────────┐
                  │ Scala Spark Analytics Engine  │
                  │ (1-min sliding cost window)   │
                  └──────────────┬────────────────┘
                                 │
                      [ Write: PostgreSQL DB ]
                                 │
                      [ Topic: aggregated-costs ]
                                 │
                  ┌──────────────▼────────────────┐
                  │ Python Anomaly Detector (ML)  │
                  │ (FastAPI & IsolationForest)   │
                  └──────────────┬────────────────┘
                                 │
                       [ Topic: anomaly-alerts ]
                                 │
                  ┌──────────────▼────────────────┐
                  │ Kotlin Alert Service          │
                  │ (Slack Webhooks & SMTP Mail)  │
                  └───────────────────────────────┘
```

---

## 📂 Project Structure

```
CloudGuard/
├── docker-compose.yml           # Runs Zookeeper, Kafka, Postgres, and Redis locally
├── sql/
│   └── schema.sql               # PostgreSQL tables (users, cost_metrics, alerts)
├── infra/
│   └── aws/                     # Terraform IaC files for RDS & MSK Kafka
├── frontend/                    # Next.js 16 + Tailwind 4 web dashboard
└── services/
    ├── api-gateway/             # Java 21 & Spring Boot 3 JWT Routing Gateway
    ├── metrics-collector/       # C++ 17 Multi-Cloud Scraping Agent
    ├── analytics-engine/        # Scala 2.13 Spark Structured Streaming aggregator
    ├── anomaly-detector/        # Python 3.12 FastAPI + scikit-learn ML model
    └── alert-service/           # Kotlin Spring Boot SMTP & Slack dispatcher
```

---

## 🚀 Getting Started (Local Development)

### Prerequisites
- Docker & Docker Compose
- Java JDK 21
- Python 3.12
- GCC / G++ (C++ 17 support)
- Scala / SBT

### Running the Infrastructure
Spin up the messaging bus, databases, and caches:
```bash
docker-compose up -d
```

### Running the Services

1. **API Gateway (Java)**:
   ```bash
   cd services/api-gateway
   mvn spring-boot:run
   ```
2. **Metrics Scraper Agent (C++)**:
   ```bash
   cd services/metrics-collector
   g++ -std=c++17 -Iinclude main.cpp src/*.cpp -o metrics-collector
   ./metrics-collector
   ```
3. **Analytics Engine (Scala)**:
   ```bash
   cd services/analytics-engine
   sbt run
   ```
4. **ML Anomaly Detector (Python)**:
   ```bash
   cd services/anomaly-detector
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
5. **Alert Service (Kotlin)**:
   ```bash
   cd services/alert-service
   ./gradlew bootRun
   ```
6. **Frontend Dashboard (Next.js)**:
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   npm run dev
   ```

Open `http://localhost:3000` to view the cost optimization dashboard.

---

## 🔒 Security & Optimization Features
- **JWT Authorization**: Secure token exchange at the Gateway level to protect client endpoints.
- **Failover Databases**: Dual DB architecture supporting H2 In-Memory failover during development and production PostgreSQL connection string handling.
- **Unsupervised Anomaly Model**: ML IsolationForest dynamically scores incoming data without manual thresholds, preventing false positives on cost decreases.
- **Branded Notification Integrations**: Webhook blocks for Slack and HTML mail formatting for SMTP clients.
