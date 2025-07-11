#!/usr/bin/env drgn

import os, sys
import argparse

import drgn
from dev_util import *

class_list = ["hwmon", "rtc", "net"]
bus_list = ["platform", "usb", "pci"]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "subsys", help="bus/class type for the device", choices=class_list + bus_list
    )
    parser.add_argument("-d", "--dev", help="name of the specified device")
    args = parser.parse_args()
    return args


def get_busdev(prog, bus, dev):
    for priv in busdev_gen(prog, bus):
        device = priv.device
        device_name = device.kobj.name.string_().decode("utf-8")
        if device_name == dev:
            return device

    return None


def get_classdev(prog, cls, dev):
    for priv in classdev_gen(prog, cls):
        device = priv.device
        device_name = device.kobj.name.string_().decode("utf-8")
        if device_name == dev:
            return device

    return None


if __name__ == "__main__":
    args = get_args()
    subsys = args.subsys
    dev = args.dev

    get_dev = get_busdev if subsys in bus_list else get_classdev
    device = get_dev(prog, subsys, dev)
    if not device:
        exit(f"Can't find {dev} on {subsys} bus/class")

    print(to_subsys_dev(subsys, device))
