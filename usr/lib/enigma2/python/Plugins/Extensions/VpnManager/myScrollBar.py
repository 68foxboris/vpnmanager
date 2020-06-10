# -*- coding: utf-8 -*-
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from enigma import gFont, getDesktop, eListboxPythonMultiContent

import math

SCROLLBARBACKCOLOR = 0x000000
SCROLLBARSLIDERCOLOR = 0x2f4665

DESKTOPSIZE = getDesktop(0).size()
if DESKTOPSIZE.width() > 1280:
    skinFactor = 1
else:
    skinFactor = 1.5


class my_scroll_bar():
    def __init__(self, height_list, label_height):
        self.Scrollbar = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
        self.Scrollbar.l.setFont(0, gFont('Regular', 1))
        self['myScrollBar'] = self.Scrollbar

        self.isShow = False
        self.wight = None
        self.height = 1
        self.wight_slider = None
        self.height_slider = None
        self.height_list = height_list
        self.label_height = label_height
        self.max_label_page = None
        self.wight_background = None

        self.onLayoutFinish.append(self.doHideScrollbar)
        self.onLayoutFinish.append(self.setSize)

    def doHideScrollbar(self):
        self['myScrollBar'].hide()
        self.isShow = False

    def doShowScrollbar(self):
        self['myScrollBar'].show()
        self.isShow = True

    def setSize(self):
        self.max_label_page = (self.height_list / self.label_height)
        self.wight_slider = int(6 / skinFactor)
        self.wight = int(7 / skinFactor)
        self.wight_background = int(2 / skinFactor)

    def loadScrollbar(self, index=0, max_items=0, new_scall=None):
        if self.height_list and self.label_height and self.max_label_page < max_items:
            max_items_show = self.height_list / self.label_height
            # Slider max pos
            max_slider_pos = int(round(math.ceil(max_items / (max_items_show + 0.0)), 0))
            # Slider height
            self.height_slider = int(self.height_list / max_slider_pos)

            x = self.max_label_page
            s = 0
            for i in range(max_slider_pos):
                if index < x:
                    if max_items - (max_items - index) >= max_items - 1:
                        s = self.height_list - self.height_slider
                    break
                x = x + self.max_label_page
                s = s + self.height_slider
            if not self.height == s or new_scall:
                self.height = s
                self.Scrollbar.setList(map(self.set_scrollbar, [1]))
                self['myScrollBar'].selectionEnabled(0)
                if not self.isShow:
                    self.doShowScrollbar()
        else:
            if self.isShow:
                self.doHideScrollbar()

    def set_scrollbar(self, entry):
        res = [entry]
        res.append(MultiContentEntryText(pos=(int(9 / skinFactor), 0), size=(self.wight_background, self.height_list),
                                         backcolor=SCROLLBARBACKCOLOR))
        res.append(MultiContentEntryText(pos=(self.wight, self.height), size=(self.wight_slider, self.height_slider),
                                         backcolor=SCROLLBARSLIDERCOLOR))
        return res
