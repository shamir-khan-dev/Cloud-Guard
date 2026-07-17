provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  default = "us-east-1"
}

variable "vpc_id" {
  type        = string
  description = "Target AWS VPC ID"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for DB Subnet Group"
}

# 1. DB Subnet Group
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "cloudguard-db-subnet-group"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "CloudGuard DB Subnet Group"
  }
}

# 2. Security Group for RDS PostgreSQL
resource "aws_security_group" "rds_sg" {
  name        = "cloudguard-rds-sg"
  description = "Allow inbound PostgreSQL traffic from VPC"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Restricted to VPC IP range
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "CloudGuard RDS SG"
  }
}

# 3. RDS PostgreSQL DB Instance
resource "aws_db_instance" "postgres" {
  identifier             = "cloudguard-postgres"
  allocated_storage      = 20
  max_allocated_storage  = 100
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = "db.t4g.micro" # Free-tier eligible / low cost ARM instance
  db_name                = "cloudguard_db"
  username               = "cloudguard_user"
  password               = var.db_password # Injected via variables
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true

  tags = {
    Environment = "production"
    Project     = "CloudGuard"
  }
}

variable "db_password" {
  type        = string
  sensitive   = true
  description = "Database master user password"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "PostgreSQL connection endpoint URI"
}
