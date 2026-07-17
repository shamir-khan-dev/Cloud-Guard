package com.cloudguard.analytics

import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.util.Properties

object Main {
  def main(args: Array[String]): Unit = {
    println("🚀 Starting CloudGuard Scala Analytics Engine...")

    // Configuration variables from Environment
    val kafkaBrokers = sys.env.getOrElse("KAFKA_BROKERS", "localhost:9092")
    val dbHost = sys.env.getOrElse("DB_HOST", "localhost")
    val dbPort = sys.env.getOrElse("DB_PORT", "5432")
    val dbName = sys.env.getOrElse("DB_NAME", "cloudguard_db")
    val dbUser = sys.env.getOrElse("DB_USER", "cloudguard_user")
    val dbPassword = sys.env.getOrElse("DB_PASSWORD", "cloudguard_password")
    
    val jdbcUrl = s"jdbc:postgresql://$dbHost:$dbPort/$dbName"
    val connectionProperties = new Properties()
    connectionProperties.setProperty("user", dbUser)
    connectionProperties.setProperty("password", dbPassword)
    connectionProperties.setProperty("driver", "org.postgresql.Driver")

    // 1. Initialize Spark Session
    val spark = SparkSession.builder()
      .appName("CloudGuardAnalytics")
      .master(sys.env.getOrElse("SPARK_MASTER", "local[*]"))
      .getOrCreate()

    import spark.implicits._

    // Set Spark log level to WARN to reduce clutter
    spark.sparkContext.setLogLevel("WARN")

    // 2. Define schema for incoming raw metrics JSON
    val metricSchema = new StructType()
      .add("provider", StringType, nullable = false)
      .add("accountId", StringType, nullable = false)
      .add("serviceName", StringType, nullable = false)
      .add("region", StringType, nullable = false)
      .add("costUsd", DoubleType, nullable = false)
      .add("usageAmount", DoubleType, nullable = true)
      .add("usageUnit", StringType, nullable = true)
      .add("timestamp", StringType, nullable = false)

    println(s"🔌 Connecting to Kafka Brokers: $kafkaBrokers")

    // 3. Connect Structured Streaming to Kafka topic
    val kafkaStream = spark.readStream
      .format("kafka")
      .option("kafka.bootstrap.servers", kafkaBrokers)
      .option("subscribe", "raw-metrics")
      .option("startingOffsets", "latest")
      .load()

    // 4. Transform and parse messages
    // The message payload is in the 'value' column as Binary
    val parsedStream = kafkaStream
      .selectExpr("CAST(value AS STRING) as json_payload")
      .select(from_json($"json_payload", metricSchema).as("metric"))
      .select("metric.*")
      .withColumn("timestamp", to_timestamp($"timestamp", "yyyy-MM-dd'T'HH:mm:ss'Z'"))

    // 5. Cost aggregations (calculate total cost per service, region and account over a window)
    val aggregatedCosts = parsedStream
      .groupBy(
        window($"timestamp", "1 minute", "10 seconds"),
        $"provider",
        $"accountId",
        $"serviceName",
        $"region"
      )
      .agg(
        sum("costUsd").as("total_cost_usd"),
        sum("usageAmount").as("total_usage_amount")
      )

    println("📡 Streaming queries initiated. Awaiting incoming metrics...")

    // 6. Output stream writer: Console output for verification + PostgreSQL sink
    val query = aggregatedCosts.writeStream
      .outputMode("complete")
      .foreachBatch { (batchDF, batchId) =>
        println(s"\n--- Processed Batch #$batchId at ${java.time.Instant.now()} ---")
        
        // Show raw results in Spark logs
        batchDF.show(5, truncate = false)

        // Write batch results to PostgreSQL cost_metrics table
        try {
          // Map schema to target Postgres cost_metrics database table
          val mappedDF = batchDF
            .select(
              // Let DB auto-generate the ID, or Map fields directly
              $"provider",
              $"accountId",
              $"serviceName",
              $"region",
              $"total_cost_usd".as("cost_usd"),
              $"total_usage_amount".as("usage_amount"),
              $"window.start".as("period_start"),
              $"window.end".as("period_end")
            )
          
          println(s"💾 Saving Spark batch to PostgreSQL table: cost_metrics...")
          
          // Connect to PostgreSQL cloud accounts to find matching cloud_account_id
          // For simplicity in mock setup, write directly or fallback gracefully
          mappedDF.write
            .mode("append")
            .jdbc(jdbcUrl, "cost_metrics", connectionProperties)
            
          println("✅ Saved successfully!")
        } catch {
          case e: Exception =>
            println(s"⚠️  PostgreSQL write failed: ${e.getMessage}. Running in console-only fallback mode.")
        }
      }
      .start()

    query.awaitTermination()
  }
}
