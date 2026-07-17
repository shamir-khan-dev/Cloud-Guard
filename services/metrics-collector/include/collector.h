#ifndef COLLECTOR_H
#define COLLECTOR_H

#include <string>
#include <vector>
#include <chrono>

struct CloudMetric {
    std::string provider;       // 'aws' | 'azure' | 'gcp'
    std::string account_id;
    std::string service_name;   // e.g. 'EC2', 'S3', 'AKS'
    std::string region;         // e.g. 'us-east-1', 'eastus'
    double cost_usd;
    double usage_amount;
    std::string usage_unit;
    std::string timestamp;      // ISO 8601 string
};

struct ServerMetric {
    std::string provider;       // 'aws' | 'azure' | 'gcp'
    std::string hostname;
    double cpu_utilization;
    double ram_utilization;
    int ssh_auth_failures;
    std::string timestamp;
};

class MetricCollector {
public:
    virtual ~MetricCollector() = default;
    
    // Pure virtual method to collect metrics from a specific cloud account
    virtual std::vector<CloudMetric> collect(const std::string& account_id) = 0;
};

class ServerHealthCollector {
public:
    virtual ~ServerHealthCollector() = default;
    virtual std::vector<ServerMetric> collect_health(const std::string& hostname) = 0;
};

// Utility function to get current ISO 8601 timestamp in C++
inline std::string get_current_timestamp() {
    auto now = std::chrono::system_clock::now();
    auto in_time_t = std::chrono::system_clock::to_time_t(now);
    
    char buf[100];
    // Formats to ISO 8601: YYYY-MM-DDTHH:MM:SSZ
    std::strftime(buf, sizeof(buf), "%Y-%m-%dT%H:%M:%SZ", std::gmtime(&in_time_t));
    return std::string(buf);
}

#endif // COLLECTOR_H
