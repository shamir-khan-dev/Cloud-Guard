#ifndef AWS_COLLECTOR_H
#define AWS_COLLECTOR_H

#include "collector.h"

class AWSCollector : public MetricCollector {
public:
    std::vector<CloudMetric> collect(const std::string& account_id) override;
};

#endif // AWS_COLLECTOR_H
