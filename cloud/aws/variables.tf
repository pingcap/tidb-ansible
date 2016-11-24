# -*- hcl -*-
variable "aws_region" {
  default = "cn-north-1"
}

variable "ssh_key_name" {
  default = "pingcap"		# $HOME/.ssh/pingcap.pem
}

variable "vpc_id" {
  default = "vpc-b3bc4bd7"
}

variable "subnet" {
  default = {
    a = "subnet-21d57056"	# cn-north-1a
    b = "subnet-de663cbb"	# cn-north-1b
  }
}

variable "cidr_blocks" {
  default = {
    vpc = "172.31.0.0/16"	# AWS default VPC
    public = "0.0.0.0/0"
    office = "103.250.227.80/32" # office IP address
  }
}

variable "tidb_port" {
  default = 4000
}

variable "grafana_port" {
  default = 3000
}

variable "prometheus_port" {
  default = 9090
}

variable "ami" {
  default = {
    ubuntu = "ami-0220b23b"	# ubuntu
    ec2 = "ami-7c15c111"	# amz linux
    debian = "ami-da69a1b7"
    redhat = "ami-52d1183f"
    suse = "ami-41559c2c"
  }
}

variable "user" {
  default = {
    ubuntu = "ubuntu"
    ec2 = "ec2-user"
    debian = "admin"
  }
}

variable "timezone" {
  default = "Asia/Shanghai"
}


variable "servers" { 		# number of servers
  default = {
    pd = 1
    tidb = 1
    tikv = 3
  }
}

variable "instance_type" {
  default = {
    pd = "c3.4xlarge"
    tikv = "c3.4xlarge"
    tidb = "c3.4xlarge"
  }
}
