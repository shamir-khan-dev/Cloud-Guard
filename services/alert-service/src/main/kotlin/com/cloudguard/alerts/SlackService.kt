package com.cloudguard.alerts

import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Value
import org.springframework.http.HttpEntity
import org.springframework.http.HttpHeaders
import org.springframework.http.MediaType
import org.springframework.stereotype.Service
import org.springframework.web.client.RestTemplate

@Service
class SlackService {
    private val log = LoggerFactory.getLogger(SlackService::class.java)
    private val restTemplate = RestTemplate()

    @Value("\${app.slack.webhookUrl}")
    private lateinit var webhookUrl: String

    fun sendSlackNotification(alert: AlertMessage) {
        val color = when (alert.severity.lowercase()) {
            "critical" -> "#EF4444" // Red
            "high" -> "#F59E0B"     // Orange
            "medium" -> "#10B981"   // Green/Emerald
            else -> "#6366F1"       // Indigo
        }

        val emoji = when (alert.severity.lowercase()) {
            "critical" -> "🔴 [CRITICAL ALARM]"
            "high" -> "🟠 [HIGH WARNING]"
            else -> "🟡 [ALERT]"
        }

        // Build rich Slack block kit message payload
        val payload = mapOf(
            "attachments" to listOf(
                mapOf(
                    "fallback" to "CloudGuard Anomaly Alert: ${alert.message}",
                    "color" to color,
                    "pretext" to "⚡ *CloudGuard Anomaly Detection Notification* ⚡",
                    "title" to "$emoji ${alert.serviceName} Cost Spike",
                    "text" to alert.message,
                    "fields" to listOf(
                        mapOf("title" to "Cloud Provider", "value" to alert.provider.uppercase(), "short" to true),
                        mapOf("title" to "Account/Subscription", "value" to alert.accountId, "short" to true),
                        mapOf("title" to "Expected Cost", "value" to "\$${String.format("%.2f", alert.expectedCost)}", "short" to true),
                        mapOf("title" to "Actual Cost", "value" to "\$${String.format("%.2f", alert.actualCost)}", "short" to true),
                        mapOf("title" to "ML Anomaly Score", "value" to "${String.format("%.1f", alert.anomalyScore * 100)}%", "short" to true)
                    ),
                    "footer" to "CloudGuard Cost Optimizer Service",
                    "ts" to System.currentTimeMillis() / 1000
                )
            )
        )

        try {
            log.info("Sending Slack webhook alert to Slack API for ${alert.serviceName}...")
            val headers = HttpHeaders()
            headers.contentType = MediaType.APPLICATION_JSON
            val request = HttpEntity(payload, headers)
            
            // Execute Slack Webhook call
            if (webhookUrl.contains("mock")) {
                log.info("[MOCK SLACK DISPATCH] -> Headers: {} | Body: {}", headers, payload)
            } else {
                restTemplate.postForLocation(webhookUrl, request)
                log.info("✅ Slack webhook dispatched successfully!")
            }
        } catch (e: Exception) {
            log.error("❌ Failed to send Slack alert: ${e.message}")
        }
    }
}
