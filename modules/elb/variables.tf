variable "subnet_public_ids" {
  type = "list"
}

variable "asg_elb_sql_id" {}

variable "tidb_instance_ids" {
	type = "list"
}

variable "asg_elb_monitor_id" {}

variable "monitor_instance_ids" {
	type = "list"
}
