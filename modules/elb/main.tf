resource "aws_elb" "aws-elb-sql" {
  name            = "pingcap-tidb-sql-elb"
  subnets         = ["${var.subnet_public_ids}"]
  security_groups = ["${var.asg_elb_sql_id}"]

  listener {
    instance_port     = 4000
    instance_protocol = "tcp"
    lb_port           = 4000
    lb_protocol       = "tcp"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "TCP:4000"
    interval            = 30
  }

  instances                   = ["${var.tidb_instance_ids}"]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags {
    Name = "pingcap-tidb-sql-elb"
  }
}

resource "aws_elb" "aws-elb-monitor" {
  name            = "pingcap-tidb-monitor-elb"
  subnets         = ["${var.subnet_public_ids}"]
  security_groups = ["${var.asg_elb_monitor_id}"]

  listener {
    instance_port     = 3000
    instance_protocol = "tcp"
    lb_port           = 3000
    lb_protocol       = "tcp"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:3000/api/health"
    interval            = 30
  }

  instances                   = ["${var.monitor_instance_ids}"]
  cross_zone_load_balancing   = true
  idle_timeout                = 400
  connection_draining         = true
  connection_draining_timeout = 400

  tags {
    Name = "pingcap-tidb-monitor-elb"
  }
}
