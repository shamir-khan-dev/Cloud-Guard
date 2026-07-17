#include <iostream>
#include <thread>
#include <chrono>
#include <sstream>
#include <cstdlib>
#include "aws_collector.h"
#include "azure_collector.h"
#include "gcp_collector.h"
#include "kafka_producer.h"

// Simple helper to serialize CloudMetric to JSON string
std::string serialize_to_json(const CloudMetric& m) {
    std::ostringstream ss;
    ss << "{"
       << "\"provider\":\"" << m.provider << "\","
       << "\"accountId\":\"" << m.account_id << "\","
       << "\"serviceName\":\"" << m.service_name << "\","
       << "\"region\":\"" << m.region << "\","
       << "\"costUsd\":" << m.cost_usd << ","
       << "\"usageAmount\":" << m.usage_amount << ","
       << "\"usageUnit\":\"" << m.usage_unit << "\","
       << "\"timestamp\":\"" << m.timestamp << "\""
       << "}";
    return ss.str();
}

// Simple helper to serialize ServerMetric to JSON string
std::string serialize_server_metric(const ServerMetric& m) {
    std::ostringstream ss;
    ss << "{"
       << "\"provider\":\"" << m.provider << "\","
       << "\"hostname\":\"" << m.hostname << "\","
       << "\"cpuUtilization\":" << m.cpu_utilization << ","
       << "\"ramUtilization\":" << m.ram_utilization << ","
       << "\"sshAuthFailures\":" << m.ssh_auth_failures << ","
       << "\"timestamp\":\"" << m.timestamp << "\""
       << "}";
    return ss.str();
}

int main() {
    std::cout << "🚀 CloudGuard Metrics Collector Agent starting up..." << std::endl;
    
    // Read config from Environment Variables
    const char* kafka_brokers_env = std::getenv("KAFKA_BROKERS");
    std::string kafka_brokers = kafka_brokers_env ? kafka_brokers_env : "localhost:9092";
    
    const char* mock_mode_env = std::getenv("MOCK_MODE");
    bool use_mock = true; // Default to mock mode for easy local compilation
    if (mock_mode_env && std::string(mock_mode_env) == "false") {
        use_mock = false;
    }
    
    // Instantiate Collectors and Producer
    AWSCollector aws;
    AzureCollector azure;
    GCPCollector gcp;
    
    KafkaProducer producer(kafka_brokers, use_mock);
    if (!producer.initialize()) {
        std::cerr << "❌ Failed to initialize producer. Exiting." << std::endl;
        return 1;
    }
    
    std::cout << "📡 Metrics Scraper loop initiated (Polling every 10 seconds)..." << std::endl;
    
    // Test account identifiers
    std::string aws_account = "123456789012";
    std::string azure_subscription = "azure-sub-8899";
    std::string gcp_project = "cloudguard-gcp-prod";
    
    int iteration = 1;
    while (true) {
        std::cout << "\n--- Scrape Cycle #" << iteration << " ---" << std::endl;
        
        // 1. Collect and dispatch AWS Metrics
        auto aws_metrics = aws.collect(aws_account);
        for (const auto& m : aws_metrics) {
            std::string json = serialize_to_json(m);
            producer.send_message("raw-metrics", m.provider, json);
        }
        
        // 2. Collect and dispatch Azure Metrics
        auto azure_metrics = azure.collect(azure_subscription);
        for (const auto& m : azure_metrics) {
            std::string json = serialize_to_json(m);
            producer.send_message("raw-metrics", m.provider, json);
        }
        
        // 3. Collect and dispatch GCP Metrics
        auto gcp_metrics = gcp.collect(gcp_project);
        for (const auto& m : gcp_metrics) {
            std::string json = serialize_to_json(m);
            producer.send_message("raw-metrics", m.provider, json);
        }
        
        // 4. Collect and dispatch AWS Server Health
        auto aws_health = aws.collect_health("aws-prod-instance");
        for (const auto& h : aws_health) {
            std::string json = serialize_server_metric(h);
            producer.send_message("server-health", h.hostname, json);
        }

        // 5. Collect and dispatch Azure Server Health
        auto azure_health = azure.collect_health("azure-vm-sandbox");
        for (const auto& h : azure_health) {
            std::string json = serialize_server_metric(h);
            producer.send_message("server-health", h.hostname, json);
        }

        // 6. Collect and dispatch GCP Server Health
        auto gcp_health = gcp.collect_health("gcp-bigdata-node");
        for (const auto& h : gcp_health) {
            std::string json = serialize_server_metric(h);
            producer.send_message("server-health", h.hostname, json);
        }
        
        std::cout.flush();
        iteration++;
        
        // Sleep for 10 seconds before next polling cycle
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }
    
    return 0;
}
