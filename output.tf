output "tidb" {
  value = "${join("\n", aws_instance.tidb.*.private_ip)}"
}

output "tikv" {
  value = "${join("\n", aws_instance.tikv.*.private_ip)}"
}

output "pd" {
  value = "${join("\n", aws_instance.pd.*.private_ip)}"
}

output "bastion_ip" {
  value = "${join("\n", aws_eip.bastion.*.public_ip)}"
}

output "monitor-dns" {
  value = "${join("\n", module.aws-elb.monitor-dns)}"
}

output "tidb-dns" {
  value = "${join("\n", module.aws-elb.tidb-dns)}"
}
