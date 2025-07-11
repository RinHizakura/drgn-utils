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


def get_busdev_childs(prog, bus, dev):
    childs = []
    for priv in busdev_gen(prog, bus):
        device = priv.device
        name = device.kobj.name.string_().decode("utf-8")
        parent = device.parent
        parent_name = parent.kobj.name.string_().decode("utf-8")
        if parent_name == dev:
            childs.append(device)

    return childs


def get_classdev_childs(prog, cls, dev):
    childs = []
    for priv in classdev_gen(prog, cls):
        device = priv.device
        name = device.kobj.name.string_().decode("utf-8")
        parent = device.parent
        parent_name = device.kobj.name.string_().decode("utf-8")
        if parent_name == dev:
            childs.append(device)

    return childs


if __name__ == "__main__":
    args = get_args()
    subsys = args.subsys
    dev = args.dev

    # FIXME: Brute forcely
    get_childs = get_busdev_childs if subsys in bus_list else get_classdev_childs
    childs = get_childs(prog, subsys, dev)
    print(f"The childs of {dev} is:")
    for d in childs:
        name = d.kobj.name.string_().decode("utf-8")
        print(f"\t{name}: {d.power.runtime_status}")
