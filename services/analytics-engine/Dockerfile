# Build stage with dependency caching
FROM sbtscala/scala-sbt:eclipse-temurin-17.0.4_1.7.1_2.13.8 AS build
WORKDIR /app

# Pre-fetch SBT dependencies for layer caching
COPY build.sbt .
RUN sbt update

# Copy source code and build assembly JAR
COPY src ./src
RUN sbt assembly || sbt package

# Lean Runtime Stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/scala-2.13/*.jar analytics-engine.jar

# Enforce container-aware JVM memory management
ENTRYPOINT ["java", "-XX:+UseG1GC", "-XX:MaxRAMPercentage=75.0", "-jar", "analytics-engine.jar"]
