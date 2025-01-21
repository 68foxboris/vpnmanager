# -*- coding: utf-8 -*-
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import map

from Components.ActionMap import ActionMap, NumberActionMap
from Plugins.Plugin import PluginDescriptor
from Components.Label import Label
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigInteger, ConfigIP, ConfigSelection, getConfigListEntry, ConfigText, \
    ConfigDirectory, \
    ConfigYesNo, configfile, ConfigSelection, ConfigSubsection, ConfigPIN, NoSave, ConfigNothing, ConfigPassword
from Components.FileList import FileList
from enigma import gFont, addFont, eTimer, getDesktop, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, \
    RT_HALIGN_CENTER, RT_VALIGN_CENTER, \
    RT_VALIGN_TOP, RT_WRAP, eListbox, gPixmapPtr, ePicLoad, loadPNG
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Tools.LoadPixmap import LoadPixmap
from Components.MultiContent import MultiContentEntryText
from Screens.VirtualKeyBoard import VirtualKeyBoard

from Components.Network import iNetwork

import shutil
import time
import subprocess
import os
import re
import glob
import ast

from .myScrollBar import my_scroll_bar
from .infoHelper import infoHelper
from .ipinfo import get_ip_info
from .readFreeVpnBook import VpnBook
from .readFreeVpnMe import VpnMe


PLUGINVERSION = "1.1.7"
INFO = "Package: enigma2-plugin-extensions-vpnmanager\nVersion: " + PLUGINVERSION + "\nDescription: Manage your VPN connections\nMaintainer: murxer <support@boxpirates.to>"


damnPanels = ["GoldenPanel", "SatVenusPanel", "GoldenFeed", "PersianDreambox", "DreamOSatDownloader"]
for damnPanel in damnPanels:
    if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/" + damnPanel + "/plugin.pyo"):
        os.remove("/usr/lib/enigma2/python/Plugins/Extensions/" + damnPanel + "/plugin.pyo")
    if os.path.exists("/usr/lib/enigma2/python/Plugins/Extensions/" + damnPanel + "/plugin.py"):
        os.remove("/usr/lib/enigma2/python/Plugins/Extensions/" + damnPanel + "/plugin.py")

RESOLVCONF = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/resolv/update-resolv-conf"
SPINNERDIR = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/spinner/"
ISVPN = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/is_vpn.png"
NOVPN = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/no_vpn.png"

VPNDNS = "/etc/openvpn/vpn_dns"
VPNAUTHFILES = ["/media/usb/openvpnauth", "/media/hdd/openvpnauth"]

config.vpnmanager = ConfigSubsection()
config.vpnmanager.directory = ConfigText(default="/hdd/vpn/", fixed_size=False)
config.vpnmanager.active = ConfigText(default=" ", fixed_size=False)
config.vpnmanager.autostart = ConfigYesNo(default=False)
config.vpnmanager.one_folder = ConfigYesNo(default=False)
config.vpnmanager.resolv = ConfigYesNo(default=True)
config.vpnmanager.dns = ConfigIP(default=[0, 0, 0, 0], auto_jump=True)
config.vpnmanager.username = ConfigText(default="Username", fixed_size=False)
config.vpnmanager.password = ConfigText(default="Password", fixed_size=False)

config.vpnmanager.vpnresolv = ConfigYesNo(default=False)
config.vpnmanager.vpndns1 = ConfigIP(default=[0, 0, 0, 0], auto_jump=True)
config.vpnmanager.vpndns2 = ConfigIP(default=[0, 0, 0, 0], auto_jump=True)

config.vpnmanager.free_mode = ConfigYesNo(default=False)
config.vpnmanager.free_mode_type = ConfigSelection(choices=[("book", "VpnBook")], default="book") #("me", "VpnMe") not more working

# Desktop
DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
    desksize = "_1920"
else:
    skinFactor = 1.5
    desksize = "_1280"


