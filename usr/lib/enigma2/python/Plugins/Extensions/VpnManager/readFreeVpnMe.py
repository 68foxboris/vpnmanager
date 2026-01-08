from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from bs4 import BeautifulSoup
import ssl
import re
import os
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from Components.config import config, configfile

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

URL = "https://www.freeopenvpn.me/"
CONF_DIRECTORY = "/etc/FreeVpn"


class VpnMe:
    CONF_DIRECTORY = CONF_DIRECTORY
    PW_PNG = CONF_DIRECTORY + "/pass.png"

    def __init__(self):
        self.update = None
        if not os.path.isdir(CONF_DIRECTORY):
            os.system("mkdir %s" % CONF_DIRECTORY)

    def get_config_data(self, is_vpn):
        data = []
        if os.path.isdir(CONF_DIRECTORY):
            for conf in os.listdir(CONF_DIRECTORY):
                if ".ovpn" in conf:
                    conf_destination = CONF_DIRECTORY + "/" + conf
                    conf_title = conf.replace(".ovpn", "")
                    conf_country = re.sub("\d+", "", conf.split("-")[0])
                    if "udp" in conf_title:
                        conf_proto = "udp"
                    elif "tcp" in conf_title:
                        conf_proto = "tcp"
                    else:
                        with open(conf_destination, "r") as conf_file:
                            conf_proto = "tcp" if "proto tcp" in conf_file.read() else "udp"
                    if config.vpnmanager.active.value == conf.replace(".conf", "").replace(".ovpn", ""):
                        is_connect = True
                        png = 1 if is_vpn else 2
                    else:
                        is_connect = False
                        png = 3
                    data.append((conf_title, conf_destination, is_connect, png))
        return data

    def set_access_data(self, soup):
        user = ""
        pw_image_url = ""
        acc = soup.find_all('section', class_="py-5")
        if len(acc) >= 1:
            user = re.findall("<p>(.*?)</p>", str(acc[1]), re.M)[0].encode("utf-8") if re.findall("<p>(.*?)</p>", str(acc[1]), re.M) else ""
            pw_image_url = URL + acc[1].find("img", src=True)["src"].encode("utf-8") if acc[1].find("img", src=True) else ""
        self.download_pw_image(pw_image_url)
        config.vpnmanager.username.value = user.strip()
        config.vpnmanager.username.save()
        configfile.save()

    def get_free_vpn(self):
        soup = self.get_url_soup(URL)
        if soup:
            os.system("rm -R %s" % CONF_DIRECTORY)
            os.system("mkdir %s" % CONF_DIRECTORY)
            self.set_access_data(soup)
            section = soup.find('section', class_="bg-gray py-5")
            if section:
                items = section.find('div', class_="row")
                for vpn in items.find_all("div"):
                    conf_data = [""]
                    country = vpn.find('a', class_="text-dark").get_text().encode("utf-8") if vpn.find('a', class_="text-dark") else ""
                    select_url = URL + vpn.find("a", class_="btn btn-outline-primary btn-sm", href=True)["href"].encode("utf-8") if vpn.find("a", class_="btn btn-outline-primary btn-sm", href=True) else ""
                    if select_url:
                        conf_data = self.get_conf_url(select_url)
                    if country and "[Offline]" not in country and conf_data:
                        for ovpn in conf_data:
                            self.download_conf(ovpn)
                self.update = True

    def get_conf_url(self, url):
        conf_data = []
        soup = self.get_url_soup(url)
        if soup:
            section = soup.find('section', class_="py-5 bg-cover bg-gray")
            if section:
                conf_data = re.findall('<p><a href="(.*?\\.ovpn)" target="', str(section), re.M)
        return conf_data

    def get_url_soup(self, url):
        try:
            data = urlopen(url, timeout=8)
            content = data.read()
            soup = BeautifulSoup(content, 'html.parser')
        # handle errors
        except HTTPError as e:
            print("HTTP Error: %s %s" % (e.code, url))
            return None
        except URLError as e:
            print("URL Error: %s %s" % (e.reason, url))
            return None
        except Exception as e:
            print("Error: %s %s" % (str(e), str(url)))
            return None
        else:
            return soup

    def download_pw_image(self, url):
        try:
            f = urlopen(url, timeout=8)
            # Open our local file for writing
            destination = CONF_DIRECTORY + "/pass.png"
            with open(destination, "wb") as local_file:
                local_file.write(f.read())
        # handle errors
        except HTTPError as e:
            print("HTTP Error: %s %s" % (e.code, url))
        except URLError as e:
            print("URL Error: %s %s" % (e.reason, url))
        except Exception as e:
            print("Error: %s %s" % (str(e), str(url)))

    def download_conf(self, url):
        try:
            f = urlopen(url, timeout=8)
            # Open our local file for writing
            destination = CONF_DIRECTORY + "/" + os.path.basename(url)
            with open(destination, "wb") as local_file:
                local_file.write(f.read())
        # handle errors
        except HTTPError as e:
            print("HTTP Error: %s %s" % (e.code, url))
        except URLError as e:
            print("URL Error: %s %s" % (e.reason, url))
        except Exception as e:
            print("Error: %s %s" % (str(e), str(url)))

