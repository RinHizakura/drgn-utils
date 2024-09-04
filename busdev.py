#!/usr/bin/env drgn

import os, sys
import argparse

import drgn
from drgn.helpers.common import *
from drgn.helpers.linux import *
from drgn import container_of

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("bus", help="bus type for the device",
            choices=["platform", "usb", "pci"])
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

class ToDev():
    def to_platform_dev(d):
        return container_of(d, "struct platform_device", "dev")

    def to_usb_dev(d):
        return "todo"

    def to_pci_dev(d):
        return container_of(d, "struct pci_dev", "dev")

def get_busdev(prog, bus, dev):
    sp = bus_to_subsys(prog, prog[f"{bus}_bus_type"].address_of_())
    if not sp:
        return None

    for priv in list_for_each_entry(
        "struct device_private", sp.klist_devices.k_list.address_of_(), "knode_bus.n_node"
    ):
        device = priv.device
        device_name = device.kobj.name.string_().decode("utf-8")
        if device_name == dev:
            return device

    return None

if __name__ == '__main__':
    args = get_args()
    bus = args.bus
    dev = args.dev

    device = get_busdev(prog, bus, dev)
    if not device:
        exit(f"Can't find {dev} on {bus} bus")

    to_dev = getattr(ToDev, f"to_{bus}_dev")
    inner_dev = to_dev(device)
    print(inner_dev)
