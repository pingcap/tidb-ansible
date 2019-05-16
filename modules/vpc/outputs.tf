output "aws_vpc_id" {
  value = "${aws_vpc.vpc_tidb_cluster.id}"
}

output "aws_subnet_ids_private" {
  value = ["${aws_subnet.private.*.id}"]
}

output "aws_subnet_ids_public" {
  value = ["${aws_subnet.public.*.id}"]
}
