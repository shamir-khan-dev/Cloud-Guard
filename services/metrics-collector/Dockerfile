# Build stage
FROM alpine:3.19 AS build
RUN apk add --no-cache g++ make cmake git bash libtool openssl-dev
WORKDIR /app
COPY . .
RUN mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release .. && make

# Run stage
FROM alpine:3.19
RUN apk add --no-cache libstdc++
WORKDIR /app
COPY --from=build /app/build/metrics-collector .
ENTRYPOINT ["./metrics-collector"]
