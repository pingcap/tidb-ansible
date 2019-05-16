output "tidb" {
  value = "${join(", ", aws_instance.tidb.*.private_ip)}"
}

output "tikv" {
  value = "${join(", ", aws_instance.tikv.*.private_ip)}"
}

output "pd" {
  value = "${join(", ", aws_instance.pd.*.private_ip)}"
}

output "bastion_ip" {
  value = "${join(", ", aws_eip.bastion.*.public_ip)}"
}

output "monitor-dns" {
  value = "${join(", ", module.aws-elb.monitor-dns)}"
}

output "tidb-dns" {
  value = "${join(", ", module.aws-elb.tidb-dns)}"
}
