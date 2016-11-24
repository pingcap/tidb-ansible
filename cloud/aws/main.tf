# -*- hcl-*-

provider "aws" {
  region = "${var.aws_region}"
}

resource "aws_security_group" "tidb" {
  name = "tidb-sg"
  description = "tidb cluster traffic"
  vpc_id = "${var.vpc_id}"
  ingress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    self = true
  }
  # allow all ingress traffic from default VPC
  ingress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["${var.cidr_blocks["vpc"]}"]
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  # change office to public will allow access from any IP
  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["${var.cidr_blocks["office"]}"]
  }
  ingress {
    from_port = "${var.grafana_port}"
    to_port = "${var.grafana_port}"
    protocol = "tcp"
    cidr_blocks = ["${var.cidr_blocks["office"]}"]
  }
  ingress {
    from_port = "${var.prometheus_port}"
    to_port = "${var.prometheus_port}"
    protocol = "tcp"
    cidr_blocks = ["${var.cidr_blocks["office"]}"]
  }
  ingress {
    from_port = "${var.tidb_port}"
    to_port = "${var.tidb_port}"
    protocol = "tcp"
    cidr_blocks = ["${var.cidr_blocks["office"]}"]
  }
}


resource "aws_instance" "tikv" {
  ami = "${var.ami["ubuntu"]}"
  instance_type = "${var.instance_type["tikv"]}"
  key_name = "${var.ssh_key_name}"
  count = "${var.servers["tikv"]}"
  subnet_id = "${var.subnet["a"]}"
  vpc_security_group_ids = ["${aws_security_group.tidb.id}"]
  connection {
    user = "ubuntu"
    agent = false
    private_key = "${file(format("~/.ssh/%s.pem", var.ssh_key_name))}"
  }
  tags {
    Name = "tikv-${count.index}"
  }
  ephemeral_block_device {
    device_name = "xvdb"
    virtual_name = "ephemeral0"
  }
  provisioner "file" {
    source = "ustc-ubuntu-sources.list"
    destination = "/tmp/sources.list"
  }
  provisioner "remote-exec" {
    inline = [
      "sudo cp /tmp/sources.list /etc/apt/sources.list",
      "sudo timedatectl set-timezone ${var.timezone}",
      "sudo apt-get update && sudo apt-get install -y ntp",
      "sudo umount /mnt || true",
      "sudo mkdir -p /data && sudo mount /dev/xvdb /data",
    ]
  }
}

resource "aws_instance" "tidb" {
  ami = "${var.ami["ubuntu"]}"
  instance_type = "${var.instance_type["tidb"]}"
  key_name = "${var.ssh_key_name}"
  count = "${var.servers["tidb"]}"
  subnet_id = "${var.subnet["a"]}"
  vpc_security_group_ids = ["${aws_security_group.tidb.id}"]
  connection {
    user = "${var.user["ubuntu"]}"
    agent = false
    private_key = "${file(format("~/.ssh/%s.pem", var.ssh_key_name))}"
  }
  tags {
    Name = "tidb-${count.index}"
  }
  ephemeral_block_device {
    device_name = "xvdb"
    virtual_name = "ephemeral0"
  }
  provisioner "file" {
    source = "ustc-ubuntu-sources.list"
    destination = "/tmp/sources.list"
  }
  provisioner "remote-exec" {
    inline = [
      "sudo cp /tmp/sources.list /etc/apt/sources.list",
      "sudo timedatectl set-timezone ${var.timezone}",
      "sudo apt-get update && sudo apt-get install -y ntp",
      "sudo umount /mnt || true",
      "sudo mkdir -p /data && sudo mount /dev/xvdb /data",
    ]
  }
}

# # if you want to deploy pd and tidb on the same instance, comment following block
# resource "aws_instance" "pd" {
#   ami = "${var.ami["ubuntu"]}"
#   instance_type = "${var.instance_type["pd"]}"
#   key_name = "${var.ssh_key_name}"
#   count = "${var.servers["pd"]}"
#   subnet_id = "${var.subnet["a"]}"
#   security_groups = ["${aws_security_group.tidb.id}"]
#   connection {
#     user = "ubuntu"
#     agent = false
#     private_key = "${file(format("~/.ssh/%s.pem", var.ssh_key_name))}"
#   }
#   tags {
#     Name = "pd-${count.index}"
#   }
#   ephemeral_block_device {
#     device_name = "xvdb"
#     virtual_name = "ephemeral0"
#   }
#   provisioner "file" {
#     source = "ustc-ubuntu-sources.list"
#     destination = "/tmp/sources.list"
#   }
#   provisioner "remote-exec" {
#     inline = [
#       "sudo cp /tmp/sources.list /etc/apt/sources.list",
#       "sudo timedatectl set-timezone ${var.timezone}",
#       "sudo apt-get update && sudo apt-get install -y ntp",
#       "sudo umount /mnt || true",
#        "sudo mkdir -p /data && sudo mount /dev/xvdb /data",
#     ]
#   }
# }
