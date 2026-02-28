# Terraform AWS VPC Module
# Generated from DevTools-CLI template
# Usage: terraform init && terraform plan && terraform apply

terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ============================================================================
# Variables
# ============================================================================
variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "{{ PROJECT_NAME }}"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "{{ VPC_CIDR }}"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "{{ REGION }}"
}

variable "availability_zones" {
  description = "Number of AZs to use"
  type        = number
  default     = {{ AZ_COUNT | default(3) }}
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway for private subnets"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Use single NAT Gateway for all AZs (cost optimization)"
  type        = bool
  default     = false
}

variable "enable_dns_hostnames" {
  description = "Enable DNS hostnames in VPC"
  type        = bool
  default     = true
}

variable "enable_dns_support" {
  description = "Enable DNS support in VPC"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags for resources"
  type        = map(string)
  default     = {}
}

# ============================================================================
# Data Sources
# ============================================================================
data "aws_availability_zones" "available" {
  state = "available"
}

# ============================================================================
# VPC
# ============================================================================
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  
  tags = merge(
    {
      Name        = "${var.project_name}-vpc"
      Environment = terraform.workspace
      ManagedBy   = "terraform"
    },
    var.tags
  )
}

# ============================================================================
# Internet Gateway
# ============================================================================
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(
    {
      Name = "${var.project_name}-igw"
    },
    var.tags
  )
}

# ============================================================================
# Public Subnets
# ============================================================================
resource "aws_subnet" "public" {
  count = var.availability_zones
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 4, count.index)
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(
    {
      Name = "${var.project_name}-public-${count.index + 1}"
      Type = "public"
    },
    var.tags
  )
}

# ============================================================================
# Private Subnets
# ============================================================================
resource "aws_subnet" "private" {
  count = var.availability_zones
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 4, count.index + var.availability_zones)
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = merge(
    {
      Name = "${var.project_name}-private-${count.index + 1}"
      Type = "private"
    },
    var.tags
  )
}

# ============================================================================
# Elastic IPs for NAT Gateways
# ============================================================================
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : var.availability_zones) : 0
  
  domain = "vpc"
  
  tags = merge(
    {
      Name = "${var.project_name}-nat-eip-${count.index + 1}"
    },
    var.tags
  )
  
  depends_on = [aws_internet_gateway.main]
}

# ============================================================================
# NAT Gateways
# ============================================================================
resource "aws_nat_gateway" "main" {
  count = var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : var.availability_zones) : 0
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(
    {
      Name = "${var.project_name}-nat-${count.index + 1}"
    },
    var.tags
  )
  
  depends_on = [aws_internet_gateway.main]
}

# ============================================================================
# Route Tables - Public
# ============================================================================
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(
    {
      Name = "${var.project_name}-public-rt"
      Type = "public"
    },
    var.tags
  )
}

resource "aws_route_table_association" "public" {
  count = var.availability_zones
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ============================================================================
# Route Tables - Private
# ============================================================================
resource "aws_route_table" "private" {
  count = var.availability_zones
  
  vpc_id = aws_vpc.main.id
  
  dynamic "route" {
    for_each = var.enable_nat_gateway ? [1] : []
    content {
      cidr_block     = "0.0.0.0/0"
      nat_gateway_id = var.single_nat_gateway ? aws_nat_gateway.main[0].id : aws_nat_gateway.main[count.index].id
    }
  }
  
  tags = merge(
    {
      Name = "${var.project_name}-private-rt-${count.index + 1}"
      Type = "private"
    },
    var.tags
  )
}

resource "aws_route_table_association" "private" {
  count = var.availability_zones
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# ============================================================================
# Outputs
# ============================================================================
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "nat_gateway_ids" {
  description = "NAT Gateway IDs"
  value       = var.enable_nat_gateway ? aws_nat_gateway.main[*].id : []
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}