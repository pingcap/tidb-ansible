variable "vpc_cidr_block" {
  type        = "string"
  description = "CIDR block for AWS VPC(TiDB Cluster)"
  default     = "10.0.0.0/16"
}

# variable "external_vpc_id" {
#   type        = "string"
#   description = "Existed VPC ID"
# }

variable "azs" {
  description = "AWS Availability Zones In the region"
  type        = "list"
}

variable "public_subnets" {
  description = "Public Subnets CIDR"
  default     = ["10.0.0.0/24", "10.0.2.0/24"]
}

variable "private_subnets" {
  description = "Private Subnets CIDR"
  default     = ["10.0.1.0/24"]
}

variable "enable_nat_gateway" {
  description = "Should be true if you want to provision NAT Gateways for each of your private networks"
  default     = false
}

variable "single_nat_gateway" {
  description = "Should be true if you want to provision a single shared NAT Gateway across all of your private networks"
  default     = false
}
