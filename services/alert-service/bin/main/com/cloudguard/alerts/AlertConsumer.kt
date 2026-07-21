package com.cloudguard.alerts

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.readValue
import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.kafka.annotation.KafkaListener
import org.springframework.stereotype.Component

@Component
class AlertConsumer {
    private val log = LoggerFactory.getLogger(AlertConsumer::class.java)

    @Autowired
    private lateinit var slackService: SlackService

    @Autowired
    private lateinit var emailService: EmailService

    @Autowired
    private lateinit var objectMapper: ObjectMapper

    @KafkaListener(topics = ["anomaly-alerts"], groupId = "alert-group")
    fun consumeAnomalyAlert(message: String) {
        log.info("📥 Consumed raw anomaly alert event: $message")
        try {
            // Deserialize JSON payload into AlertMessage object
            val alert: AlertMessage = objectMapper.readValue(message)
            log.info("🔔 Processing cost anomaly alert for ${alert.provider.uppercase()} -> ${alert.serviceName} (${alert.severity})")

            // Dispatch Slack notification
            slackService.sendSlackNotification(alert)

            // Dispatch Email alert
            emailService.sendEmailNotification(alert)

            log.info("🚀 Anomaly alert notifications successfully dispatched!")
        } catch (e: Exception) {
            log.error("❌ Failed to parse and dispatch anomaly alert: ${e.message}")
        }
    }
}
