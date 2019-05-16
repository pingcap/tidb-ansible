provider "aws" {
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  region     = "${var.aws_region}"
}

data "aws_availability_zones" "available" {}

module "aws-vpc" {
  source             = "modules/vpc"
  azs                = ["${data.aws_availability_zones.available.names[0]}"]
  public_subnets     = "${var.public_subnets}"
  private_subnets    = "${var.private_subnets}"
  vpc_cidr_block     = "${var.vpc_cidr_block}"
  enable_nat_gateway = "${var.enable_nat_gateway}"
  single_nat_gateway = "${var.single_nat_gateway}"
}

module "aws-elb" {
  source               = "modules/elb"
  tidb_instance_ids    = "${aws_instance.tidb.*.id}"
  monitor_instance_ids = "${aws_instance.monitor.*.id}"
  subnet_public_ids    = "${module.aws-vpc.aws_subnet_ids_public}"
  asg_elb_sql_id       = "${module.aws-asg.aws-sql-elb}"
  asg_elb_monitor_id   = "${module.aws-asg.aws-monitor-elb}"
}

module "aws-asg" {
  source     = "modules/asg"
  aws_vpc_id = "${module.aws-vpc.aws_vpc_id}"
}

module "ssh-key" {
  source = "modules/sshkey"
}

resource "null_resource" "sshkey-private" {
  triggers {
    private_content = "${module.ssh-key.private_key_pem}"
  }

  provisioner "local-exec" {
    command = "chmod 400 ${module.ssh-key.private_key_path}"
  }
}

data "aws_ami" "distro" {
  most_recent = true

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["137112412989"] #Amazon Linux 2
}

resource "aws_instance" "bastion" {
  count                  = 1
  ami                    = "${data.aws_ami.distro.id}"
  instance_type          = "${var.bastion_instance_type}"
  subnet_id              = "${element(module.aws-vpc.aws_subnet_ids_public, 0)}"
  key_name               = "${module.ssh-key.key_name}"
  vpc_security_group_ids = ["${module.aws-asg.bastion-ssh}", "${module.aws-asg.outbound}"]

  tags {
    Name = "PingCAP-Bastion-${count.index}"
  }
}

