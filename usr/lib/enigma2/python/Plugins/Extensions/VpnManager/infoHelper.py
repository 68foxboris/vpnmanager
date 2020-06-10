# -*- coding: utf-8 -*-
from Components.MenuList import MenuList
from Components.config import config
from enigma import gFont, getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, \
    RT_VALIGN_CENTER, eTimer
from Tools.LoadPixmap import LoadPixmap
import os
import re

STATUS = "/etc/openvpn/openvpn.stat"

sizes = [(1 << 50L, 'PB'),
         (1 << 40L, 'TB'),
         (1 << 30L, 'GB'),
         (1 << 20L, 'MB'),
         (1 << 10L, 'KB'),
         (1, 'B')
         ]

# Desktop
DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
else:
    skinFactor = 1.5
if DESKTOPSIZE.width() == 1920:
    png_true = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/true_1920.png"
    png_false = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/false_1920.png"
else:
    png_true = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/true_1280.png"
    png_false = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/false_1280.png"


class infoHelper():
    def __init__(self):
        self.infoLabel = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.infoLabel.l.setFont(0, gFont('Vpn', int(27 / skinFactor)))
        self.infoLabel.l.setItemHeight(int(42 / skinFactor))
        self['myInfoLabel'] = self.infoLabel

        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.load_info)

        self.onLayoutFinish.append(self.load_info)

    def load_info(self):
        info = [("OpenVPN Autostart:", config.vpnmanager.autostart.value, True),
                ("Resolv conf:", config.vpnmanager.resolv.value, True)]

        if os.path.isfile("/etc/resolv.conf"):
            with open("/etc/resolv.conf", "r") as resolv_conf:
                x = 1
                for line in resolv_conf.readlines():
                    if "nameserver" in line:
                        dns = "DNS %s:" % str(x)
                        text = re.sub("nameserver", "", line).strip()
                        info.append((dns, text, False))
                        x = x + 1

        if os.path.isfile(STATUS):
            stat = open(STATUS, "r")
            for line in stat.readlines():
                cols = line.split(',')
                if len(cols) == 2:
                    if is_number(cols[1].replace("\n", "")):
                        item = cols[0].replace("bytes", "").strip()
                        item_info = byte2str(int(cols[1].replace("\n", "")))
                        info.append((item, item_info, False))

        self.infoLabel.setList(map(set_info_label, info))
        self['myInfoLabel'].selectionEnabled(0)
        if not self.StatusSpinner:
            self.updateTimer.start(12000, True)


def byte2str(size):
    f = suf = 0
    for f, suf in sizes:
        if size >= f:
            break
    return "%.2f %s" % (size / float(f), suf)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def set_info_label(entry):
    res = [entry]
    if entry[2]:
        res.append(
            (eListboxPythonMultiContent.TYPE_TEXT, int(8 / skinFactor), 0, int(280 / skinFactor), int(42 / skinFactor), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]))
        if entry[1]:
            png = LoadPixmap(png_true)
        else:
            png = LoadPixmap(png_false)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(300 / skinFactor), int(5 / skinFactor), int(45 / skinFactor), int(32 / skinFactor), png))
    else:
        res.append(
            (eListboxPythonMultiContent.TYPE_TEXT, int(8 / skinFactor), 0, int(280 / skinFactor), int(42 / skinFactor), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]))
        res.append(
            (eListboxPythonMultiContent.TYPE_TEXT, int(300 / skinFactor), 0, int(200 / skinFactor), int(42 / skinFactor), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[1]))
    return res
