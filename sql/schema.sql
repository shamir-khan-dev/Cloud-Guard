-- Enable pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cloud Accounts Table
CREATE TABLE IF NOT EXISTS cloud_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL,         -- 'aws' | 'azure' | 'gcp'
  account_id VARCHAR(100) NOT NULL,
  display_name VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT unique_user_provider_account UNIQUE (user_id, provider, account_id)
);

-- Cost Metrics Table (Stores granular raw cost metrics)
CREATE TABLE IF NOT EXISTS cost_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cloud_account_id UUID REFERENCES cloud_accounts(id) ON DELETE CASCADE,
  service_name VARCHAR(100) NOT NULL,     -- e.g. 'EC2', 'S3', 'Lambda'
  region VARCHAR(50) NOT NULL,            -- e.g. 'us-east-1', 'eastus'
  cost_usd NUMERIC(12, 4) NOT NULL,
  usage_amount NUMERIC(16, 4),
  usage_unit VARCHAR(50),
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Anomaly Alerts Table
CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cloud_account_id UUID REFERENCES cloud_accounts(id) ON DELETE CASCADE,
  service_name VARCHAR(100) NOT NULL,
  anomaly_score NUMERIC(6, 4) NOT NULL,
  expected_cost NUMERIC(12, 4),
  actual_cost NUMERIC(12, 4),
  message TEXT NOT NULL,
  severity VARCHAR(50) NOT NULL,         -- 'low' | 'medium' | 'high' | 'critical'
  resolved BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create some indexes for performance
CREATE INDEX IF NOT EXISTS idx_cost_metrics_account_time ON cost_metrics (cloud_account_id, period_start);
CREATE INDEX IF NOT EXISTS idx_alerts_account_time ON alerts (cloud_account_id, created_at);
