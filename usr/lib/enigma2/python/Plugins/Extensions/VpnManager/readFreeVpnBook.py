from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()

from builtins import str

from bs4 import BeautifulSoup
import ssl
import os
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from zipfile import ZipFile
import re

from Components.config import config, configfile

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

URL = "https://www.vpnbook.com/freevpn"

CONF_DIRECTORY = "/home/root/FreeVpn"


class VpnBook:
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
                    conf_country = re.sub("\d+", "", conf.split("-")[1]) if len(conf.split("-")) > 1 else ""
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
        user = str(soup.find('strong').get_text()) if soup.find('strong') else ""
        pw_image_url = "https://www.vpnbook.com/" + str(soup.find("img", src=True)["src"]).replace(" ", "%20") if soup.find("img", src=True) else ""
        self.download_pw_image(pw_image_url)
        config.vpnmanager.username.value = user.strip()
        config.vpnmanager.username.save()
        configfile.save()

    def get_free_vpn(self):
        data = []
        soup = self.get_url_soup(URL)
        if soup:
            section = soup.find_all('ul', class_="disc")
            if len(section) >= 2:
                os.system("rm -R %s" % CONF_DIRECTORY)
                os.system("mkdir %s" % CONF_DIRECTORY)
                self.set_access_data(section[1])
                for zip_url in section[1].find_all("a", href=True):
                    url = "https://www.vpnbook.com" + str(zip_url["href"])
                    data.append(url)

        if data:
            for find in data:
                self.download_conf(find)
            self.update = True

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

    def download_conf(self, url):
        try:
            f = urlopen(url, timeout=8)
            # Open our local file for writing
            destination = "/tmp/" + os.path.basename(url)
            with open(destination, "wb") as local_file:
                local_file.write(f.read())
        # handle errors
        except HTTPError as e:
            print("HTTP Error: %s %s" % (e.code, url))
        except URLError as e:
            print("URL Error: %s %s" % (e.reason, url))
        else:
            if os.path.isfile(destination):
                zf = ZipFile(destination, 'r')
                zf.extractall(CONF_DIRECTORY)
                zf.close()

