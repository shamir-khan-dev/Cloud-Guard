#ifndef AZURE_COLLECTOR_H
#define AZURE_COLLECTOR_H

#include "collector.h"

class AzureCollector : public MetricCollector {
public:
    std::vector<CloudMetric> collect(const std::string& subscription_id) override;
};

#endif // AZURE_COLLECTOR_H