class VpnManagerScreen(Screen, my_scroll_bar, infoHelper):
    def __init__(self, session):
        try:
            addFont("/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/font/OpenSans-Regular.ttf", "Vpn", 100, False)
        except Exception as ex:
            addFont("/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/font/OpenSans-Regular.ttf", "Vpn", 100, False,
                    0)
        if DESKTOPSIZE.width() == 1920:
            self.skin = """
                                    <screen name="VpnManagerScreen" backgroundColor="#00ffffff" position="center,center" size="1920,1080" title="VpnManagerScreen" flags="wfNoBorder">
                                    <eLabel name="BackgroundColor" position="2,2" size="1916,1076" zPosition="1" backgroundColor="#002a2a2a" />
                                    <ePixmap name="logo" position="77,2" size="1018,297" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1920.png" alphatest="blend" zPosition="2" />          
                                    <eLabel name="line1" position="28,299" size="1116,760" zPosition="1" backgroundColor="#00ffffff" />
                                    <eLabel name="line2" position="1122,301" size="20,756" zPosition="2" backgroundColor="#002a2a2a" />
                                    <widget name="vpnlist" position="30,301" size="1090,756" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0" />
                                    <widget name="myScrollBar" position="1122,301" size="20,756" transparent="0" backgroundColor="#002a2a2a" zPosition="3" itemHeight="756"  enableWrapAround="1" />
                                    <eLabel name="line3" position="1188,38" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line5" position="1188,348" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line6" position="1188,1022" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line7" position="1188,1057" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line8" position="1188,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line9" position="1888,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                                    <widget name="hop1_png" position="1190,50" size="128,128" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/no_vpn.png" alphatest="blend" zPosition="2" />
                                    <widget name="hop1" position="1328,40" size="558,300" foregroundColor="#00ffffff"  backgroundColor="#002a2a2a" font="Vpn; 27" valign="top" halign="left"  zPosition="2" transparent="0" />
                                    <widget name="myInfoLabel" position="1190,350" size="694,672" transparent="0" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" itemHeight="42"  enableWrapAround="1" />
                                    <eLabel name="line10" position="1190,1022" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                                    <eLabel text="OpenVpn Stop" position="1190,1024" size="200,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                                    <eLabel name="line10" position="1190,1057" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                                    <eLabel name="line10" position="1390,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line10" position="1392,1022" size="200,2" zPosition="4" backgroundColor="#0000ff00" />
                                    <eLabel text="OpenVpn Start" position="1392,1024" size="200,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" /> 
                                    <eLabel name="line10" position="1392,1057" size="200,2" zPosition="4" backgroundColor="#0000ff00" />
                                    <eLabel name="line11" position="1592,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="Menu" position="1594,1024" size="100,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" /> 
                                    <eLabel name="line12" position="1694,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="OK" position="1696,1024" size="85,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                                    <eLabel name="line13" position="1781,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="V """ + PLUGINVERSION + """" position="1783,1024" size="105,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                                    </screen>
                                    """
        else:
            self.skin = """
                                    <screen name="VpnManagerScreen" backgroundColor="#00ffffff" position="center,center" size="1280,720" title="VpnManagerScreen" flags="wfNoBorder">
                                    <eLabel name="BackgroundColor" position="1,1" size="1277,717" zPosition="1" backgroundColor="#002a2a2a" />
                                    <ePixmap name="logo" position="51,1" size="678,198" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1280.png" alphatest="blend" zPosition="2" />
                                    <eLabel name="line1" position="18,199" size="744,506" zPosition="1" backgroundColor="#00ffffff" />
                                    <eLabel name="line2" position="748,200" size="13,504" zPosition="2" backgroundColor="#002a2a2a" />
                                    <widget name="vpnlist" position="20,200" size="726,504" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0" />
                                    <widget name="myScrollBar" position="748,200" size="13,504" transparent="0" backgroundColor="#002a2a2a" zPosition="3" itemHeight="504"  enableWrapAround="1" />
                                    <eLabel name="line3" position="792,25" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line5" position="792,232" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line6" position="792,681" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line7" position="792,704" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line8" position="792,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line9" position="1258,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                                    <widget name="hop1_png" position="793,33" size="85,85" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/no_vpn.png" alphatest="blend" zPosition="2" />
                                    <widget name="hop1" position="885,26" size="372,200" foregroundColor="#00ffffff"  backgroundColor="#002a2a2a" font="Vpn; 18" valign="top" halign="left"  zPosition="2" transparent="0" />
                                    <widget name="myInfoLabel" position="793,233" size="462,448" transparent="0" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" itemHeight="28"  enableWrapAround="1" />
                                    <eLabel name="line10" position="793,681" size="133,1" zPosition="4" backgroundColor="#00ff0000" />
                                    <eLabel text="OpenVpn Stop" position="793,682" size="133,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                                    <eLabel name="line10" position="793,704" size="133,1" zPosition="4" backgroundColor="#00ff0000" />
                                    <eLabel name="line10" position="926,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel name="line10" position="928,681" size="133,1" zPosition="4" backgroundColor="#0000ff00" />
                                    <eLabel text="OpenVpn Start" position="928,682" size="133,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                                    <eLabel name="line10" position="928,704" size="133,1" zPosition="4" backgroundColor="#0000ff00" /><eLabel name="line11" position="1061,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="Menu" position="1062,682" size="66,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                                    <eLabel name="line12" position="1129,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="OK" position="1130,682" size="56,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                                    <eLabel name="line13" position="1187,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                                    <eLabel text="V """ + PLUGINVERSION + """" position="1188,682" size="70,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                                    </screen>
                                    """
        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OpenVPN_Actions"], {
            "ok": self.keyOK,
            "up": self.keyUp,
            "down": self.keyDown,
            "right": self.keyRight,
            "left": self.keyLeft,
            "red": self.keyRed,
            "green": self.keyGreen,
            "menu": self.keyMenu,
            "cancel": self.keyCancel,
            "info": self.keyInfo,
            "0": self.keyExit
        }, -1)

        self.chooseMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.chooseMenuList.l.setFont(0, gFont('Vpn', int(29 / skinFactor)))
        self.chooseMenuList.l.setItemHeight(int(42 / skinFactor))

        my_scroll_bar.__init__(self, int(756 / skinFactor), int(42 / skinFactor))
        infoHelper.__init__(self)

        # Pixmap
        self["hop1_png"] = Pixmap()
        # Label
        self["hop1"] = Label("")
        self['vpnlist'] = self.chooseMenuList

        self.is_vpn = False

        # OpenVpn Status Check Timer
        self.StatusTimerCheckOpenVpn = eTimer()
        self.StatusCheckOpenVpnTimer = 0
        self.StatusTimerCheckOpenVpn.callback.append(self.checkOpenVpn)

        # Spinner Timer
        self.StatusTimerSpinner = eTimer()
        self.StatusSpinner = False
        self.StatusSpinnerTimer = 0
        self.StatusTimerSpinner.callback.append(self.loadSpinner)

        # Free mode
        self.freeVpnBook = VpnBook()
        self.freeVpnMe = VpnMe()

        self.listVpn = []
        self.onLayoutFinish.append(self.saveDefaultResolv)
        self.onLayoutFinish.append(self.setList)

    def setList(self, reload=None):
        self.listVpn = []
        self.is_vpn = statusTun()

        if config.vpnmanager.free_mode.value:
            if config.vpnmanager.free_mode_type.value == "book":
                self.listVpn = self.freeVpnBook.get_config_data(self.is_vpn)
            else:
                self.listVpn = self.freeVpnMe.get_config_data(self.is_vpn)
        else:
            if os.path.exists(config.vpnmanager.directory.value):
                if not config.vpnmanager.one_folder.value:
                    for directory in os.listdir(config.vpnmanager.directory.value):
                        if os.path.isdir(config.vpnmanager.directory.value + "/" + directory):
                            if config.vpnmanager.active.value == directory:
                                is_connect = True
                                png = 1 if self.is_vpn else 2
                            else:
                                is_connect = False
                                png = 3
                            self.listVpn.append(
                                (directory, config.vpnmanager.directory.value + "/" + directory, is_connect, png))
                else:
                    for conf in os.listdir(config.vpnmanager.directory.value):
                        if os.path.isfile(config.vpnmanager.directory.value + "/" + conf):
                            if conf.endswith("conf") or conf.endswith("ovpn"):
                                if config.vpnmanager.active.value == conf.replace(".conf", "").replace(".ovpn", ""):
                                    is_connect = True
                                    png = 1 if self.is_vpn else 2
                                else:
                                    is_connect = False
                                    png = 3
                                self.listVpn.append(
                                    (conf.replace(".conf", "").replace(".ovpn", ""),
                                     config.vpnmanager.directory.value + "/" + conf, is_connect, png))

        if self.listVpn:
            self.listVpn.sort()
            x = 0
            s = 0
            for title, directory_destination, is_connect, png in self.listVpn:
                if is_connect:
                    s = x
                    break
                x = x + 1
            self.chooseMenuList.setList(list(map(enterListEntry, self.listVpn, )))
            self.chooseMenuList.moveToIndex(s)
            self.loadScrollbar(index=s, max_items=len(self.listVpn))
        self.readIP()
        self.load_info()

    def keyOK(self):
        if not self.StatusSpinner and self.listVpn:
            city = self["vpnlist"].getCurrent()[0][0]
            conf_destination = self["vpnlist"].getCurrent()[0][1]

            config.vpnmanager.active.value = city
            config.vpnmanager.active.save()
            configfile.save()

            # stop openvpn
            if statusTun():
                stop_vpn()
            if self.statusTunOff():
                self.setDefaultDns()
            # del old Config
            if os.path.exists("/etc/openvpn"):
                os.system("rm -R /etc/openvpn/*")
            # write new Config
            new_config = "/etc/openvpn/%s.conf" % city
            new_conf_write = open(new_config, "a")

            conf_file = ""
            if not config.vpnmanager.one_folder.value:
                if os.path.isdir(conf_destination):
                    data = os.listdir(conf_destination)
                    for file in data:
                        if file.endswith("conf") or file.endswith("ovpn"):
                            conf_file = conf_destination + "/" + file
                        else:
                            shutil.copy2(conf_destination + "/" + file, "/etc/openvpn/" + file)
                            os.system("chmod 600 /etc/openvpn/%s" % file)
            else:
                conf_file = conf_destination
                data = os.listdir(config.vpnmanager.directory.value)
                for file in data:
                    file_destination = config.vpnmanager.directory.value + "/" + file
                    if os.path.isfile(file_destination):
                        if not file.endswith("conf"):
                            if not file.endswith("ovpn"):
                                shutil.copy2(file_destination, "/etc/openvpn/" + file)
                                os.system("chmod 600 /etc/openvpn/%s" % file)

            if os.path.isfile(conf_file):
                with open(conf_file, "r") as data:
                    resolv = False
                    security = False
                    for line in data:
                        if re.search("auth-user-pass", line):
                            new_line = "auth-user-pass /etc/openvpn/pass.file\n" \
                                       "log /etc/openvpn/openvpn.log\n" \
                                       "status /etc/openvpn/openvpn.stat 10\n"
                            new_conf_write.write(new_line)
                        elif re.search("up\\s+/etc/openvpn/update-resolv-conf", line):
                            resolv = True
                            if config.vpnmanager.resolv.value:
                                new_line = "setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n" \
                                           "up /etc/openvpn/update-resolv-conf\n"
                                new_conf_write.write(new_line)
                        elif re.search("down\\s+/etc/openvpn/update-resolv-conf", line):
                            if config.vpnmanager.resolv.value:
                                new_line = "down /etc/openvpn/update-resolv-conf\ndown-pre\n"
                                new_conf_write.write(new_line)
                        elif re.search("route-delay", line) or re.search("route-method", line):
                            pass
                        elif re.search("script-security", line):
                            security = True
                            new_conf_write.write(line)
                        elif line[:3] == "dev":
                            new_line = "dev tun\n"
                            new_conf_write.write(new_line)
                        else:
                            new_conf_write.write(line)
                    if not security:
                        new_line = "\nscript-security 2\n"
                        new_conf_write.write(new_line)

                    if not resolv and config.vpnmanager.resolv.value:
                        new_line = "setenv PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n" \
                                   "up /etc/openvpn/update-resolv-conf\n"
                        new_conf_write.write(new_line)

                        new_line = "down /etc/openvpn/update-resolv-conf\ndown-pre\n"
                        new_conf_write.write(new_line)

            # set pass.conf
            if not os.path.isfile("/etc/openvpn/pass.file"):
                pass_file = "/etc/openvpn/pass.file"
                pass_file_write = open(pass_file, "w")
                pass_file_write.write("%s\n%s" % (config.vpnmanager.username.value, config.vpnmanager.password.value))
                pass_file_write.close()

            # close
            new_conf_write.close()

            if os.path.exists("/etc/openvpn"):
                if config.vpnmanager.resolv.value:
                    if config.vpnmanager.vpnresolv.value:
                        dns1 = '%d.%d.%d.%d' % tuple(config.vpnmanager.vpndns1.value)
                        dns2 = '%d.%d.%d.%d' % tuple(config.vpnmanager.vpndns2.value)
                        vpn_dns = open(VPNDNS, "w")
                        vpn_dns.write("nameserver %s\n" % dns1)
                        if not dns2 == "0.0.0.0":
                            vpn_dns.write("nameserver %s\n" % dns2)
                        vpn_dns.close()
                    try:
                        shutil.copyfile(RESOLVCONF, "/etc/openvpn/update-resolv-conf")
                    except shutil.Error as e:
                        print(e)
                    os.system("chmod 755 /etc/openvpn/update-resolv-conf")
                os.system("chmod 600 /etc/openvpn/*.conf")
                os.system("chmod 600 /etc/openvpn/pass.file")

        if not statusTun():
            self["hop1"].setText("Connecting...")
            start_vpn()
            set_auto_start()
            self.StatusSpinner = True
            self.loadSpinner()
            self.checkOpenVpn()
        else:
            self.session.open(MessageBox, "Open Vpn Stop Error: tunnel found", MessageBox.TYPE_ERROR, timeout=10)

    def keyUp(self):
        if self.listVpn:
            if not self.StatusSpinner:
                self['vpnlist'].up()
                index = self['vpnlist'].getSelectionIndex()
                self.loadScrollbar(index=index, max_items=len(self.listVpn))

    def keyDown(self):
        if self.listVpn:
            if not self.StatusSpinner:
                self['vpnlist'].down()
                index = self['vpnlist'].getSelectionIndex()
                self.loadScrollbar(index=index, max_items=len(self.listVpn))

    def keyRight(self):
        if self.listVpn:
            if not self.StatusSpinner:
                self['vpnlist'].pageDown()
                index = self['vpnlist'].getSelectionIndex()
                self.loadScrollbar(index=index, max_items=len(self.listVpn))

    def keyLeft(self):
        if self.listVpn:
            if not self.StatusSpinner:
                self['vpnlist'].pageUp()
                index = self['vpnlist'].getSelectionIndex()
                self.loadScrollbar(index=index, max_items=len(self.listVpn))

    def keyMenu(self):
        if not self.StatusSpinner:
            self.session.openWithCallback(self.Exit, VpnManagerConfigScreen)

    def keyGreen(self):
        # start openvpn
        if not self.StatusSpinner:
            if statusTun():
                stop_vpn()
                if self.statusTunOff():
                    self.setDefaultDns()

            if self.statusTunOff():
                rm_file = ["/etc/openvpn/openvpn.log", "/etc/openvpn/openvpn.stat"]
                for log in rm_file:
                    if os.path.isfile(log):
                        os.system("rm %s" % log)
                start_vpn()
            self["hop1"].setText("Connecting...")
            self.StatusSpinner = True
            self.loadSpinner()
            self.checkOpenVpn()

    def keyRed(self):
        # stop openvpn
        if not self.StatusSpinner:
            if statusTun():
                stop_vpn()
                rm_file = ["/etc/openvpn/openvpn.log", "/etc/openvpn/openvpn.stat"]
                for log in rm_file:
                    if os.path.isfile(log):
                        os.system("rm %s" % log)
            if self.statusTunOff():
                self.setDefaultDns()
                text = "OpenVpn Stop"
                self.session.openWithCallback(self.setList, MessageBox, text, MessageBox.TYPE_INFO, timeout=10)
            else:
                text = "OpenVpn Error: OpenVpn is Running"
                self.session.openWithCallback(self.setList, MessageBox, text, MessageBox.TYPE_ERROR, timeout=10)

    def saveDefaultResolv(self):
        if not statusTun():
            default_dns = '%d.%d.%d.%d' % tuple(config.vpnmanager.dns.value)
            nameserver = []
            if default_dns == "0.0.0.0" and not statusTun():
                try:
                    resolv_file = "/etc/resolv.conf"
                    if os.path.isfile(resolv_file):
                        with open(resolv_file, "r") as resolv_conf:
                            for line in resolv_conf.readlines():
                                if re.search("nameserver", line):
                                    dns = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", line, re.S)
                                    if dns:
                                        nameserver.append(dns[0])
                except:
                    pass
            if nameserver:
                config.vpnmanager.dns.value = [ast.literal_eval(x) for x in nameserver[0].split('.')]
            config.vpnmanager.dns.save()
            configfile.save()

    def setNewDNS(self):
        nameservers = iNetwork.getNameserverList()
        nameserver = []
        for i in range(len(nameservers)):
            iNetwork.removeNameserver(nameservers[0])

        resolv_file = "/etc/resolv.conf"
        try:
            with open(resolv_file, "r") as resolv_conf:
                for line in resolv_conf.readlines():
                    line = line.split('#', 1)[0]
                    line = line.rstrip()
                    if 'nameserver' in line:
                        dns = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", line, re.S)
                        if dns:
                            nameserver.append(dns[0])
        except:
            pass
        if nameserver:
            for dns in nameserver:
                iNetwork.addNameserver([ast.literal_eval(x) for x in dns.split('.')])

    def setDefaultDns(self):
        nameservers = iNetwork.getNameserverList()
        nameserver = []
        for i in range(len(nameservers)):
            iNetwork.removeNameserver(nameservers[0])

        nameserverEntries = [NoSave(ConfigIP(default=nameserver)) for nameserver in nameservers]
        resolv_file = "/etc/resolv.conf"
        try:
            with open(resolv_file, "r") as resolv_conf:
                for line in resolv_conf.readlines():
                    line = line.split('#', 1)[0]
                    line = line.rstrip()
                    if 'nameserver' in line:
                        dns = re.findall("[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", line, re.S)
                        if dns:
                            nameserver.append(dns[0])
        except:
            pass
        if nameserver:
            for dns in nameserver:
                try:
                    iNetwork.addNameserver([ast.literal_eval(x) for x in dns.split('.')])
                except:
                    pass
        self.saveDefaultResolv()

    def checkOpenVpn(self):
        if os.path.isfile("/etc/openvpn/openvpn.log"):
            error = None
            read_log = open("/etc/openvpn/openvpn.log", "r")
            for line in read_log:
                if re.search("AUTH: Received control message: AUTH_FAILED", line):
                    error = "Login Error: AUTH_FAILED"
                    break
                elif re.search("VERIFY ERROR", line):
                    error = "Login Error: VERIFY ERROR"
                    break
            if error:
                self.StatusCheckOpenVpnTimer = 0
                self.StatusSpinner = False
                self.session.open(MessageBox, error, MessageBox.TYPE_ERROR, timeout=10)
                self.setList()
                read_log.close()
                return

            if self.StatusCheckOpenVpnTimer is not 8:
                status = statusTun()
                if status:
                    self.StatusCheckOpenVpnTimer = 0
                    self.StatusSpinner = False
                    self.setNewDNS()
                    time.sleep(2)
                    self.setList()
                else:
                    self.StatusCheckOpenVpnTimer += 1
                    self.StatusTimerCheckOpenVpn.start(3000, True)
            else:
                self.StatusCheckOpenVpnTimer = 0
                self.StatusSpinner = False
                if self.statusTunOn():
                    time.sleep(2)
                    self.setNewDNS()
                self.setList()
            read_log.close()
        else:
            if self.statusTunOn():
                time.sleep(2)
                self.setNewDNS()
            self.StatusSpinner = False
            self.setList()

    def statusTunOn(self):
        x = 0
        while x < 30:
            status = statusTun()
            if status:
                time.sleep(5)
                return True
            time.sleep(1)
            x += 1
        else:
            return False

    def statusTunOff(self):
        x = 0
        while x < 15:
            status = statusTun()
            if not status:
                return True
            time.sleep(1)
            x += 1
        else:
            return False

    def readIP(self):
        tun = statusTun()
        info = get_ip_info(tun=tun)
        png = ISVPN if statusTun() else NOVPN
        self["hop1"].setText(info)
        self.showVpnConnect(png)

    def loadSpinner(self):
        if self.StatusSpinner:
            png = "%s%s.png" % (SPINNERDIR, str(self.StatusSpinnerTimer))
            self.showVpnConnect(png)

    def showVpnConnect(self, png):
        self['hop1_png'].instance.setPixmap(gPixmapPtr())
        self.scale = AVSwitch().getFramebufferScale()
        self.picload = ePicLoad()
        size = self['hop1_png'].instance.size()
        self.picload.setPara((size.width(), size.height(), self.scale[0], self.scale[1], False, 1, "#002a2a2a"))
        decode = self.picload.startDecode(png, 0, 0, False)
        if decode == 0:
            ptr = self.picload.getData()
            if ptr != None:
                self['hop1_png'].instance.setPixmap(ptr)
                self['hop1_png'].show()
                del self.picload
        if self.StatusSpinner:
            if self.StatusSpinnerTimer is not 5:
                self.StatusSpinnerTimer += 1
            else:
                self.StatusSpinnerTimer = 1
            self.StatusTimerSpinner.start(200, True)

    def keyExit(self):
        self.close(self.session, True)

    def Exit(self):
        self.close(self.session, False)

    def keyCancel(self):
        if not self.StatusSpinner:
            self.close(self.session, True)

    def keyInfo(self):
        self.session.open(MessageBox, windowTitle="VPN-Manager Info", text=INFO, type=MessageBox.TYPE_INFO)


