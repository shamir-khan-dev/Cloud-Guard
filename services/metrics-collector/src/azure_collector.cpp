#include "azure_collector.h"
#include <random>
#include <ctime>

std::vector<CloudMetric> AzureCollector::collect(const std::string& subscription_id) {
    std::vector<CloudMetric> metrics;
    std::string timestamp = get_current_timestamp();
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> dis(0.9, 1.15); // Slight fluctuation factor
    
    // 1. Azure Virtual Machines
    CloudMetric vm;
    vm.provider = "azure";
    vm.account_id = subscription_id;
    vm.service_name = "Virtual Machines";
    vm.region = "eastus";
    vm.cost_usd = 11.20 * dis(gen);
    vm.usage_amount = 24.0 * dis(gen);
    vm.usage_unit = "Hrs";
    vm.timestamp = timestamp;
    metrics.push_back(vm);
    
    // 2. Blob Storage
    CloudMetric storage;
    storage.provider = "azure";
    storage.account_id = subscription_id;
    storage.service_name = "Blob Storage";
    storage.region = "eastus";
    storage.cost_usd = 2.45 * dis(gen);
    storage.usage_amount = 95.2 * dis(gen);
    storage.usage_unit = "GB-Month";
    storage.timestamp = timestamp;
    metrics.push_back(storage);
    
    // 3. AKS (Azure Kubernetes Service)
    CloudMetric aks;
    aks.provider = "azure";
    aks.account_id = subscription_id;
    aks.service_name = "AKS Kubernetes Services";
    aks.region = "eastus";
    aks.cost_usd = 6.80 * dis(gen);
    aks.usage_amount = 24.0 * dis(gen);
    aks.usage_unit = "Hrs";
    aks.timestamp = timestamp;
    metrics.push_back(aks);
    
    return metrics;
}
