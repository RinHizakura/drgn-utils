#!/usr/bin/env drgn

import os, sys
import argparse

import drgn
from drgn.helpers.common import *
from drgn.helpers.linux import *
from drgn import container_of
from dev_util import to_subsys_dev

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


def bus_to_subsys(prog, bus):
    for sp in list_for_each_entry(
        "struct subsys_private",
        prog["bus_kset"].list.address_of_(),
        "subsys.kobj.entry",
    ):
        name = sp.bus.name.string_().decode("utf-8")
        if name == bus:
            return sp
    return None


def class_to_subsys(prog, cls):
    for sp in list_for_each_entry(
        "struct subsys_private",
        prog["class_kset"].list.address_of_(),
        "subsys.kobj.entry",
    ):
        name = getattr(sp, "class").name.string_().decode("utf-8")
        if name == cls:
            return sp
    return None

def get_busdev_childs(prog, bus, dev):
    sp = bus_to_subsys(prog, bus)
    if not sp:
        return None

    childs = []

    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_bus.n_node",
    ):
        device = priv.device
        name = device.kobj.name.string_().decode("utf-8")
        parent = device.parent
        parent_name = parent.kobj.name.string_().decode("utf-8")
        if parent_name == dev:
            childs.append(device)

    return childs

def get_classdev_childs(prog, cls, dev):
    sp = class_to_subsys(prog, cls)
    if sp == None:
        return None

    childs = []

    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_class.n_node",
    ):
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