class VpnManagerConfigScreen(Screen, ConfigListScreen):
    def __init__(self, session):
        if DESKTOPSIZE.width() == 1920:
            self.skin = """
                        <screen name="VpnManger" backgroundColor="#00ffffff" position="center,center" size="1920,1080" title="VpnManager" flags="wfNoBorder">
                        <eLabel name="BackgroundColor" position="2,2" size="1916,1076" zPosition="1" backgroundColor="#002a2a2a" />
                        <ePixmap name="logo" position="77,2" size="1018,297" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1920.png" alphatest="blend" zPosition="2" />          
                        <widget name="PwLogo" position="1337,550" size="400,52" alphatest="blend" zPosition="4" />
                        <eLabel name="line1" position="28,299" size="1116,760" zPosition="1" backgroundColor="#00ffffff" />
                        <eLabel name="line2" position="1122,301" size="20,756" zPosition="2" backgroundColor="#002a2a2a" />
                        <widget name="config" position="30,301" size="1090,756" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0" />
                        <eLabel name="line3" position="1188,38" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line5" position="1188,348" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line6" position="1188,1022" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line7" position="1188,1057" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line8" position="1188,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="1190,1022" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                        <widget name="myInfoLabel" position="1190,40" size="694,872" transparent="0" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" font="Vpn; 28" valign="center" halign="center"/>
                        
                        <eLabel text="Set Default DNS" position="1190,1024" size="200,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        <eLabel name="line10" position="1190,1057" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                        <eLabel name="line9" position="1888,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="1390,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line11" position="1592,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line12" position="1694,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="OK" position="1696,1024" size="85,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        <eLabel name="line13" position="1781,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="V """ + PLUGINVERSION + """" position="1783,1024" size="105,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        </screen>
                        """
        else:
            self.skin = """
                        <screen name="VpnManager" backgroundColor="#00ffffff" position="center,center" size="1280,720" title="VpnManager" flags="wfNoBorder">
                        <eLabel name="BackgroundColor" position="1,1" size="1277,717" zPosition="1" backgroundColor="#002a2a2a" />
                        <ePixmap name="logo" position="51,1" size="678,198" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1280.png" alphatest="blend" zPosition="2" />
                        <widget name="PwLogo" position="891,366" size="266,34" alphatest="blend" zPosition="4" />
                        <eLabel name="line1" position="18,199" size="744,506" zPosition="1" backgroundColor="#00ffffff" />
                        <eLabel name="line2" position="748,200" size="13,504" zPosition="2" backgroundColor="#002a2a2a" />
                        <widget name="config" position="20,200" size="726,504" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0"/>
                        <eLabel name="line3" position="792,25" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line5" position="792,232" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line6" position="792,681" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line7" position="792,704" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line8" position="792,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line9" position="1258,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="926,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="793,681" size="133,1" zPosition="4" backgroundColor="#00ff0000" />
                        <widget name="myInfoLabel" position="793,26" size="462,581" transparent="0" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" font="Vpn; 18" valign="center" halign="center"/>
                        
                        <eLabel text="Set Default DNS" position="793,682" size="133,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        <eLabel name="line10" position="793,704" size="133,1" zPosition="4" backgroundColor="#00ff0000" /><eLabel name="line11" position="1061,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line12" position="1129,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="OK" position="1130,682" size="56,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        <eLabel name="line13" position="1187,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="V """ + PLUGINVERSION + """" position="1188,682" size="70,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        </screen>
                        """

        Screen.__init__(self, session)
        self.session = session

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions"], {
            "ok": self.keyOK,
            "red": self.keyRed,
            "left": self.keyLeft,
            "right": self.keyRight,
            "up": self.keyUp,
            "down": self.keyDown,
            "cancel": self.keyCancel
        }, -1)

        self["myNumberActions"] = NumberActionMap(["InputActions"], {
            "1": self.keyNumberGlobal,
            "2": self.keyNumberGlobal,
            "3": self.keyNumberGlobal,
            "4": self.keyNumberGlobal,
            "5": self.keyNumberGlobal,
            "6": self.keyNumberGlobal,
            "7": self.keyNumberGlobal,
            "8": self.keyNumberGlobal,
            "9": self.keyNumberGlobal,
            "0": self.keyNumberGlobal
        }, -1)

        self["PwLogo"] = Pixmap()
        self["PwLogo"].hide()
        self["myInfoLabel"] = Label("")

        # Free mode
        self.freeVpnBook = VpnBook()
        self.freeVpnMe = VpnMe()
        self.freeModeProvider = config.vpnmanager.free_mode_type.value

        self.list = []
        self.createConfigList()
        ConfigListScreen.__init__(self, self.list, on_change=self.setInfoTxt)

        for file_destination in VPNAUTHFILES:
            if os.path.isfile(file_destination):
                with open(file_destination, "r") as auth_file:
                    data = auth_file.readlines()
                    if len(data) > 1:
                        config.vpnmanager.username.value = data[0].replace("\n", "").strip()
                        config.vpnmanager.password.value = data[1].replace("\n", "").strip()
                        config.vpnmanager.username.save()
                        config.vpnmanager.password.save()
                        configfile.save()
                        break

        self.onLayoutFinish.append(self.createConfigList)

    def createConfigList(self):
        self.list = []

        self.list.append(getConfigListEntry(_("VPN free mode:"), config.vpnmanager.free_mode))
        if not config.vpnmanager.free_mode.value:
            self.list.append(getConfigListEntry(_("All config's in one folder:"), config.vpnmanager.one_folder))
            self.list.append(getConfigListEntry(_("Storage location for config files:"), config.vpnmanager.directory))
        else:
            self.list.append(getConfigListEntry(_("Provider:"), config.vpnmanager.free_mode_type))

        self.list.append(getConfigListEntry("Default DNS 1:", config.vpnmanager.dns))
        self.list.append(getConfigListEntry("OpenVpn autostart:", config.vpnmanager.autostart))
        self.list.append(getConfigListEntry("OpenVpn resolv:", config.vpnmanager.resolv))
        if config.vpnmanager.resolv.value:
            self.list.append(getConfigListEntry("Set optional VPN DNS server:", config.vpnmanager.vpnresolv))
            if config.vpnmanager.vpnresolv.value:
                self.list.append(getConfigListEntry("VPN -- DNS 1:", config.vpnmanager.vpndns1))
                self.list.append(getConfigListEntry("VPN -- DNS 2:", config.vpnmanager.vpndns2))
        self.list.append(getConfigListEntry("Vpn username", config.vpnmanager.username))
        self.list.append(getConfigListEntry("Vpn password", config.vpnmanager.password))

    def keyNumberGlobal(self, number):
        if self['config'].getCurrent()[1] == config.vpnmanager.username or self['config'].getCurrent()[1] == config.vpnmanager.password:
            if config.vpnmanager.free_mode.value:
                ConfigListScreen.keyNumberGlobal(self, number)
            else:
                title = self['config'].getCurrent()[0]
                text = self['config'].getCurrent()[1].value
                self.session.openWithCallback(self.set_config_value, VirtualKeyBoard, title=title, text=text)
        elif self['config'].getCurrent()[1] == config.vpnmanager.directory:
            self.session.openWithCallback(self.createConfigList, FolderScreen, config.vpnmanager.directory.value)
        else:
            ConfigListScreen.keyNumberGlobal(self, number)

    def set_config_value(self, callback):
        if callback != None:
            config_value = self["config"].getCurrent()[1]
            config_value.value = callback
            config_value.save()
            configfile.save()
            self.changedEntry()

    def keyUp(self):
        self["config"].instance.moveSelection(self["config"].instance.moveUp)
        self.setInfoTxt()

    def keyDown(self):
        if self["config"].getCurrentIndex() < len(self["config"].getList()) - 1:
            self["config"].instance.moveSelection(self["config"].instance.moveDown)
        self.setInfoTxt()

    def changedEntry(self):
        self.createConfigList()
        self["config"].setList(self.list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.changedEntry()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.changedEntry()

    def keyOK(self):
        if self['config'].getCurrent()[1] == config.vpnmanager.directory:
            self.session.openWithCallback(self.createConfigList, FolderScreen, config.vpnmanager.directory.value)
        else:
            if config.vpnmanager.free_mode.value:
                if config.vpnmanager.free_mode_type.value == "book":
                    if not self.freeVpnBook.update:
                        self.session.openWithCallback(self.loadNewConfig, MessageBox, _("No new configs have been loaded yet!\nDownload configs?"), MessageBox.TYPE_YESNO, default=True)
                        return
                else:
                    if not self.freeVpnMe.update:
                        self.session.openWithCallback(self.loadNewConfig, MessageBox, _("No new configs have been loaded yet!\nDownload configs?"), MessageBox.TYPE_YESNO, default=True)
                        return
            self.saveExit()

    def setInfoTxt(self):
        txt = ""
        show = False
        if self['config'].getCurrent()[1] == config.vpnmanager.one_folder:
            txt = _("If all configs are in one folder, please activate this function.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.directory:
            txt = _("Here you can specify the storage location for the configs.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.dns:
            txt = _("Here you can change the standard DNS.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.autostart:
            txt = _("Here you can activate the autostart.\nThus, a VPN connection is started automatically after booting.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.resolv:
            txt = _("If you disable resolvconf, the standard DNS servers are used. This creates a security hole.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.vpnresolv:
            txt = _("Please only activate if you do not want to use the DNS server of the VPN provider.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.free_mode:
            txt = _("This allows you to use free VPN connections.")
        elif self['config'].getCurrent()[1] == config.vpnmanager.free_mode_type:
            txt = _("Here you can choose between different providers.\n\nhttps://www.vpnbook.com/freevpn\nhttps://www.freeopenvpn.me/")
        elif self['config'].getCurrent()[1] == config.vpnmanager.username or self['config'].getCurrent()[1] == config.vpnmanager.password:
            if config.vpnmanager.free_mode.value and self['config'].getCurrent()[1] == config.vpnmanager.username:
                txt = _("Username is set automatically.")
            elif config.vpnmanager.free_mode.value and self['config'].getCurrent()[1] == config.vpnmanager.password:
                txt = _("Please enter the password from the picture.")
                show = True
            else:
                txt = _("1 variant:\nEnter login data\n\n2 variant:\ncreates a text file in /media/hdd or/media/usb, this must be openvpnauth. This openvpnauth file should only consist of 2 lines, these are\nusername\npassword\nIf you now open the settings again, these access data will also be used.\n\n3 variant:\nAdd a file to the configs with the name pass.file. The content of the file consists of 2 lines, like the openvpnauth.")
        if show:
            self.showPwPng()
        else:
            self["PwLogo"].hide()
        self["myInfoLabel"].setText(txt)

    def showPwPng(self):
        png = self.freeVpnBook.PW_PNG
        if os.path.isfile(png):
            self["PwLogo"].instance.setPixmapFromFile(png)
            self["PwLogo"].show()
        else:
            txt = _("Sorry the password image was not found!")
            self["myInfoLabel"].setText(txt)

    def loadNewConfig(self, answer):
        if answer:
            if config.vpnmanager.free_mode_type.value == "book":
                self.freeVpnBook.get_free_vpn()
                self.freeModeProvider = "book"
            else:
                self.freeModeProvider = "me"
                self.freeVpnMe.get_free_vpn()
            self.changedEntry()
        else:
            self.saveExit()

    def saveExit(self):
        if not self.freeModeProvider == config.vpnmanager.free_mode_type.value:
            os.system("rm -R %s" % self.freeVpnBook.CONF_DIRECTORY)
            os.system("mkdir %s" % self.freeVpnBook.CONF_DIRECTORY)
        if config.vpnmanager.free_mode.value:
            config.vpnmanager.directory.value = self.freeVpnBook.CONF_DIRECTORY
            config.vpnmanager.directory.save()
            config.vpnmanager.one_folder.value = True

        config.vpnmanager.free_mode.save()
        config.vpnmanager.free_mode_type.save()
        config.vpnmanager.one_folder.save()
        config.vpnmanager.username.save()
        config.vpnmanager.password.save()
        config.vpnmanager.resolv.save()
        config.vpnmanager.autostart.save()
        config.vpnmanager.vpnresolv.save()
        config.vpnmanager.vpndns1.save()
        config.vpnmanager.vpndns2.save()
        config.vpnmanager.dns.save()
        configfile.save()
        set_auto_start()
        self.close()

    def keyRed(self):
        default_dns1 = '%d.%d.%d.%d' % tuple(config.vpnmanager.dns.value)
        if not default_dns1 == "0.0.0.0":
            try:
                resolv_orig = "/etc/resolv.orig"
                if os.path.isfile(resolv_orig):
                    os.system("sed -i '/nameserver/d' %s" % resolv_orig)
                    os.system("echo nameserver %s >> %s" % (default_dns1, resolv_orig))
            except OSError as e:
                self.session.open(MessageBox, str(e), MessageBox.TYPE_ERROR, timeout=10)
            try:
                resolv_conf = "/etc/resolv.conf"
                if not os.path.islink(resolv_conf):
                    os.system("sed -i '/nameserver/d' %s" % resolv_conf)
                    os.system("echo nameserver %s >> %s" % (default_dns1, resolv_conf))
                if os.path.isfile("/etc/resolvconf.conf"):
                    with open("/etc/resolvconf.conf", "r") as resolv_file:
                        for line in resolv_file.readlines():
                            if re.search("resolv_conf=", line):
                                line = re.sub("resolv_conf=|\n", "", line).strip()
                                resolv_conf = line
                                if os.path.isfile(resolv_conf):
                                    os.system("sed -i '/nameserver/d' %s" % resolv_conf)
                                    os.system("echo nameserver %s >> %s" % (default_dns1, resolv_conf))
                                break
            except OSError as e:
                self.session.open(MessageBox, str(e), MessageBox.TYPE_ERROR, timeout=10)
            else:
                self.session.open(MessageBox, "Default DNS enabled", MessageBox.TYPE_INFO, timeout=10)

    def keyCancel(self):
        if config.vpnmanager.free_mode.value:
            if config.vpnmanager.free_mode_type.value == "book":
                if not self.freeVpnBook.update:
                    self.session.openWithCallback(self.loadNewConfig, MessageBox, _("No new configs have been loaded yet!\nDownload configs?"), MessageBox.TYPE_YESNO, default=True)
                    return
            else:
                if not self.freeVpnMe.update:
                    self.session.openWithCallback(self.loadNewConfig, MessageBox, _("No new configs have been loaded yet!\nDownload configs?"), MessageBox.TYPE_YESNO, default=True)
                    return
        self.saveExit()


class FolderScreen(Screen):
    def __init__(self, session, initDir, plugin_path=None):
        if DESKTOPSIZE.width() == 1920:
            self.skin = """
                        <screen name="VpnManagerScreen" backgroundColor="#00ffffff" position="center,center" size="1920,1080" title="VpnManagerScreen" flags="wfNoBorder">
                        <eLabel name="BackgroundColor" position="2,2" size="1916,1076" zPosition="1" backgroundColor="#002a2a2a" />
                        <ePixmap name="logo" position="77,2" size="1018,297" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1920.png" alphatest="blend" zPosition="2" />          
                        <widget name="media" position="30,304" size="1110,37" foregroundColor="#00ffffff"  backgroundColor="#002a2a2a" font="Vpn; 27" valign="top" halign="left"  zPosition="2" transparent="0" />
                        <eLabel name="line1" position="28,302" size="1114,755" zPosition="1" backgroundColor="#00ffffff" />
                        <widget name="folderlist" scrollbarMode="showOnDemand" position="30,343" size="1110,712" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0" itemHeight="42"/>
                        <eLabel name="line3" position="1188,38" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line5" position="1188,348" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line6" position="1188,1022" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line7" position="1188,1057" size="700,2" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line8" position="1188,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line9" position="1888,38" size="2,1019" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="1190,1022" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                        <eLabel text="Exit" position="1190,1024" size="200,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        <eLabel name="line10" position="1190,1057" size="200,2" zPosition="4" backgroundColor="#00ff0000" />
                        <eLabel name="line10" position="1390,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="1392,1022" size="200,2" zPosition="4" backgroundColor="#0000ff00" />
                        <eLabel text="Save" position="1392,1024" size="200,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" /> 
                        <eLabel name="line10" position="1392,1057" size="200,2" zPosition="4" backgroundColor="#0000ff00" />
                        <eLabel name="line11" position="1592,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line12" position="1694,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="OK" position="1696,1024" size="85,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        <eLabel name="line13" position="1781,1022" size="2,37" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="V """ + PLUGINVERSION + """" position="1783,1024" size="105,33" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 24" valign="top" halign="center" />
                        </screen>
                        """
        else:
            self.skin = """
                        <screen name="VpnManagerScreen" backgroundColor="#00ffffff" position="center,center" size="1280,720" title="VpnManagerScreen" flags="wfNoBorder">
                        <eLabel name="BackgroundColor" position="1,1" size="1277,717" zPosition="1" backgroundColor="#002a2a2a" />
                        <ePixmap name="logo" position="51,1" size="678,198" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/openvpn_logo_1280.png" alphatest="blend" zPosition="2" />
                        <widget name="media" position="20,202" size="740,24" foregroundColor="#00ffffff"  backgroundColor="#002a2a2a" font="Vpn; 18" valign="top" halign="left"  zPosition="2" transparent="0" />
                        <eLabel name="line1" position="18,201" size="744,503" zPosition="1" backgroundColor="#00ffffff" />
                        <widget name="folderlist" scrollbarMode="showOnDemand" position="20,228" size="740,474" backgroundColorSelected="#002f4665" foregroundColorSelected="#00ffffff" foregroundColor="#00ffffff" backgroundColor="#002a2a2a" zPosition="3" transparent="0" itemHeight="28"/>
                        <eLabel name="line3" position="792,25" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line5" position="792,232" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line6" position="792,681" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line7" position="792,704" size="466,1" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line8" position="792,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line9" position="1258,25" size="1,679" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="793,681" size="133,1" zPosition="4" backgroundColor="#00ff0000" />
                        <eLabel text="Exit" position="793,682" size="133,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        <eLabel name="line10" position="793,704" size="133,1" zPosition="4" backgroundColor="#00ff0000" />
                        <eLabel name="line10" position="926,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line10" position="928,681" size="133,1" zPosition="4" backgroundColor="#0000ff00" />
                        <eLabel text="Save" position="928,682" size="133,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        <eLabel name="line10" position="928,704" size="133,1" zPosition="4" backgroundColor="#0000ff00" /><eLabel name="line11" position="1061,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel name="line12" position="1129,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="OK" position="1130,682" size="56,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        <eLabel name="line13" position="1187,681" size="1,24" zPosition="2" backgroundColor="#00ffffff" />
                        <eLabel text="V """ + PLUGINVERSION + """" position="1188,682" size="70,22" backgroundColor="#002a2a2a" transparent="0" foregroundColor="#00ffffff" zPosition="3" font="Vpn; 16" valign="top" halign="center" />
                        </screen>
                        """
        Screen.__init__(self, session)

        directory_data = initDir[:-1].split("/")
        directory = re.sub("/" + directory_data[len(directory_data) - 1], "", initDir) if len(
            directory_data) > 1 else initDir
        if not os.path.isdir(directory):
            directory = "/media/"

        self["folderlist"] = FileList(directory, inhibitMounts=False, inhibitDirs=False, showMountpoints=False,
                                      showFiles=False)

        self["media"] = Label(directory)
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "SetupActions"], {
            "cancel": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.OK,
            "green": self.green,
            "red": self.cancel
        }, -1)

    def cancel(self):
        self.close()

    def green(self):
        config.vpnmanager.directory.value = self["folderlist"].getSelection()[0]
        config.vpnmanager.directory.save()
        configfile.save()
        self.close()

    def up(self):
        self["folderlist"].up()
        self.updateFile()

    def down(self):
        self["folderlist"].down()
        self.updateFile()

    def left(self):
        self["folderlist"].pageUp()
        self.updateFile()

    def right(self):
        self["folderlist"].pageDown()
        self.updateFile()

    def OK(self):
        if self["folderlist"].canDescent():
            self["folderlist"].descent()

    def updateFile(self):
        currFolder = self["folderlist"].getSelection()[0]
        self["media"].setText(currFolder)


def enterListEntry(entry):
    res = [entry]
    if entry[3] == 1:
        png_connect = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/is_connect%s.png" % desksize
    elif entry[3] == 2:
        png_connect = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/error_connect%s.png" % desksize
    else:
        png_connect = "/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/image/no_connect%s.png" % desksize

    # City
    res.append((eListboxPythonMultiContent.TYPE_TEXT, int(20 / skinFactor), 0, int(950 / skinFactor),
                int(38 / skinFactor), 0, RT_HALIGN_LEFT | RT_VALIGN_CENTER, entry[0]))

    png_connect = LoadPixmap(png_connect)
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, int(1039 / skinFactor), 1, int(38 / skinFactor),
                int(38 / skinFactor), png_connect))

    res.append(MultiContentEntryText(pos=(0, int(41 / skinFactor)), size=(int(1090 / skinFactor), 1),
                                     font=0,
                                     flags=0 | 0 | 0,
                                     text="",
                                     backcolor=0xffffff))
    return res


def get_device():
    dev_device = "tun0"
    try:
        if os.path.exists("/etc/openvpn"):
            for i in os.listdir("/etc/openvpn"):
                if i.split('.')[-1] == 'conf':
                    f = open("/etc/openvpn/%s" % i, "r").readlines()
                    for line in f:
                        if "dev" in line:
                            if not "#" == line[0]:
                                dev_device = line[4:].strip() + "0"
                                break
    except:
        dev_device = "tun0"
    return dev_device


def statusTun():
    try:
        tun_status = os.listdir("/sys/devices/virtual/net")
    except:
        tun_status = os.listdir("/sys/class/net")
    return True if get_device() in str(tun_status) else False


def stop_vpn():
    open_vpn_stop = subprocess.Popen(['/etc/init.d/openvpn', 'stop'])
    open_vpn_stop.wait()
    open_vpn_stop = subprocess.Popen(['killall', 'openvpn'])
    open_vpn_stop.wait()


def start_vpn():
    open_vpn_start = subprocess.Popen(['/etc/init.d/openvpn', 'start'])
    open_vpn_start.wait()


def set_auto_start():
    if config.vpnmanager.autostart.value:
        if not glob.glob('/etc/rc3.d/*openvpn'):
            openvpn_autostart = subprocess.Popen(['update-rc.d', 'openvpn', 'defaults'])
            openvpn_autostart.wait()

    else:
        if glob.glob('/etc/rc3.d/*openvpn'):
            openvpn_autostart = subprocess.Popen(['update-rc.d', '-f', 'openvpn', 'remove'])
            openvpn_autostart.wait()


def exit(session, result):
    if not result:
        session.openWithCallback(exit, VpnManagerScreen)


def main(session, **kwargs):
    session.openWithCallback(exit, VpnManagerScreen)


def Plugins(**kwargs):
    if DESKTOPSIZE.width() > 1280:
        return [PluginDescriptor(name=_("Vpn Manager"), description="Manage your VPN connections",
                                 where=PluginDescriptor.WHERE_PLUGINMENU, icon="pluginfhd.png", fnc=main),
                PluginDescriptor(name=_("Vpn Manager"), description="Manage your VPN connections",
                                 where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
    else:
        return [PluginDescriptor(name=_("Vpn Manager"), description="Manage your VPN connections",
                                 where=PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main),
                PluginDescriptor(name=_("Vpn Manager"), description="Manage your VPN connections",
                                 where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
