from drgn import cast

def dev_get_drvdata(typ, d):
    return cast(typ, d.driver_data)

def pci_get_drvdata(typ, pdev):
    # Cast driver_data to the given type. For example:
    # pci_get_drvdata("struct net_device *", pdev)
    return dev_get_drvdata(typ, pdev.dev)

def platform_get_drvdata(typ, pdev):
    return dev_get_drvdata(typ, pdev.dev)
