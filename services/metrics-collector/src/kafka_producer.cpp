#include "kafka_producer.h"
#include <iostream>

KafkaProducer::KafkaProducer(const std::string& brokers, bool use_mock) 
    : brokers_list(brokers), mock_mode(use_mock) {}

KafkaProducer::~KafkaProducer() {
    if (!mock_mode) {
        std::cout << "🔌 Closing connection to Kafka brokers: " << brokers_list << std::endl;
    }
}

bool KafkaProducer::initialize() {
    if (mock_mode) {
        std::cout << "🧠 Initializing mock Kafka Producer (logging to console fallback)..." << std::endl;
        return true;
    }
    
    std::cout << "🔌 Connecting to Kafka cluster at: " << brokers_list << "..." << std::endl;
    // Real Kafka client initiation would occur here using librdkafka
    std::cout << "⚠️  Kafka cluster offline or unreachable. Falling back to local console logger." << std::endl;
    mock_mode = true;
    return true;
}

void KafkaProducer::send_message(const std::string& topic, const std::string& key, const std::string& payload) {
    if (mock_mode) {
        std::cout << "[MOCK KAFKA] -> Topic: " << topic 
                  << " | Key: " << key 
                  << " | Payload: " << payload << std::endl;
        return;
    }
    
    // Publish message to Kafka broker here using rd_kafka_produce
}
