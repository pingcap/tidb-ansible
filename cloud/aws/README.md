# AWS infrastructure

We use [Terraform](https://www.terraform.io) to start and destroy machines on AWS at our need.

1. Download terraform [here](https://www.terraform.io/downloads.html), and then extract terraform to your `$PATH`

    For example if `$HOME/bin` is in your `$PATH`
	```
    # for Mac OSX
    wget https://releases.hashicorp.com/terraform/0.7.11/terraform_0.7.11_darwin_amd64.zip
    unzip terraform_0.7.11_darwin_amd64.zip -d $HOME/bin
    # for Linux
    wget https://releases.hashicorp.com/terraform/0.7.11/terraform_0.7.11_linux_amd64.zip
    unzip terraform_0.7.11_linux_amd64.zip -d $HOME/bin

    # verify terraform installed correctly
    terraform version
    ```

2. Prepare AWS access key and ssh key pair

   ```sh
   $ mkdir -p $HOME/.aws
   $ cat $HOME/.aws/config
   [default]
   region=cn-north-1
   $ cat $HOME/.aws/credentials
   [default]
   aws_access_key_id=YOUR_ACCESS_KEY
   aws_secret_access_key=YOUR_SECRET_KEY
   $ chmod 400 $HOME/.ssh/pingcap.pem
   ```

3. Modify variables.tf and start AWS instances

   By default terraform will launch 4 ubuntu-14.04 instances, 3 for
   TiKV and 1 for both Pd and TiDB. If you want to deploy pd and tidb
   on different instances, uncomment `resource "aws_instance" "pd" {}`
   block in main.tf and `output "pd_ip" {}` block in outputs.tf.

   Normally you only need to change `servers`, `instance_type`,
   variable in variables.tf. Look at the table below to learn more
   about `instance_type`. These types provide physical disks as
   instance store which has better performance than EBS, other not
   listed types only provide EBS.

   | Type       | CPU                                               | Memory(GiB) | Storage(GiB)  | Price(¥/hour) |
   |------------+---------------------------------------------------+-------------+---------------+---------------|
   | m3.medium  | 3 ECUs, 1 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2    |        3.75 | 1x4 (SSD)     |         0.868 |
   | m3.large   | 6.5 ECUs, 2 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2  |         7.5 | 1x32 (SSD)    |         1.735 |
   | m3.xlarge  | 13 ECUs, 4 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |          15 | 2x40 (SSD)    |         3.471 |
   | m3.2xlarge | 26 ECUs, 8 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |          30 | 2x80 (SSD)    |         6.942 |
   | c3.large   | 7 ECUs, 2 vCPUs, 2.8 GHz, Intel Xeon E5-2680v2    |        3.75 | 2x16 (SSD)    |         1.054 |
   | c3.xlarge  | 14 ECUs, 4 vCPUs, 2.8 GHz, Intel Xeon E5-2680v2   |         7.5 | 2x40 (SSD)    |         2.109 |
   | c3.2xlarge | 28 ECUs, 8 vCPUs, 2.8 GHz, Intel Xeon E5-2680v2   |          15 | 2x80 (SSD)    |         4.217 |
   | c3.4xlarge | 55 ECUs, 16 vCPUs, 2.8 GHz, Intel Xeon E5-2680v2  |          30 | 2x160 (SSD)   |         8.434 |
   | c3.8xlarge | 108 ECUs, 32 vCPUs, 2.8 GHz, Intel Xeon E5-2680v2 |          60 | 2x320 (SSD)   |        16.869 |
   | r3.large   | 6.5 ECUs, 2 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2  |          15 | 1x32 (SSD)    |        2.4509 |
   | r3.xlarge  | 13 ECUs, 4 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |        30.5 | 1x80 (SSD)    |        4.9018 |
   | r3.2xlarge | 26 ECUs, 8 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |          61 | 1x160 (SSD)   |        9.8036 |
   | r3.4xlarge | 52 ECUs, 16 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2  |         122 | 1x320 (SSD)   |       19.6073 |
   | r3.8xlarge | 104 ECUs, 32 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2 |         244 | 2x320 (SSD)   |       39.2147 |
   | d2.xlarge  | 14 ECUs, 4 vCPUs, 2.4 GHz, Intel Xeon E52676v3    |        30.5 | 3x2048 (HDD)  |         6.673 |
   | d2.2xlarge | 28 ECUs, 8 vCPUs, 2.4 GHz, Intel Xeon E52676v3    |          61 | 6x2048 (HDD)  |        13.345 |
   | d2.4xlarge | 56 ECUs, 16 vCPUs, 2.4 GHz, Intel Xeon E52676v3   |         122 | 12x2048 (HDD) |        26.690 |
   | d2.8xlarge | 116 ECUs, 36 vCPUs, 2.4 GHz, Intel Xeon E52676v3  |         244 | 24x2048 (HDD) |        53.380 |
   | i2.xlarge  | 14 ECUs, 4 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |        30.5 | 1x800 (SSD)   |        10.204 |
   | i2.2xlarge | 27 ECUs, 8 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2   |          61 | 2x800 (SSD)   |        20.407 |
   | i2.4xlarge | 53 ECUs, 16 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2  |         122 | 4x800 (SSD)   |        40.815 |
   | i2.8xlarge | 104 ECUs, 32 vCPUs, 2.5 GHz, Intel Xeon E5-2670v2 |         244 | 8x800 (SSD)   |         81.63 |


   Sadly only one disk can be used as data store currently, and will
   be mounted under `/data`

   To preview what resources will be created, run `terraform
   plan`. It's always a good practice to run `terraform plan` before
   `terraform apply` and `terraform destroy`. If all seems ok, you can
   run `terraform apply` to create actual resources. wait some minutes
   and instance IPs will be printed at the end of execution.

   After `terraform apply` executed successfully, you can ssh into
   these instances by `ssh -i ~/.ssh/pingcap.pem ubuntu@IP_OF_INSTANCE`

   After finishing your test on AWS, you should destroy machines by
   `terraform destroy` to save money.

   **Do not delete terraform.tfstate before destroying instances**,
   actually this should be checked into git.

## TODO

* Multiple tests on the same VPC maybe conflict with each other
