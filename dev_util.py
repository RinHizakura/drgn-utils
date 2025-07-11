from drgn import cast, container_of
from drgn.helpers.linux import *


class ToDev:
    def to_platform_dev(d):
        return container_of(d, "struct platform_device", "dev")

    def to_usb_dev(d):
        return container_of(d, "struct usb_device", "dev")

    def to_pci_dev(d):
        return container_of(d, "struct pci_dev", "dev")

    def to_hwmon_dev(d):
        return container_of(d, "struct hwmon_device", "dev")

    def to_rtc_dev(d):
        return container_of(d, "struct rtc_device", "dev")

    def to_net_dev(d):
        return container_of(d, "struct net_device", "dev")


def to_subsys_dev(subsys, device):
    to_dev = getattr(ToDev, f"to_{subsys}_dev")
    return to_dev(device)


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


def busdev_gen(prog, bus):
    sp = bus_to_subsys(prog, bus)
    if not sp:
        return None
    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_bus.n_node",
    ):
        yield priv


def classdev_gen(prog, cls):
    sp = class_to_subsys(prog, cls)
    if sp == None:
        return None
    for priv in list_for_each_entry(
        "struct device_private",
        sp.klist_devices.k_list.address_of_(),
        "knode_class.n_node",
    ):
        yield priv


def dev_get_drvdata(typ, d):
    return cast(typ, d.driver_data)


def pci_get_drvdata(typ, pdev):
    # Cast driver_data to the given type. For example:
    # pci_get_drvdata("struct net_device *", pdev)
    return dev_get_drvdata(typ, pdev.dev)


def platform_get_drvdata(typ, pdev):
    return dev_get_drvdata(typ, pdev.dev)
