from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from builtins import str

import json
from urllib.request import urlopen

import re
import os

URL1 = "http://ip-api.com/json"
URL2 = "https://checkip.justwatch.com"


def get_ip_info(tun=False):
    infos = []
    content = get_ip_info_data(URL1)
    if content:
        ip = content["query"]
        if not ip:
            json_data = get_ip_info_data(URL2)
            ip = json_data["ip"] if json_data.get("ip") else None
        if tun:
            ip = get_ping(ip)
        else:
            ip = "IP: " + ip if ip else "IP: n/a"
        infos.append(ip)
        country = "Country: " + str(content["country"]) if content.get("country") else "Country: n/a"
        infos.append(country)
        region = "Region: " + str(content["regionName"]) if content.get("regionName") else "Region: n/a"
        infos.append(region)
        city = "City: " + str(content["city"]) if content.get("city") else "City: n/a"
        infos.append(city)
        org = "Organisation: " + str(content["org"]) if content.get("org") else "Organisation: n/a"
        infos.append(org)

    info_label = ""
    if infos:
        for i in infos:
            info_label = info_label + i + "\n"

    return info_label


def get_ping(ip):
    ping = "IP: n/a\nPing: n/a"

    if ip:
        try:
            read_proc = os.popen("ping -c 2 " + ip)
            proc_data = read_proc.read()
            read_proc.close()
            result = re.findall("round-trip min/avg/max = \d+\\.\d+/(\d+\\.\d+)/\d+\\.\d+\sms", proc_data,
                                re.S)
            if result:
                ping = "IP: %s\nPing: %s ms" % (ip, result[0])
            else:
                ping = "IP: %s\nPing: n/a" % ip
        except OSError:
            ping = "IP: %s\n" % ip

    return ping


def get_ip_info_data(url):
    content = {}
    try:
        content = urlopen(url, timeout=4)
        content = json.load(content)
    except:
        pass
    return content
