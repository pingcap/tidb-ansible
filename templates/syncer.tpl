[syncer]
${tidb_server}

[all:vars]
rds_endpoint = ${rds_address}
rds_port = ${rds_port}
rds_user = ${rds_user}
rds_password = ${rds_password}

tidb_host = ${tidb_server}
tidb_port = 4000
tidb_user = root
deploy_user = ec2-user
deploy_dir = /home/ec2-user/deploy
