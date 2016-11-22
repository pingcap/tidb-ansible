# -*- hcl -*-

output "tikv_ip" {
  value = "${join(",", aws_instance.tikv.*.public_ip)}"
}

output "tidb_ip" {
  value = "${join(",", aws_instance.tidb.*.public_ip)}"
}

# output "pd_ip" {
#   value = "${join(",", aws_instance.pd.*.public_ip)}"
# }
