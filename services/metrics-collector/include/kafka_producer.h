#ifndef KAFKA_PRODUCER_H
#define KAFKA_PRODUCER_H

#include <string>

class KafkaProducer {
private:
    std::string brokers_list;
    bool mock_mode;
    
public:
    KafkaProducer(const std::string& brokers, bool use_mock = true);
    ~KafkaProducer();
    
    bool initialize();
    void send_message(const std::string& topic, const std::string& key, const std::string& payload);
};

#endif // KAFKA_PRODUCER_H
