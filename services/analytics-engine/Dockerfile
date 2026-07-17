# Build stage
FROM hseeberger/scala-sbt:eclipse-temurin-17.0.2_1.6.2_2.13.8 AS build
WORKDIR /app
COPY build.sbt .
COPY src ./src
RUN sbt assembly || sbt package

# Run stage
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=build /app/target/scala-2.13/*.jar analytics-engine.jar
ENTRYPOINT ["java", "-jar", "analytics-engine.jar"]
