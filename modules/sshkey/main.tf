locals {
  private_key_filename = "keys/private.pem"
  public_key_filename  = "keys/public.pem"
}

resource "tls_private_key" "pingcap-generated" {
  count = 1

  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "aws_key_pair" "generated" {
  count      = 1
  depends_on = ["tls_private_key.pingcap-generated"]
  key_name   = "pingcap-generated"
  public_key = "${tls_private_key.pingcap-generated.public_key_openssh}"
}

resource "local_file" "public_key_openssh" {
  count      = 1
  depends_on = ["tls_private_key.pingcap-generated"]
  content    = "${tls_private_key.pingcap-generated.public_key_openssh}"
  filename   = "${local.public_key_filename}"
}

resource "local_file" "private_key_pem" {
  count      = 1
  depends_on = ["tls_private_key.pingcap-generated"]
  content    = "${tls_private_key.pingcap-generated.private_key_pem}"
  filename   = "${local.private_key_filename}"
}
