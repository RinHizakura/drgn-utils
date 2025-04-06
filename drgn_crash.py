# Reference: https://blogs.oracle.com/linux/post/enter-the-drgn

from drgn import (
    FaultError,
    NULL,
    Object,
    cast,
    container_of,
    execscript,
    offsetof,
    reinterpret,
    sizeof,
    stack_trace,
)
from drgn.helpers.common import *
from drgn.helpers.linux import *

import datetime, time, warnings


def roundup(x, y):
    return ((x + (y - 1)) / y) * y


def GIGABYTES(x):
    return x * 2**30


def MEGABYTES(x):
    return x * 2**20


def node_present_pages(nid):
    # FIXME: Consider different arch
    return prog["node_data"][nid].node_present_pages


def get_num_physpages():
    # Reference: https://elixir.bootlin.com/linux/v6.11/source/include/linux/mm.h#L3183
    phys_pages = 0
    for node in for_each_online_node():
        phys_pages += node_present_pages(node)
    return phys_pages


def get_memory_size(prog):
    # Reference: https://github.com/crash-utility/crash/blob/master/memory.c#L14364
    total = prog["PAGE_SIZE"] * get_num_physpages()
    next_gig = roundup(total, GIGABYTES(1))
    if next_gig > 0:
        if (next_gig - total) <= MEGABYTES(64):
            total = next_gig
    return total


# Reference: https://github.com/crash-utility/crash/blob/master/task.c#L6351
def get_panicmsg(prog):
    panic_msg = [
        "SysRq : Crash",
        "SysRq : Trigger a crash",
        "SysRq : Netdump",
        "Kernel panic: ",
        "Kernel panic - ",
        "Kernel BUG at",
        "kernel BUG at",
        "Unable to handle kernel paging request",
        "Unable to handle kernel NULL pointer dereference",
        "BUG: unable to handle kernel ",
        "general protection fault: ",
        "double fault: ",
        "divide error: ",
        "stack segment: ",
        "[Hardware Error]: ",
        "Bad mode in ",
        "Oops: ",
    ]

    msg_found = False
    res = ""
    dmesg = get_dmesg(prog).decode()

    for s in dmesg.split("\n"):
        for msg in panic_msg:
            if msg in s:
                res = s[s.index(msg) :]
                msg_found = True
                break

        if msg_found:
            break
    return res


uts_namespace_detail = prog["init_uts_ns"]

nodename = uts_namespace_detail.name.nodename.string_().decode("utf-8")
release = uts_namespace_detail.name.release.string_().decode("utf-8")
version = uts_namespace_detail.name.version.string_().decode("utf-8")
machine = uts_namespace_detail.name.machine.string_().decode("utf-8")

timekeeper = prog["tk_core"].shadow_timekeeper
xtime_sec = timekeeper.xtime_sec
date = time.ctime(xtime_sec)
uptime = str(datetime.timedelta(seconds=int(timekeeper.ktime_sec)))

cpus = len(list(for_each_possible_cpu(prog)))
tasks = len(list(for_each_pid(prog)))
# Include swapper here to align with crash utility. Do
# simple check to make sure the assumption is correct
for cpu in for_each_possible_cpu(prog):
    comm = idle_task(prog, cpu).comm.string_().decode("utf-8")
    if comm != f"swapper/{cpu}":
        warnings.warn(f"Fail to find swapper task on cpu{cpu}")
    else:
        tasks += 1

total = get_memory_size(prog)
memory = number_in_binary_units(total)

load = ", ".join([f"{v:.2f}" for v in loadavg(prog)])

panic = get_panicmsg(prog)

cpu = prog["crashing_cpu"]
task = per_cpu(prog["runqueues"], cpu).curr
task_addr = task.value_()
comm = task.comm.string_().decode("utf-8")
pid = task.pid
# Check: https://man7.org/linux/man-pages/man1/ps.1.html#PROCESS_STATE_CODES
state = task_state_to_char(task)

print(f"CPUS: {cpus}")
print(f"DATE: {date}")
print(f"UPTIME: {uptime}")
print(f"LOAD AVERAGE: {load}")
print(f"TASKS: {tasks}")
print(f"NODENAME : {nodename}")
print(f"RELEASE : {release}")
print(f"VERSION : {version}")
print(f"MACHINE : {machine}")
print(f"MEMORY : {memory}")
print(f"PANIC: \"{panic}\"")
print(f"PID: {int(pid)}")
print(f'COMM: "{comm}"')
print(f"TASK: {hex(task_addr)}")
print(f"CPU: {int(cpu)}")
print(f"STATE: {state}")
