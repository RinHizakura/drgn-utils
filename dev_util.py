from drgn import cast

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

def dev_get_drvdata(typ, d):
    return cast(typ, d.driver_data)

def pci_get_drvdata(typ, pdev):
    # Cast driver_data to the given type. For example:
    # pci_get_drvdata("struct net_device *", pdev)
    return dev_get_drvdata(typ, pdev.dev)

def platform_get_drvdata(typ, pdev):
    return dev_get_drvdata(typ, pdev.dev)
