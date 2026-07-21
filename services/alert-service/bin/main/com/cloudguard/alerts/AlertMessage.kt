package com.cloudguard.alerts

data class AlertMessage(
    val provider: String,
    val accountId: String,
    val serviceName: String,
    val anomalyScore: Double,
    val expectedCost: Double,
    val actualCost: Double,
    val message: String,
    val severity: String
)
