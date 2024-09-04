#!/usr/bin/env drgn

import os, sys
import argparse

import drgn
from drgn.helpers.common import *
from drgn.helpers.linux import *
from drgn import container_of

class_list = ["hwmon", "net"]
bus_list = ["platform", "usb", "pci"]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "subsys", help="bus/class type for the device", choices=class_list + bus_list
    )
    parser.add_argument("-d", "--dev", help="name of the specified device")
    args = parser.parse_args()
    return args


def bus_to_subsys(prog, bus):
    for sp in list_for_each_entry(
        "struct subsys_private",
        prog["bus_kset"].list.address_of_(),
        "subsys.kobj.entry",
    ):
        if sp.bus == bus:
            return sp
    return None


def class_to_subsys(prog, cls):
    for sp in list_for_each_entry(
        "struct subsys_private",
        prog["class_kset"].list.address_of_(),
        "subsys.kobj.entry",
    ):
        if getattr(sp, "class") == cls:
            return sp
    return None


class ToDev:
    def to_platform_dev(d):
        return container_of(d, "struct platform_device", "dev")

    def to_usb_dev(d):
        return "todo"

    def to_pci_dev(d):
        return container_of(d, "struct pci_dev", "dev")

    def to_hwmon_dev(d):
        return container_of(d, "struct hwmon_device", "dev")

    def to_net_dev(d):
        return "todo"


def get_busdev(prog, bus, dev):
    sp = bus_to_subsys(prog, prog[f"{bus}_bus_type"].address_of_())
    if not sp:
        return None

    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_bus.n_node",
    ):
        device = priv.device
        device_name = device.kobj.name.string_().decode("utf-8")
        if device_name == dev:
            return device

    return None

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dev", help="name of the specified device")
    args = parser.parse_args()
    return args


def get_classdev(prog, cls, dev):
    sp = class_to_subsys(prog, prog[f"{cls}_class"].address_of_())
    if sp == None:
        return None

    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_class.n_node",
    ):
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

    to_dev = getattr(ToDev, f"to_{subsys}_dev")
    inner_dev = to_dev(device)
    print(inner_dev)
