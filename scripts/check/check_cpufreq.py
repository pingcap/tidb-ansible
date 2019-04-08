# -*- coding: utf-8 -*-

import os
import sys
import re
import argparse

sysfs_cpu_online = "/sys/devices/system/cpu/online"

def get_file_content(path, default=None, strip=True):
    data = default
    if os.path.exists(path) and os.access(path, os.R_OK):
        try:
            try:
                datafile = open(path)
                data = datafile.read()
                if strip:
                    data = data.strip()
                if len(data) == 0:
                    data = default
            finally:
                datafile.close()
        except Exception:
            pass
    return data


def parse_opts():
    parser = argparse.ArgumentParser(
        description="Check Linux system CPUfreq governor.")
    parser.add_argument("--available-governors", action="store_true", default=False,
                        help="Show the CPUfreq governors available in the kernel.")
    parser.add_argument("--current-governor", action="store_true", default=False,
                        help="Show the currently active governor.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_opts()

    cpu_online = get_file_content(sysfs_cpu_online)

    if cpu_online is not None:
        cpu_num = re.split(',|-', cpu_online)[0]
        sysfs_cpufreq = "/sys/devices/system/cpu/cpu{0}/cpufreq".format(cpu_num)

        sysfs_cpufreq_available_governors = "{0}/scaling_available_governors".format(sysfs_cpufreq)
        sysfs_cpufreq_governor = "{0}/scaling_governor".format(sysfs_cpufreq)
    else:
        print(cpu_online)
        sys.exit()

    available_governors = get_file_content(sysfs_cpufreq_available_governors)
    current_governor = get_file_content(sysfs_cpufreq_governor)

    if args.available_governors:   
        print(available_governors)
        sys.exit()

    if args.current_governor:
        print(current_governor)
        sys.exit()
