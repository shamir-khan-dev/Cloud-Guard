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

        val isSecurity = alert.accountId == "server-guard"
        val titleText = if (isSecurity) "$emoji ${alert.serviceName} Security Threat" else "$emoji ${alert.serviceName} Cost Spike"
        val fields = if (isSecurity) {
            listOf(
                mapOf("title" to "Cloud Provider", "value" to alert.provider.uppercase(), "short" to true),
                mapOf("title" to "Intrusion Guard", "value" to alert.serviceName, "short" to true),
                mapOf("title" to "ML Confidence Score", "value" to "${String.format("%.1f", alert.anomalyScore * 100)}%", "short" to true),
                mapOf("title" to "Threat Status", "value" to "🚨 UNRESOLVED", "short" to true)
            )
        } else {
            listOf(
                mapOf("title" to "Cloud Provider", "value" to alert.provider.uppercase(), "short" to true),
                mapOf("title" to "Account/Subscription", "value" to alert.accountId, "short" to true),
                mapOf("title" to "Expected Cost", "value" to "\$${String.format("%.2f", alert.expectedCost)}", "short" to true),
                mapOf("title" to "Actual Cost", "value" to "\$${String.format("%.2f", alert.actualCost)}", "short" to true),
                mapOf("title" to "ML Anomaly Score", "value" to "${String.format("%.1f", alert.anomalyScore * 100)}%", "short" to true)
            )
        }

        // Build rich Slack block kit message payload
        val payload = mapOf(
            "attachments" to listOf(
                mapOf(
                    "fallback" to "CloudGuard Anomaly Alert: ${alert.message}",
                    "color" to color,
                    "pretext" to "⚡ *CloudGuard Anomaly Detection Notification* ⚡",
                    "title" to titleText,
                    "text" to alert.message,
                    "fields" to fields,
                    "footer" to "CloudGuard Security Posture Manager",
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