resource "null_resource" "bastion" {
  # Changes to any instance of the bastion requires re-provisioning
  triggers {
    bastion_instance_ids = "${join(",",aws_instance.bastion.*.id)}"
  }

  provisioner "file" {
    source      = "keys/private.pem"
    destination = "/home/ec2-user/.ssh/aws.key"

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }

  provisioner "file" {
    source      = "files/config"
    destination = "/home/ec2-user/.ssh/config"

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "null_resource" "bastion-init" {
  # Changes to any instance of the bastion requires re-provisioning
  triggers {
    bastion_instance_ids = "${join(",",aws_instance.bastion.*.id)}"
  }

  provisioner "file" {
    source      = "scripts/init_bastion.sh"
    destination = "/tmp/init_bastion.sh"

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/init_bastion.sh",
      "/tmp/init_bastion.sh ec2-user ${var.tidb_version}"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "aws_instance" "tidb" {
  count                  = "${var.tidb_count}"
  ami                    = "${data.aws_ami.distro.id}"
  instance_type          = "${var.tidb_instance_type}"
  subnet_id              = "${element(module.aws-vpc.aws_subnet_ids_private, count.index)}"
  key_name               = "${module.ssh-key.key_name}"
  vpc_security_group_ids = ["${module.aws-asg.intranet}", "${module.aws-asg.outbound}", "${module.aws-asg.tidb}"]

  tags {
    Name    = "PingCAP-TiDB-${count.index}"
    Cluster = "PingCAP-TiDB-Cluster"
    Role    = "TiDB-Server"
    Created = "Terraform"
    Init    = "True"
  }
}

resource "aws_instance" "tikv" {
  count                  = "${var.tikv_count}"
  ami                    = "${data.aws_ami.distro.id}"
  instance_type          = "${var.tikv_instance_type}"
  subnet_id              = "${element(module.aws-vpc.aws_subnet_ids_private, count.index)}"
  key_name               = "${module.ssh-key.key_name}"
  vpc_security_group_ids = ["${module.aws-asg.intranet}", "${module.aws-asg.outbound}", "${module.aws-asg.tikv}"]
  user_data              = "${file("files/attach_nvme.sh")}"

  tags {
    Name    = "PingCAP-TiKV-${count.index}"
    Cluster = "PingCAP-TiKV-Cluster"
    Role    = "TiKV-Server"
    Created = "Terraform"
    Init    = "True"
  }
}

resource "aws_instance" "pd" {
  count                  = "${var.pd_count}"
  ami                    = "${data.aws_ami.distro.id}"
  instance_type          = "${var.pd_instance_type}"
  subnet_id              = "${element(module.aws-vpc.aws_subnet_ids_private, count.index)}"
  key_name               = "${module.ssh-key.key_name}"
  vpc_security_group_ids = ["${module.aws-asg.intranet}", "${module.aws-asg.outbound}", "${module.aws-asg.pd}"]
  user_data              = "${file("files/attach_nvme.sh")}"

  tags {
    Name    = "PingCAP-PD-${count.index}"
    Cluster = "PingCAP-PD-Cluster"
    Role    = "PD-Sever"
    Created = "Terraform"
    Init    = "True"
  }
}

resource "aws_instance" "monitor" {
  count                  = 1
  ami                    = "${data.aws_ami.distro.id}"
  instance_type          = "${var.monitor_instance_type}"
  subnet_id              = "${element(module.aws-vpc.aws_subnet_ids_private, count.index)}"
  key_name               = "${module.ssh-key.key_name}"
  vpc_security_group_ids = ["${module.aws-asg.intranet}", "${module.aws-asg.outbound}", "${module.aws-asg.monitor}"]
  user_data              = "${file("files/attach_ebs.sh")}"

  ebs_block_device {
    device_name           = "/dev/sdg"
    volume_type           = "gp2"
    volume_size           = 200
    delete_on_termination = true
  }

  tags {
    Name    = "PingCAP-Monitor-${count.index}"
    Cluster = "PingCAP-Monitor-Cluster"
    Role    = "Monitoring-Server"
  }
}

resource "aws_eip" "bastion" {
  count = 1
}

resource "aws_eip_association" "eip_assoc" {
  instance_id   = "${aws_instance.bastion.id}"
  allocation_id = "${aws_eip.bastion.id}"
}

data "template_file" "inventory" {

  vars {
    list_tidb    = "${join(",",aws_instance.tidb.*.private_ip)}"
    list_tikv    = "${join(",",aws_instance.tikv.*.private_ip)}"
    list_pd      = "${join(",",aws_instance.pd.*.private_ip)}"
    list_monitor = "${join(",",aws_instance.monitor.*.private_ip)}"
  }
}

data "template_file" "ssh-bastion" {
  template = "${file("${path.module}/templates/ssh-bastion.tpl")}"

  vars {
    bastion_host  = "${aws_eip.bastion.public_ip}"
    identity_file = "${path.module}/${module.ssh-key.private_key_path}"
    list_hosts    = "${join(" ",concat(aws_instance.tidb.*.private_ip, aws_instance.tikv.*.private_ip, aws_instance.pd.*.private_ip, aws_instance.monitor.*.private_ip))}"
  }
}

resource "null_resource" "ssh-bastion" {
  triggers {
    template = "${data.template_file.ssh-bastion.rendered}"
  }

  provisioner "local-exec" {
    command = "echo '${data.template_file.ssh-bastion.rendered}' > ./ssh-bastion.conf"
  }
}

resource "null_resource" "bastion-ansible" {
  depends_on = ["null_resource.bastion-init"]

  provisioner "file" {
    source      = "scripts/init_ansible.sh"
    destination = "/tmp/init_ansible.sh"

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /tmp/init_ansible.sh",
      "/tmp/init_ansible.sh ${data.template_file.inventory.vars.list_tidb} ${data.template_file.inventory.vars.list_tikv} ${data.template_file.inventory.vars.list_pd} ${data.template_file.inventory.vars.list_monitor}"
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "null_resource" "bastion-local-prepare" {
  depends_on = ["null_resource.bastion-ansible"]

  provisioner "remote-exec" {
    inline = [
      "cd /home/ec2-user/tidb-ansible/",
      "ansible-playbook local_prepare.yml",
      "sleep 10",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "null_resource" "bastion-bootstrap" {
  depends_on = ["null_resource.bastion-local-prepare"]

  provisioner "remote-exec" {
    inline = [
      "cd /home/ec2-user/tidb-ansible/",
      "ansible-playbook bootstrap.yml",
      "sleep 10",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "null_resource" "bastion-deploy" {
  depends_on = ["null_resource.bastion-bootstrap"]

  provisioner "remote-exec" {
    inline = [
      "cd /home/ec2-user/tidb-ansible/",
      "ansible-playbook deploy.yml",
      "sleep 10",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}

resource "null_resource" "bastion-start" {
  depends_on = ["null_resource.bastion-deploy"]

  provisioner "remote-exec" {
    inline = [
      "cd /home/ec2-user/tidb-ansible/",
      "ansible-playbook start.yml",
      "sleep 10",
    ]

    connection {
      type        = "ssh"
      user        = "ec2-user"
      private_key = "${module.ssh-key.private_key_pem}"
      host        = "${aws_eip.bastion.public_ip}"
    }
  }
}
