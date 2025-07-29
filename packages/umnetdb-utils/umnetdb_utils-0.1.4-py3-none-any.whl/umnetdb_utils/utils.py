import ipaddress
import re
def is_ip_address(input_str, version=None):
    try:
        ip = ipaddress.ip_address(input_str)
    except ValueError:
        return False

    if version and version != ip.version:
        return False

    return True

def is_ip_network(input_str, version=None):
 
    # First check that this is a valid IP or network
    try:
        net = ipaddress.ip_network(input_str)
    except ValueError:
        return False

    if version and version != net.version:
        return False
    
    return True

def is_mac_address(input_str):
    '''
    Validates the input string as a mac address. Valid formats are
    XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXX.XXXX.XXXX
    where 'X' is a hexadecimal digit (upper or lowercase).
    '''
    mac = input_str.lower()
    if re.match(r'[0-9a-f]{2}([-:])[0-9a-f]{2}(\1[0-9a-f]{2}){4}$', mac):
        return True
    if re.match(r'[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}$', mac):
        return True

    return False
