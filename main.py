# Prints amazon aws ips in the openvpn route format, for example:
# route 52.124.128.0 255.255.128.0
# Works with python 2 and 3

import json
import requests
import ipaddress

OUTPUT = ""


def transform_address(address):
    address_with_netmask = ipaddress.ip_network(
        address).with_netmask.split('/')
    return "route " + address_with_netmask[0] + " " + address_with_netmask[1] + "\n"


def add_amazon():
    r = requests.get("https://ip-ranges.amazonaws.com/ip-ranges.json")
    prefixes = r.json()["prefixes"]
    prefixes.sort(key=lambda x: x["region"], reverse=True)
    current_region = ""
    output = "\n### Amazon EC2\n"
    for prefix in prefixes:
        if current_region != prefix["region"]:
            output += "# " + prefix["region"] + "\n"
            current_region = prefix["region"]
        output += transform_address(prefix["ip_prefix"])
    return output


def add_github():
    output = "\n### GitHub\n"
    r = requests.get("https://api.github.com/meta")
    json = {k: v for k, v in r.json().items() if isinstance(v, list)}
    current_group = ""
    for group, address_list in json.items():
        if current_group != group:
            #output += transform_address(address)
            output += "# " + group + "\n"
            current_group = group
        for address in address_list:
            output += transform_address(address)
    return output


def add_gitlab():
    # Placeholder for when public api is released
    # See https://gitlab.com/gitlab-com/infrastructure/issues/434
    return "\n## GitLab\nroute 35.231.145.151 255.0.0.0\n"


OUTPUT += add_amazon()
OUTPUT += add_github()
OUTPUT += add_gitlab()

with open("routes.txt", 'w') as out:
    out.write(OUTPUT)
print("Output written to 'routes.txt'")
