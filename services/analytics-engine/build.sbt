name := "analytics-engine"

version := "0.1"

scalaVersion := "2.13.12"

libraryDependencies ++= Seq(
  // Spark core & sql dependencies
  "org.apache.spark" %% "spark-core" % "3.5.0",
  "org.apache.spark" %% "spark-sql" % "3.5.0",
  
  // Spark Kafka connector for streaming queries
  "org.apache.spark" %% "spark-sql-kafka-0-10" % "3.5.0",
  
  // PostgreSQL driver to write aggregated analytics outputs
  "org.postgresql" % "postgresql" % "42.6.0",
  
  // Configuration parser helper
  "com.typesafe" % "config" % "1.4.2"
)

// Configure fork options to run Spark in separate JVM
fork := true
javaOptions ++= Seq(
  "--add-opens=java.base/java.lang=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED",
  "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED",
  "--add-opens=java.base/java.io=ALL-UNNAMED",
  "--add-opens=java.base/java.net=ALL-UNNAMED",
  "--add-opens=java.base/java.nio=ALL-UNNAMED",
  "--add-opens=java.base/java.util=ALL-UNNAMED",
  "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED",
  "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED",
  "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED",
  "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED",
  "--add-opens=java.base/security=ALL-UNNAMED",
  "--add-opens=java.base/sun.security.action=ALL-UNNAMED"
)
