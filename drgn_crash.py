# crash(8)-style summary of a kernel dump, built on drgn's crash commands.
#
# Usage:
#   drgn -c vmcore -s vmlinux drgn_crash.py   # dump
#   sudo drgn drgn_crash.py                   # live kernel
# In an interactive drgn session the same output comes from
#   %crash sys
#   %crash set
#
# Reference: https://blogs.oracle.com/linux/post/enter-the-drgn
from drgn.commands import run_command

run_command(prog, "crash sys")  # kernel, dumpfile, cpus, date, uptime, load, memory, panic
run_command(prog, "crash set")  # panicking task: pid, command, task, cpu, state
