#!/usr/bin/env drgn

import argparse

import drgn
from drgn.helpers.common import *
from drgn.helpers.linux import *
from drgn import Object


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("gpio", type=str, help="name of the gpio")
    args = parser.parse_args()
    return args


def gpio_name_to_desc(gpio):
    for gdev in list_for_each_entry(
        "struct gpio_device", prog["gpio_devices"].address_of_(), "list"
    ):

        for idx in range(gdev.ngpio):
            desc = gdev.descs[idx]
            name = desc.name.string_().decode("utf-8")
            if name == gpio:
                return desc

    return None


args = get_args()
gpio = args.gpio

print(f"Get information of gpio {gpio}")

desc = gpio_name_to_desc(gpio)
print(desc)
