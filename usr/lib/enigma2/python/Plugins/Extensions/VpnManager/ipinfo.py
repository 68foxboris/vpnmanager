import json
import urllib2
import re
import os

URL1 = "http://ip-api.com/json"
URL2 = "https://checkip.justwatch.com"


def get_ip_info(tun=False):
    infos = []
    content = get_ip_info_data(URL1)
    if content:
        ip = content["query"].encode("utf-8") if isinstance(content["query"], unicode) else str(content["query"])
        if not ip:
            json_data = get_ip_info_data(URL2)
            ip = json_data.get("ip").encode("utf-8") if isinstance(json_data.get("ip"), unicode) else None
        if tun:
            ip = get_ping(ip)
        else:
            ip = "IP: " + ip if ip else "IP: n/a"
        infos.append(ip)
        country = "Country: " + content["country"].encode("utf-8") if isinstance(content["country"], unicode) else "Country: " + content["country"]
        infos.append(country)
        region = "Region: " + content["regionName"].encode("utf-8") if isinstance(content["regionName"], unicode) else "Region: " + content["regionName"]
        infos.append(region)
        city = "City: " + content["city"].encode("utf-8") if isinstance(content["city"], unicode) else "City: " + content["city"]
        infos.append(city)
        org = "Organisation: " + content["org"].encode("utf-8") if isinstance(content["org"], unicode) else "Organisation: " + content["org"]
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
        content = urllib2.urlopen(url, timeout=4)
        content = json.load(content)
    except:
        pass
    return content
