#!/usr/bin/env drgn
# Copyright (c) Canonical Ltd.
# SPDX-License-Identifier: LGPL-2.1-or-later

"""
Script to dump vmallocinfo status using drgn. This is actually a copy from
https://github.com/osandov/drgn/blob/main/contrib/vmallocinfo.py
with a few changes to show specific information only and run on
older version of drgn.
"""

import argparse, re
from typing import Optional

from drgn import IntegerLike, Program
from drgn.helpers.common import *
from drgn.helpers.linux import *

def _vmap_nodes(prog):
    vmap_nodes = prog["vmap_nodes"]
    try:
        return vmap_nodes.read_()
    except ObjectAbsentError:
        return prog.variable("single", "mm/vmalloc.c").address_of_()

def for_each_vmap_area_internal(prog):
    try:
        vmap_nodes = _vmap_nodes(prog)
    except KeyError:
        yield from list_for_each_entry(
            "struct vmap_area", prog["vmap_area_list"].address_of_(), "list"
        )
    else:
        for i in range(prog["nr_vmap_nodes"]):
            yield from list_for_each_entry(
                "struct vmap_area", vmap_nodes[i].busy.head.address_of_(), "list"
            )

VMAP_RAM = 0x1  # indicates vm_map_ram area

VM_IOREMAP = 0x00000001  # ioremap() and friends
VM_ALLOC = 0x00000002  # vmalloc()
VM_MAP = 0x00000004  # vmap()ed pages
VM_USERMAP = 0x00000008  # suitable for remap_vmalloc_range
VM_DMA_COHERENT = 0x00000010  # dma_alloc_coherent
VM_SPARSE = 0x00001000  # sparse vm_area. not all pages are present.


def is_vmalloc_addr(prog: Program, addr: IntegerLike) -> Optional[bool]:
    vmcoreinfo = prog["VMCOREINFO"].string_()
    match = re.search(
        rb"^NUMBER\(VMALLOC_START\)=(0x[0-9a-f]+)$", vmcoreinfo, flags=re.M
    )
    if match:
        VMALLOC_START = int(match.group(1), 16)

    match = re.search(rb"^NUMBER\(VMALLOC_END\)=(0x[0-9a-f]+)$", vmcoreinfo, flags=re.M)
    if match:
        VMALLOC_END = int(match.group(1), 16)

    try:
        return True if addr >= VMALLOC_START and addr < VMALLOC_END else False
    except:
        return None

def get_args():
     parser = argparse.ArgumentParser()
     parser.add_argument("-a", "--addr", help="the virtual address you are interesting in", type=lambda x: int(x,0))
     args = parser.parse_args()
     return args

args = get_args()
addr = args.addr

for vmap_area in for_each_vmap_area_internal(prog):
    if not vmap_area.vm:
        if vmap_area.flags & VMAP_RAM:
            print(
                f"0x{vmap_area.va_start:x}-0x{vmap_area.va_end:x} {vmap_area.va_end - vmap_area.va_start:10d} vm_map_ram"
            )
            continue
    v = vmap_area.vm
    start_addr = v.addr.value_()
    end_addr = (v.addr+v.size).value_()
    if addr != None and (addr < start_addr or addr >= end_addr):
        continue
    print(
        f"0x{start_addr:x}-0x{end_addr:x} {v.size.value_():10d}",
        end="",
    )
    if v.caller:
        try:
            print(f" {prog.symbol(v.caller.value_()).name}", end="")
        except LookupError:
            print(f" 0x{v.caller.value_():x}", end="")
    if v.nr_pages:
        print(f" pages={v.nr_pages.value_():d}", end="")
    if v.phys_addr:
        print(f" phys=0x{v.phys_addr.value_():x}", end="")
    if v.flags & VM_IOREMAP:
        print(" ioremap", end="")
    if v.flags & VM_SPARSE:
        print(" sparse", end="")
    if v.flags & VM_ALLOC:
        print(" vmalloc", end="")
    if v.flags & VM_MAP:
        print(" vmap", end="")
    if v.flags & VM_USERMAP:
        print(" user", end="")
    if v.flags & VM_DMA_COHERENT:
        print(" dma-coherent", end="")
    if is_vmalloc_addr(prog, v.pages):
        print(" vpages", end="")
    print("")
