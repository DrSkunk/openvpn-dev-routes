# Prints amazon aws ips in the openvpn route format, for example:
# route 52.124.128.0 255.255.128.0
# Works with python 2 and 3

import sys
import json
import requests
import ipaddress

OUTPUT = ""


class DataFetchError(Exception):
    """Exception raised for errors while fetching data.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        pass

def transform_address(address):
    address_with_netmask = ipaddress.ip_network(
        address).with_netmask.split('/')
    return "route " + address_with_netmask[0] + " " + address_with_netmask[1] + "\n"


def add_amazon():
    try:
        print("Fetching Amazon EC2")
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
    except:
        raise DataFetchError("Error fetching data from Amazon EC2")
    return output


def add_github():
    print("Fetching GitHub")
    output = "\n### GitHub\n"
    r = requests.get("https://api.github.com/meta")
    json = {k: v for k, v in r.json().items() if isinstance(v, list)}

    if not json.items():
        raise DataFetchError("Error fetching data from GitHub")

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
    print("Fetching GitLab")
    # Placeholder for when public api is released
    # See https://gitlab.com/gitlab-com/infrastructure/issues/434
    return "\n## GitLab\nroute 35.231.145.151 255.0.0.0\n"


def add_atlassian():
    try:
        print("Fetching Atlassian")
        output = "\n### Atlassian\n"
        r = requests.get("https://ip-ranges.atlassian.com/")
        for item in r.json()["items"]:
            output += "route " + item["network"] + " " + item["mask"] + "\n"
    except:
        raise DataFetchError("Error fetching data from Amazon Atlassian")
    return output


try:
    OUTPUT += add_amazon()
    OUTPUT += add_github()
    OUTPUT += add_gitlab()
    OUTPUT += add_atlassian()
    with open("routes.txt", 'w') as out:
        out.write(OUTPUT)
    print("Output written to 'routes.txt'")
except IOError:
    print("Error while writing 'routes.txt'")
    sys.exit(1)
except Exception as e:
    print(e)
    sys.exit(1)
