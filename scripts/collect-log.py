#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import datetime
import logging
import os
import shutil
import time

from subprocess import Popen, PIPE


def parse_opts():
    parser = argparse.ArgumentParser(description="TiDB Insight Scripts",
                                     epilog="This script is designed to be called by ansible playbook.")
    parser.add_argument("--log-dir", action="store", default=None,
                        help="Location of log files.")
    parser.add_argument("--retention", action="store", type=int, default=0,
                        help="Time of log retention policy, e.g.: 1d, 12h")
    parser.add_argument("--output", action="store", default=None,
                        help="The base directory path to store all log files.")
    parser.add_argument("--prefix", action="store", default=None,
                        help="The prefix of log files, will be the directory name of all logs, will be in the name of output tarball.")
    parser.add_argument("--alias", action="store", default=None,
                        help="The alias of this instance, will be in the name of output tarball.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False,
                        help="Print verbose output.")

    return parser.parse_args()


def run_cmd(cmd):
    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    return p.communicate()


# create target directory, do nothing if it already exists
def create_dir(path):
    try:
        os.mkdir(path)
        return path
    except OSError as e:
        # There is FileExistsError (devided from OSError) in Python 3.3+,
        # but only OSError in Python 2, so we use errno to check if target
        # dir already exists.
        import errno
        if e.errno == errno.EEXIST and os.path.isdir(path):
            # NOTE: It's not checked if output dir empty or not, any exist
            # file with conlfict name may be overwitten.
            return path
        else:
            logging.fatal(
                "Failed to preopare output dir, error is: %s" % str(e))
    return None


def get_hostname():
    import socket
    return socket.gethostname()


def compare_time(base_time, comp_timestamp, valid_range):
    if valid_range <= 0:
        return True
    threhold = datetime.timedelta(0, 0, 0, 0, 0, valid_range)  # hour
    delta_secs = base_time - comp_timestamp
    return datetime.timedelta(0, delta_secs) <= threhold


def get_filelist(base_dir, prefix, curr_time, retention_hour):
    valid_file_list = []
    for file in os.listdir(base_dir):
        fullpath = os.path.join(base_dir, file)
        if os.path.isdir(fullpath):
            # check for all sub-directories
            for f in get_filelist(fullpath, prefix, curr_time, retention_hour):
                valid_file_list.append(f)
        if not compare_time(curr_time, os.path.getmtime(fullpath), retention_hour):
            continue
        if file.startswith(prefix):
            valid_file_list.append(fullpath)
    return valid_file_list


def collect_log(args):
    # init values of args
    source_dir = args.log_dir
    if not os.path.isdir(source_dir):
        raise OSError("Source log path is not a directory.")
    output_base = args.output
    if not output_base:
        output_base = source_dir
    file_prefix = args.prefix
    retention_hour = args.retention
    host_alias = args.alias
    if not host_alias:
        host_alias = get_hostname()

    # the output tarball name
    output_name = "%s_%s" % (file_prefix, host_alias)
    # the full path of output directory
    output_dir = os.path.join(output_base, output_name)

    # prepare output directory
    if not create_dir(output_dir):
        raise OSError("Failed to preopare output dir")

    # copy valid log files to output directory
    file_list = get_filelist(source_dir, file_prefix,
                             time.time(), retention_hour)
    for file in file_list:
        if output_name in file:
            # Skip output files if source and output are the same directory
            continue
        shutil.copy(file, output_dir)
        logging.info("Logfile saved: %s", file)

    # compress output files to tarball
    os.chdir(output_base)
    cmd = ["tar",
           "--remove-files",
           "-zcf",
           "%s.tar.gz" % output_name,
           output_name]
    stdout, stderr = run_cmd(cmd)
    if not stderr and stderr != '':
        raise OSError(stderr)
    if not stdout and stdout != '':
        logging.info("tar output: %s" % stdout)


if __name__ == "__main__":
    args = parse_opts()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    #collect_log(args)
    try:
        collect_log(args)
    except Exception as e:
        logging.fatal(e)
        exit(1)
    exit(0)
