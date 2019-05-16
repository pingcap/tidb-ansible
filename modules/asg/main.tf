resource "aws_security_group" "bastion-ssh" {
  name   = "pingcap-tidb-ssh-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-ssh-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-ssh-connections" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.bastion-ssh.id}"
}

resource "aws_security_group" "outbound" {
  name   = "pingcap-tidb-outbound-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-outbound-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-all-out-traffic" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "ALL"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.outbound.id}"
}

resource "aws_security_group" "tidb" {
  name   = "pingcap-tidb-tidb-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-tidb-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-tidb-4000-connections" {
  type              = "ingress"
  from_port         = 4000
  to_port           = 4000
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.tidb.id}"
}

resource "aws_security_group_rule" "allow-tidb-10080-connections" {
  type              = "ingress"
  from_port         = 10080
  to_port           = 10080
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.tidb.id}"
}

resource "aws_security_group" "tikv" {
  name   = "pingcap-tidb-tikv-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-tikv-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-tikv-20160-connections" {
  type              = "ingress"
  from_port         = 20160
  to_port           = 20160
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.tikv.id}"
}

resource "aws_security_group_rule" "allow-tikv-20180-connections" {
  type              = "ingress"
  from_port         = 20180
  to_port           = 20180
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.tikv.id}"
}

resource "aws_security_group" "pd" {
  name   = "pingcap-tidb-pd-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-pd-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-pd-use-connections" {
  type              = "ingress"
  from_port         = 2379
  to_port           = 2379
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.pd.id}"
}

resource "aws_security_group_rule" "allow-pd-peer-connections" {
  type              = "ingress"
  from_port         = 2380
  to_port           = 2380
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.pd.id}"
}

resource "aws_security_group" "monitor" {
  name   = "pingcap-tidb-monitor-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-monitor-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-monitor-prometheus-connections" {
  type              = "ingress"
  from_port         = 0
  to_port           = 9090
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.monitor.id}"
}

resource "aws_security_group_rule" "allow-monitor-pushgateway-connections" {
  type              = "ingress"
  from_port         = 0
  to_port           = 9091
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.monitor.id}"
}

resource "aws_security_group_rule" "allow-monitor-grafana-connections" {
  type              = "ingress"
  from_port         = 3000
  to_port           = 3000
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.monitor.id}"
}

resource "aws_security_group_rule" "allow-monitor-grafana-collector" {
  type              = "ingress"
  from_port         = 8686
  to_port           = 8686
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.monitor.id}"
}

resource "aws_security_group_rule" "allow-monitor-tidb-connections" {
  type              = "ingress"
  from_port         = 10080
  to_port           = 10080
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.monitor.id}"
}

resource "aws_security_group" "intranet" {
  name   = "pingcap-tidb-intranet-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-intranet-securitygroup"
  }
}

resource "aws_security_group_rule" "allow-intranet-ssh-connections" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.intranet.id}"
}

resource "aws_security_group_rule" "allow-intranet-node-exporter-connections" {
  type              = "ingress"
  from_port         = 9100
  to_port           = 9100
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.intranet.id}"
}

resource "aws_security_group_rule" "allow-intranet-blackbox-connections" {
  type              = "ingress"
  from_port         = 9115
  to_port           = 9115
  protocol          = "TCP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.intranet.id}"
}

resource "aws_security_group_rule" "allow-intranet-icmp-connections" {
  type              = "ingress"
  from_port         = 8
  to_port           = 0
  protocol          = "ICMP"
  cidr_blocks       = ["10.0.0.0/16"]
  security_group_id = "${aws_security_group.intranet.id}"
}

resource "aws_security_group" "aws-sql-elb" {
  name   = "pingcap-tidb-sql-securitygroup-elb"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-sql-securitygroup-elb"
  }
}

resource "aws_security_group_rule" "aws-allow-tidb-access" {
  type              = "ingress"
  from_port         = 4000
  to_port           = 4000
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-sql-elb.id}"
}

resource "aws_security_group_rule" "aws-allow-sql-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "ALL"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-sql-elb.id}"
}

resource "aws_security_group" "aws-monitor-elb" {
  name   = "pingcap-tidb-monitor-securitygroup-elb"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-tidb-monitor-securitygroup-elb"
  }
}

resource "aws_security_group_rule" "aws-allow-tidb-monitor-access" {
  type              = "ingress"
  from_port         = 3000
  to_port           = 3000
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-monitor-elb.id}"
}

resource "aws_security_group_rule" "aws-allow-tidb-monitor-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "ALL"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-monitor-elb.id}"
}

### for rds demo
resource "aws_security_group" "aws-rds-demo" {
  name   = "pingcap-rds-demo-securitygroup"
  vpc_id = "${var.aws_vpc_id}"

  tags {
    Name = "pingcap-rds-demo-securitygroup"
  }
}

resource "aws_security_group_rule" "aws-allow-rds-demo-access" {
  type              = "ingress"
  from_port         = 3306
  to_port           = 3306
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-rds-demo.id}"
}

resource "aws_security_group_rule" "aws-allow-rds-demo-egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "ALL"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = "${aws_security_group.aws-rds-demo.id}"
}
