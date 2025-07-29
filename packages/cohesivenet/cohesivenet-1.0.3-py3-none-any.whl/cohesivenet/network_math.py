import ipaddress
from typing import List

from cohesivenet import util


class NetworkMathException(Exception):
    pass


def get_default_gateway(subnet_cidr: str) -> str:
    return str(util.take(ipaddress.ip_network(subnet_cidr).hosts(), 1)[-1])


def get_dns_server(subnet_cidr: str) -> str:
    return str(util.take(ipaddress.ip_network(subnet_cidr).hosts(), 2)[-1])


def calculate_next_subnets(
    prefix_length: int, take: int, cidr: str, after_subnet: str = None
) -> List[str]:
    """Calculate the next {take} subnets of prefix length {prefix_length} for network cidr {cidr}

    Arguments:
        prefix_length {int}
        take {int}
        cidr {str}

    Returns:
        List[str]
    """
    network = ipaddress.ip_network(cidr)
    subnets = network.subnets(new_prefix=prefix_length)

    if after_subnet:
        try:
            # iterate until next in sequence is subnet after
            next(sn for sn in subnets if sn == ipaddress.ip_network(after_subnet))
        except (StopIteration, ValueError):
            raise NetworkMathException(
                "Subnet %s not found in subnets of prefix "
                "length %s for parent network %s." % (after_subnet, prefix_length, cidr)
            )

    try:
        return [next(subnets) for _ in range(take)]
    except StopIteration:
        raise NetworkMathException(
            "Cant take %s subnets [prefix:%s] from parent "
            "net %s [after subnet:%s]" % (take, prefix_length, cidr, after_subnet)
        )


def subnet_contains_ipv4(ip_address: str, subnet: str):
    """subnet_contains Check if ip address in subnet

    Arguments:
        ip_address {str} -- string
        subnet {str}

    Returns:
        bool
    """
    return ipaddress.ip_address(ip_address) in ipaddress.ip_network(subnet)
