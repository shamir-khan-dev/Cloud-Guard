#ifndef AWS_COLLECTOR_H
#define AWS_COLLECTOR_H

#include "collector.h"

class AWSCollector : public MetricCollector, public ServerHealthCollector {
public:
    std::vector<CloudMetric> collect(const std::string& account_id) override;
    std::vector<ServerMetric> collect_health(const std::string& hostname) override;
};

#endif // AWS_COLLECTOR_H
