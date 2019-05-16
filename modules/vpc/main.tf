# State can be either: available, information, impaired, or unavailable
resource "aws_vpc" "vpc_tidb_cluster" {
  # count      = "${var.external_vpc_id == "" ? 1 : 0}"
  cidr_block = "${var.vpc_cidr_block}"

  tags {
    Name = "VPC-tidb-cluster"
  }
}

resource "aws_internet_gateway" "vpc_tidb_igw" {
  count  = "${length(var.public_subnets) > 0 ? 1 : 0}"
  vpc_id = "${aws_vpc.vpc_tidb_cluster.id}"
}

resource "aws_eip" "nat" {
  count = "${var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.azs)) : 0}"
}

resource "aws_nat_gateway" "vpc_tidb_ngw" {
  count = "${var.enable_nat_gateway ? (var.single_nat_gateway ? 1 : length(var.azs)) : 0}"

  allocation_id = "${element(aws_eip.nat.*.id, (var.single_nat_gateway ? 0 : count.index))}"
  subnet_id     = "${element(aws_subnet.public.*.id, (var.single_nat_gateway ? 0 : count.index))}"

  depends_on = ["aws_internet_gateway.vpc_tidb_igw"]
}

resource "aws_subnet" "public" {
  vpc_id            = "${aws_vpc.vpc_tidb_cluster.id}"
  count             = "${length(var.public_subnets)}"
  availability_zone = "${element(slice(var.azs,0,length(var.public_subnets)),count.index)}"
  cidr_block        = "${element(var.public_subnets,count.index)}"

  tags {
    Name = "Public-Subnet-TiDB"
    Tier = "Public"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = "${aws_vpc.vpc_tidb_cluster.id}"
  count             = "${length(var.private_subnets)}"
  availability_zone = "${element(slice(var.azs,0,length(var.private_subnets)),count.index)}"
  cidr_block        = "${element(var.private_subnets,count.index)}"

  tags {
    Name = "Private-Subnet-TiDB"
    Tier = "Private"
  }
}

resource "aws_route_table" "public" {
  count = "${length(var.public_subnets) > 0 ? 1 : 0}"

  vpc_id = "${aws_vpc.vpc_tidb_cluster.id}"
}

resource "aws_route" "public_internet" {
  count                  = "${length(var.public_subnets) > 0 ? 1 : 0}"
  route_table_id         = "${aws_route_table.public.id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.vpc_tidb_igw.id}"
}

resource "aws_route_table_association" "public" {
  count          = "${length(var.public_subnets)}"
  subnet_id      = "${element(aws_subnet.public.*.id,count.index)}"
  route_table_id = "${aws_route_table.public.id}"
}

resource "aws_route_table" "private" {
  count = 1

  vpc_id = "${aws_vpc.vpc_tidb_cluster.id}"
}

resource "aws_route" "private_nat_gateway" {
  count = 1

  route_table_id         = "${element(aws_route_table.private.*.id, count.index)}"
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = "${element(aws_nat_gateway.vpc_tidb_ngw.*.id, count.index)}"
}

resource "aws_route_table_association" "private" {
  count          = "${length(var.private_subnets)}"
  subnet_id      = "${element(aws_subnet.private.*.id,count.index)}"
  route_table_id = "${aws_route_table.private.id}"
}
