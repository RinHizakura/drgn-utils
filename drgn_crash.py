# Reference: https://blogs.oracle.com/linux/post/enter-the-drgn

from drgn import FaultError, NULL, Object, cast, container_of, execscript, offsetof, reinterpret, sizeof, stack_trace
from drgn.helpers.common import *
from drgn.helpers.linux import *

import datetime, time

uts_namespace_detail = prog['init_uts_ns']

nodename = uts_namespace_detail.name.nodename.string_().decode("utf-8")
release = uts_namespace_detail.name.release.string_().decode("utf-8")
version = uts_namespace_detail.name.version.string_().decode("utf-8")
machine = uts_namespace_detail.name.machine.string_().decode("utf-8")

timekeeper = prog['tk_core'].shadow_timekeeper
xtime_sec = timekeeper.xtime_sec
date = time.ctime(xtime_sec)
uptime = str(datetime.timedelta(seconds=int(timekeeper.ktime_sec)))

print(f'DATE: {date}')
print(f'UPTIME: {uptime}')
print(f'NODENAME : {nodename}')
print(f'RELEASE : {release}')
print(f'VERSION : {version}')
print(f'MACHINE : {machine}')
