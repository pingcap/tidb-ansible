output "tidb-dns" {
  value = "${aws_elb.aws-elb-sql.*.dns_name}"
}

output "monitor-dns" {
  value = "${aws_elb.aws-elb-monitor.*.dns_name}"
}
