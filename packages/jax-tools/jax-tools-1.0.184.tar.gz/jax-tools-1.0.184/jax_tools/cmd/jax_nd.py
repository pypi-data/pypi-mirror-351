"""
nd command
"""
import sys
from jax_tools.network_test import check_connectivity


def main() -> None:
    """
    Main function
    Returns:

    """
    if len(sys.argv) == 3:
        target_ip = sys.argv[1]
        target_port = int(sys.argv[2])
        check_connectivity(target_ip, target_port, True)
    elif len(sys.argv) == 2:
        target_ip = sys.argv[1]
        check_connectivity(target_ip, None, True)
    else:
        print("Usage: nd <TargetIP> <TargetPort>")
