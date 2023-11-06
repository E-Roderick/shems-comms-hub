import ifaddr, ipaddress

from typing import List, Tuple, Union

# Functions
def is_connectable_ip(
    ip: Union[ipaddress.IPv4Address, ipaddress.IPv6Address]
) -> bool:
    """ Checks if a given IP address is connectable. A connectable IP address is
        one that is a non-loopback private address, or a link local address.

        Returns:
            (bool) True if the IP address is valid. False otherwise.
    """
    return (ip.is_private and not ip.is_loopback) or ip.is_link_local


def get_addresses() -> List[Tuple['address', 'network']]:
    """ Finds all valid addresses for network adapters on this machine. An
        address is valid if it meets the criteria outlined in is_connectable_ip.

        Returns:
            (List[Tuple[address, network]]) A list of addresses as tuples
            containing the IP address object for the addressm and the network
            object for the network that address is in.
    """
    addresses = []

    adapters = ifaddr.get_adapters()
    for adapter in adapters:
        for ip in adapter.ips:

            # Get ipv6 or ipv4 representation string
            mask = ip.network_prefix
            ip = ip.ip[0] if isinstance(ip.ip, tuple) else ip.ip

            address = ipaddress.ip_address(ip)
            if not is_connectable_ip(address):
                continue

            network = ipaddress.ip_network(f"{ip}/{mask}", strict=False)
            addresses.append((address, network))

    return addresses
