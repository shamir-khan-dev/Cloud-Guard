#ifndef AZURE_COLLECTOR_H
#define AZURE_COLLECTOR_H

#include "collector.h"

class AzureCollector : public MetricCollector, public ServerHealthCollector {
public:
    std::vector<CloudMetric> collect(const std::string& subscription_id) override;
    std::vector<ServerMetric> collect_health(const std::string& hostname) override;
};

#endif // AZURE_COLLECTOR_H
