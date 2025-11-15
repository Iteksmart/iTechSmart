# iTechSmart Suite - AWS Terraform Variables

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (development, staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be development, staging, or production."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.large"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 100
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "itechsmart_admin"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.medium"
}

variable "product_names" {
  description = "List of iTechSmart product names"
  type        = list(string)
  default = [
    "enterprise",
    "ninja",
    "analytics",
    "supreme",
    "hl7",
    "prooflink",
    "passport",
    "impactos",
    "legalai-pro",
    "dataflow",
    "pulse",
    "connect",
    "vault",
    "notify",
    "ledger",
    "copilot",
    "shield",
    "workflow",
    "marketplace",
    "cloud",
    "devops",
    "mobile",
    "ai",
    "compliance",
    "dataplatform",
    "customersuccess",
    "portmanager",
    "mdmagent",
    "qaqc",
    "thinktank",
    "sentinel",
    "forge",
    "sandbox"
  ]
}

variable "enable_monitoring" {
  description = "Enable CloudWatch monitoring"
  type        = bool
  default     = true
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
}