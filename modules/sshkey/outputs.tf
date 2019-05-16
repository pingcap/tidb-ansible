output "key_name" {
  value = "${aws_key_pair.generated.key_name}"
}

output "private_key_pem" {
  value = "${tls_private_key.pingcap-generated.private_key_pem}"
}

output "private_key_path" {
  value = "${local.private_key_filename}"
}
