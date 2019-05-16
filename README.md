# tidb-aws-terraform
Handy terraform scripts for running TiDB on AWS

### Quick Start
1. Download and install terraform(https://www.terraform.io/downloads.html)
2. git clone this project，and execute `terraform init`
3. modify variables.tf, fill with the cluster topology
4. execute `terraform plan`, enter the access key and secret key as prompted
5. Make sure terraform generates right plan, and execute `terraform apply`, enter the access key and secret key as prompted
6. After Step 5, you can see the public IP of relay-server，ssh to the replay-server, the tidb-ansible directory will be on /home/ec2-user/tidb-ansible
7. After Step 5, you also can see the tidb-dns and monitor-dns, and can use these two DNS to access the monitoring and database
8. execute `terraform destroy` to destroy all resources when you do not need to use these resources

### Resource Overview
1. Deploy region

	* us-east-1

2. Default EC2 instance type

	| type  | instanceType  | counts | typeOfSubnet|
	| :-: |:-:| :-:| :-: |
	| bastion | t2.micro   | 1 | public  |
	| tidb    | c4.4xlarge | 3 | priveta |
	| tikv    | i3.2xlarge   | 3 | private |
	| pd      | i3.xlarge | 3 | private |
	| monitor | t2.xlarge   | 1 | private |

3. Network resource

	* 1 VPC
	* 1 public subnet
	* 1 private subnet
	* 1 internet gateway
	* 1 nat gateway

5. ELB resrouce

	* tidb provides ELB, expose port 4000
	* tidb monitor ELB，expose port 3000

	> ELB is in public subnet

6. Security group
	* All the ports TiDB needs

7. Storage resource
 	* monitor node has a 200GB EBS, tikv nodes have 1.7T NVMe SSD, pd nodes have 880 GB NVMe SSD

8. AWS key pair

9. Generating Template File for TiDB ansible
	* Generate [TiDB-Ansible](https://github.com/pingcap/tidb-ansible) 's inventory.ini

### Query AMI information
1. First refer to this [document](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) to install the AWS cli tool.
2. Configure the local AWS cli tool, ~/.aws/config is configured as follows:

```
[default]
region=us-east-1  # Fill in the name of region you need to operate.
output=json
```
touch ~/.aws/credentials, fill with your aws_access_key and aws_secret_key as follows:

 ```
[default]
aws_access_key_id=xxx
aws_secret_access_key=xxx
```
3. Execute the following command after the above steps are completed.

```shell
aws ec2 describe-images --filters "Name=name,Values=amzn2-ami-hvm-*" "Name=virtualization-type,Values=hvm"
```
Select an AMI from the returned AMI list, modify main.tf file and fill in the `OwnerId` value in the list of owners fields in the `data "aws_ami" "distro"`.
