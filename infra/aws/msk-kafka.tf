# 1. Security Group for MSK Kafka Cluster
resource "aws_security_group" "msk_sg" {
  name        = "cloudguard-msk-sg"
  description = "Security group for Managed Kafka Cluster"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Open only to internal VPC microservices
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "CloudGuard MSK SG"
  }
}

# 2. AWS MSK (Managed Streaming for Kafka) Cluster
resource "aws_msk_cluster" "kafka" {
  cluster_name           = "cloudguard-kafka"
  kafka_version          = "3.4.0"
  number_of_broker_nodes = 2

  broker_node_group_info {
    instance_type = "kafka.t3.small" # Smallest cost-optimized broker node
    client_subnets = var.subnet_ids
    security_groups = [aws_security_group.msk_sg.id]
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "PLAINTEXT" # For simple internal VPC traffic, TLS can be added
      in_cluster    = true
    }
  }

  tags = {
    Environment = "production"
    Project     = "CloudGuard"
  }
}

output "zookeeper_connect_string" {
  value       = aws_msk_cluster.kafka.zookeeper_connect_string
  description = "MSK ZooKeeper cluster connection endpoints"
}

output "bootstrap_brokers" {
  value       = aws_msk_cluster.kafka.bootstrap_brokers_plaintext
  description = "MSK Plaintext Bootstrap brokers string"
}
