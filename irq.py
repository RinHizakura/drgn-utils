#!/usr/bin/env drgn

import argparse

import drgn
from drgn.helpers.common import *
from drgn.helpers.linux import *
from drgn import Object

IRQ_TYPE_EDGE_RISING = 0x00000001
IRQ_TYPE_EDGE_FALLING = 0x00000002
IRQ_TYPE_EDGE_BOTH = (IRQ_TYPE_EDGE_FALLING | IRQ_TYPE_EDGE_RISING)
IRQ_TYPE_LEVEL_HIGH = 0x00000004
IRQ_TYPE_LEVEL_LOW = 0x00000008
IRQ_TYPE_LEVEL_MASK = (IRQ_TYPE_LEVEL_LOW | IRQ_TYPE_LEVEL_HIGH)
IRQ_TYPE_SENSE_MASK = 0x0000000f

def _sparse_irq_supported(prog):
    try:
        # Since Linux kernel commit 721255b9826b ("genirq: Use a maple
        # tree for interrupt descriptor management") (in v6.5), sparse
        # irq descriptors are stored in a maple tree.
        _ = prog["sparse_irqs"]
        return True, "maple"
    except KeyError:
        # Before that, they are in radix tree.
        try:
            _ = prog["irq_desc_tree"]
            return True, "radix"
        except KeyError:
            return False, None

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("irq", type=int, help="number of the irq")
    args = parser.parse_args()
    return args

def irq_to_desc(prog, irq):
    _, tree_type = _sparse_irq_supported(prog)
    if tree_type == "radix":
        addr = radix_tree_lookup(prog["irq_desc_tree"].address_of_(), irq)
    else:
        addr = mtree_load(prog["sparse_irqs"].address_of_(), irq)
    return Object(prog, "struct irq_desc", address=addr).address_of_()

def irq_settings_get_trigger_mask(desc):
    return desc.status_use_accessors & IRQ_TYPE_SENSE_MASK

def irq_desc_get_chip(desc):
    return desc.irq_data.chip

if __name__ == "__main__":
    args = get_args()
    irq = args.irq

    print(f"Get information of irq {irq}")

    desc = irq_to_desc(prog, irq)
    domain = desc.irq_data.domain

    print(desc)
    print("irq_common_data = ", desc.irq_common_data)
    print("irq_chip = ", irq_desc_get_chip(desc))
    print("trigger = ", irq_settings_get_trigger_mask(desc))
    print("action thread_fn = ", desc.action.thread_fn)
    print(domain)

    print(f"Get parent information of irq {irq}")
    parent = desc.irq_data.parent_data
    while parent:
        print(f"{parent.chip.name}:")
        print(parent)
        parent = parent.parent_data
