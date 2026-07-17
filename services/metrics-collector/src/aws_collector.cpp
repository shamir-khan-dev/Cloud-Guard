#include "aws_collector.h"
#include "system_monitor.h"
#include <random>
#include <ctime>

std::vector<CloudMetric> AWSCollector::collect(const std::string& account_id) {
    std::vector<CloudMetric> metrics;
    std::string timestamp = get_current_timestamp();
    
    // Seed random number generator
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.9, 1.15); // Slight fluctuation factor
    
    // 1. EC2 Compute Spend
    CloudMetric ec2;
    ec2.provider = "aws";
    ec2.account_id = account_id;
    ec2.service_name = "EC2 Compute Engine";
    ec2.region = "us-east-1";
    // Base cost is $15.50 per hour factor * fluctuation
    ec2.cost_usd = 15.50 * dis(gen);
    ec2.usage_amount = 24.0 * dis(gen); // Hrs
    ec2.usage_unit = "Hrs";
    ec2.timestamp = timestamp;
    metrics.push_back(ec2);
    
    // 2. S3 Storage Spend
    CloudMetric s3;
    s3.provider = "aws";
    s3.account_id = account_id;
    s3.service_name = "S3 Simple Storage";
    s3.region = "us-east-1";
    s3.cost_usd = 3.20 * dis(gen);
    s3.usage_amount = 120.5 * dis(gen); // GB
    s3.usage_unit = "GB-Month";
    s3.timestamp = timestamp;
    metrics.push_back(s3);
    
    // 3. RDS Database Spend
    CloudMetric rds;
    rds.provider = "aws";
    rds.account_id = account_id;
    rds.service_name = "RDS Aurora Database";
    rds.region = "us-east-1";
    rds.cost_usd = 8.75 * dis(gen);
    rds.usage_amount = 24.0 * dis(gen);
    rds.usage_unit = "Hrs";
    rds.timestamp = timestamp;
    metrics.push_back(rds);
    
    return metrics;
}

std::vector<ServerMetric> AWSCollector::collect_health(const std::string& hostname) {
    std::vector<ServerMetric> metrics;
    std::string timestamp = get_current_timestamp();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.9, 1.1);
    std::uniform_int_distribution<> hack_chance(1, 10);
    
    ServerMetric m;
    m.provider = "aws";
    m.hostname = hostname;
    m.cpu_utilization = get_physical_cpu_utilization();
    m.ram_utilization = get_physical_ram_utilization();
    
    // Simulate active SSH hacking brute force 10% of the time
    if (hack_chance(gen) == 10) {
        std::uniform_int_distribution<> failures(12, 28);
        m.ssh_auth_failures = failures(gen);
        m.cpu_utilization += 35.0; // Hacking spikes CPU load!
    } else {
        m.ssh_auth_failures = 0;
    }
    
    m.timestamp = timestamp;
    metrics.push_back(m);
    
    return metrics;
}
