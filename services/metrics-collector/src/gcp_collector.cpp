#include "gcp_collector.h"
#include <random>
#include <ctime>

std::vector<CloudMetric> GCPCollector::collect(const std::string& project_id) {
    std::vector<CloudMetric> metrics;
    std::string timestamp = get_current_timestamp();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.9, 1.15); // Slight fluctuation factor
    
    // 1. GCP Compute Engine
    CloudMetric gce;
    gce.provider = "gcp";
    gce.account_id = project_id;
    gce.service_name = "Compute Engine";
    gce.region = "us-central1";
    gce.cost_usd = 9.80 * dis(gen);
    gce.usage_amount = 24.0 * dis(gen);
    gce.usage_unit = "Hrs";
    gce.timestamp = timestamp;
    metrics.push_back(gce);
    
    // 2. Cloud Storage
    CloudMetric storage;
    storage.provider = "gcp";
    storage.account_id = project_id;
    storage.service_name = "Cloud Storage";
    storage.region = "us-central1";
    storage.cost_usd = 1.95 * dis(gen);
    storage.usage_amount = 78.4 * dis(gen);
    storage.usage_unit = "GB-Month";
    storage.timestamp = timestamp;
    metrics.push_back(storage);
    
    // 3. BigQuery Analytics
    CloudMetric bq;
    bq.provider = "gcp";
    bq.account_id = project_id;
    bq.service_name = "BigQuery Data Storage";
    bq.region = "us-central1";
    bq.cost_usd = 5.20 * dis(gen);
    bq.usage_amount = 1.2 * dis(gen); // TB scanned
    bq.usage_unit = "TB";
    bq.timestamp = timestamp;
    metrics.push_back(bq);
    
    return metrics;
}

std::vector<ServerMetric> GCPCollector::collect_health(const std::string& hostname) {
    std::vector<ServerMetric> metrics;
    std::string timestamp = get_current_timestamp();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.9, 1.1);
    std::uniform_int_distribution<> hack_chance(1, 10);
    
    ServerMetric m;
    m.provider = "gcp";
    m.hostname = hostname;
    m.cpu_utilization = 32.0 * dis(gen); // Base CPU around 32%
    m.ram_utilization = 48.0 * dis(gen); // Base RAM around 48%
    
    // Simulate active SSH hacking brute force 10% of the time
    if (hack_chance(gen) == 10) {
        std::uniform_int_distribution<> failures(8, 20);
        m.ssh_auth_failures = failures(gen);
        m.cpu_utilization += 45.0; // Hacking spikes CPU load!
    } else {
        m.ssh_auth_failures = 0;
    }
    
    m.timestamp = timestamp;
    metrics.push_back(m);
    
    return metrics;
}
