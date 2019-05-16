Host ${bastion_host}
  StrictHostKeyChecking no
  User ec2-user
  IdentityFile ${identity_file}

Host ${list_hosts}
  StrictHostKeyChecking no
  ProxyCommand ssh -W %h:%p ec2-user@${bastion_host} -i ${identity_file}
