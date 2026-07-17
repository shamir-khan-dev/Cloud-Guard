package com.cloudguard.alerts

import org.slf4j.LoggerFactory
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.beans.factory.annotation.Value
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.mail.javamail.MimeMessageHelper
import org.springframework.stereotype.Service

@Service
class EmailService {
    private val log = LoggerFactory.getLogger(EmailService::class.java)

    @Autowired(required = false)
    private val mailSender: JavaMailSender? = null

    @Value("\${spring.mail.username}")
    private lateinit var fromEmail: String

    @Value("\${app.alerts.emailRecipient}")
    private lateinit var toEmail: String

    fun sendEmailNotification(alert: AlertMessage) {
        val subject = "⚠️ [CloudGuard Anomaly] ${alert.severity.uppercase()} Spend Spike in ${alert.provider.uppercase()}"
        
        val htmlContent = """
            <div style="font-family: Arial, sans-serif; max-width: 600px; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; color: #1e293b;">
                <div style="background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); padding: 24px; text-align: center; color: white;">
                    <h2 style="margin: 0; font-size: 22px;">CloudGuard Cost Alert</h2>
                    <p style="margin: 4px 0 0 0; opacity: 0.85; font-size: 14px;">Real-time Multi-Cloud Cost Optimizer</p>
                </div>
                <div style="padding: 24px;">
                    <div style="background-color: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; padding: 16px; margin-bottom: 24px;">
                        <h3 style="margin: 0 0 8px 0; color: #b91c1c; font-size: 16px;">Spike Detected: ${alert.serviceName}</h3>
                        <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #7f1d1d;">${alert.message}</p>
                    </div>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 24px;">
                        <tr style="border-bottom: 1px solid #e2e8f0;">
                            <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #64748b; text-transform: uppercase;">Metric</td>
                            <td style="padding: 10px 0; font-weight: bold; font-size: 13px; color: #64748b; text-transform: uppercase; text-align: right;">Value</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 10px 0; font-size: 14px;">Provider / Scope</td>
                            <td style="padding: 10px 0; font-size: 14px; text-align: right; font-weight: bold;">${alert.provider.uppercase()} (${alert.accountId})</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 10px 0; font-size: 14px;">Actual Bill Cost</td>
                            <td style="padding: 10px 0; font-size: 14px; text-align: right; color: #ef4444; font-weight: bold;">$${String.format("%.2f", alert.actualCost)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 10px 0; font-size: 14px;">Expected Baseline</td>
                            <td style="padding: 10px 0; font-size: 14px; text-align: right; font-weight: bold;">$${String.format("%.2f", alert.expectedCost)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #f1f5f9;">
                            <td style="padding: 10px 0; font-size: 14px;">ML Confidence Score</td>
                            <td style="padding: 10px 0; font-size: 14px; text-align: right; font-weight: bold;">${String.format("%.1f", alert.anomalyScore * 100)}%</td>
                        </tr>
                    </table>
                    <p style="font-size: 12px; color: #94a3b8; line-height: 1.5; margin: 0;">
                        This anomaly detection alert was automatically triggered by the CloudGuard IsolationForest pipeline. Action is recommended to audit resource provisioning states.
                    </p>
                </div>
            </div>
        """.trimIndent()

        try {
            if (mailSender == null || fromEmail.contains("demo@")) {
                log.info("[MOCK EMAIL DISPATCH] -> To: {} | Subject: {} | HTML Body length: {} chars", toEmail, subject, htmlContent.length)
                return
            }

            log.info("Sending SMTP alert email to {}...", toEmail)
            val mimeMessage = mailSender.createMimeMessage()
            val helper = MimeMessageHelper(mimeMessage, "utf-8")
            helper.setText(htmlContent, true)
            helper.setTo(toEmail)
            helper.setSubject(subject)
            helper.setFrom(fromEmail)
            
            mailSender.send(mimeMessage)
            log.info("✅ SMTP Alert email sent successfully!")
        } catch (e: Exception) {
            log.error("❌ Failed to send SMTP email: ${e.message}")
        }
    }
}
