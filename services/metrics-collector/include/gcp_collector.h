#ifndef GCP_COLLECTOR_H
#define GCP_COLLECTOR_H

#include "collector.h"

class GCPCollector : public MetricCollector, public ServerHealthCollector {
public:
    std::vector<CloudMetric> collect(const std::string& project_id) override;
    std::vector<ServerMetric> collect_health(const std::string& hostname) override;
};

#endif // GCP_COLLECTOR_H
