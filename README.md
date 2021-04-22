## :warning: End of project :warning:

[![development](https://img.shields.io/badge/development-halted-red.svg)](https://github.com/pingcap/tidb-ansible/issues/1365)

This project [has ended](https://github.com/pingcap/tidb-ansible/issues/1365), and **all development/maintenance activities have halted**.

As it is free software, people are free and welcome to fork and develop the codebase on their own.
However, to avoid any confusion, the original repository is archived and we recommend any further fork/development to proceed with an explicit rename and rebranding first.

We encourage all interested parties to mirror any relevant bits as we can't actively guarantee their existence in the future.

# Ansible Playbook for TiDB

## Overview
Ansible is an IT automation tool. It can configure systems, deploy software, and orchestrate more advanced IT tasks such as continuous deployments or zero downtime rolling updates.

TiDB-Ansible is a TiDB cluster deployment tool developed by PingCAP, based on Ansible playbook. TiDB-Ansible enables you to quickly deploy a new TiDB cluster which includes PD, TiDB, TiKV, and the cluster monitoring modules.
 
You can use the TiDB-Ansible configuration file to set up the cluster topology, completing all operation tasks with one click, including:
	
- Initializing the system, including creating the user for deployment, setting up the hostname, etc.
- Deploying the components
- Rolling update, including module survival detection
- Cleaning data
- Cleaning the environment
- Configuring monitoring modules

## Tutorial

- [English](https://docs.pingcap.com/tidb/v3.0/online-deployment-using-ansible)
- [简体中文](https://docs.pingcap.com/zh/tidb/v3.0/online-deployment-using-ansible)

## License
TiDB-Ansible is under the Apache 2.0 license. 
