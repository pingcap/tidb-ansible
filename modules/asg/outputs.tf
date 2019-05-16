output "outbound" {
  value = "${aws_security_group.outbound.id}"
}

output "bastion-ssh" {
  value = "${aws_security_group.bastion-ssh.id}"
}

output "intranet" {
  value = "${aws_security_group.intranet.id}"
}

output "tikv" {
  value = "${aws_security_group.tikv.id}"
}

output "tidb" {
  value = "${aws_security_group.tidb.id}"
}

output "pd" {
  value = "${aws_security_group.pd.id}"
}

output "monitor" {
  value = "${aws_security_group.monitor.id}"
}

output "aws-monitor-elb" {
  value = "${aws_security_group.aws-monitor-elb.id}"
}

output "aws-sql-elb" {
  value = "${aws_security_group.aws-sql-elb.id}"
}
