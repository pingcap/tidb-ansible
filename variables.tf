variable "aws_access_key" {
  type        = "string"
  description = "Your AWS access key id"
}

variable "aws_secret_key" {
  type        = "string"
  description = "Your AWS secret key"
}

variable "aws_region" {
  type        = "string"
  description = "The AWS region you want to create resources"
  default     = "us-east-1"
}

variable "public_subnets" {
  description = "Public Subnets CIDR"
  default     = ["10.0.0.0/24"]
}

variable "private_subnets" {
  description = "Private Subnets CIDR"
  default     = ["10.0.1.0/24"]
}

variable "vpc_cidr_block" {
  type        = "string"
  description = "CIDR block for AWS VPC(TiDB Cluster)"
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Should be true if you want to provision NAT Gateways for each of your private networks"
  default     = "true"
}

variable "single_nat_gateway" {
  description = "Should be true if you want to provision a single shared NAT Gateway across all of your private networks"
  default     = "true"
}

variable "tidb_instance_type" {
 type    = "string"
 default = "c5.4xlarge"
}

variable "tikv_instance_type" {
  type    = "string"
  default = "c5d.2xlarge"
}

variable "pd_instance_type" {
  type    = "string"
  default = "c5.2xlarge"
}

variable "monitor_instance_type" {
  type    = "string"
  default = "t2.xlarge"
}

variable "bastion_instance_type" {
  type    = "string"
  default = "t2.micro"
}

variable "tidb_count" {
	type = "string"
	description = "The numble of the tidb instances to be deployed"
	default = "2"
}

variable "tikv_count" {
	type = "string"
	description = "The numble of the tikv instances to be deployed"
	default = "3"
}

variable "pd_count" {
	type = "string"
	description = "The numble of the pd instances to be deployed"
	default = "3"
}

variable "tidb_version" {
	type = "string"
	description = "The version of the tidb cluster"
	default = "v3.0.0-rc.1"
}
