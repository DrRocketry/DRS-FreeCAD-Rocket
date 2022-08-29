# ***************************************************************************
# *   Copyright (c) 2021 David Carter <dcarter@davidcarter.ca>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""Provides support for importing Open Rocket files."""

__title__ = "FreeCAD Open Rocket Importer Common Component"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

from App.Importer.SaxElement import Element
from App.Constants import LOCATION_PARENT_TOP, LOCATION_PARENT_MIDDLE, LOCATION_PARENT_BOTTOM, \
    LOCATION_BASE, LOCATION_AFTER

class ComponentElement(Element):

    def __init__(self, parent, tag, attributes, parentObj, filename, line):
        super().__init__(parent, tag, attributes, parentObj, filename, line)

        self._componentTags = ["name", "color", "linestyle", "position", "axialoffset", "overridemass", "overridecg", "overridecd", 
            "overridesubcomponents", "comment", "preset", "finish", "material"]

    def handleTag(self, tag, attributes):
        _tag = tag.lower().strip()
        if _tag == "position":
            positionType = attributes["type"]
            print("positionType = %s" % (positionType))
            if positionType == "after":
                self.onPositionType(LOCATION_AFTER)
            elif positionType == "top":
                self.onPositionType(LOCATION_PARENT_TOP)
            elif positionType == "middle":
                self.onPositionType(LOCATION_PARENT_MIDDLE)
            elif positionType == "bottom":
                self.onPositionType(LOCATION_PARENT_BOTTOM)
            else:
                self.onPositionType(LOCATION_BASE)
        else:
            super().handleTag(tag, attributes)

    def handleEndTag(self, tag, content):
        _tag = tag.lower().strip()
        if _tag == "name":
            self.onName(content)
        elif _tag == "color":
            self.onColor(content)
        elif _tag == "linestyle":
            self.onLinestyle(content)
        elif _tag == "position":
            self.onPosition(content)
        elif _tag == "axialoffset":
            pass
        elif _tag == "overridemass":
            # diameter = float(content) * 2.0
            # self._obj.Diameter = str(diameter) + "m"
            pass
        elif _tag == "overridecg":
            pass
        elif _tag == "overridecd":
            pass
        elif _tag == "overridesubcomponents":
            pass
        elif _tag == "comment":
            self.onComment(content)
        elif _tag == "preset":
            self.onPreset(content)
        else:
            super().handleEndTag(tag, content)

    def onName(self, content):
        pass

    def onColor(self, content):
        pass

    def onLinestyle(self, content):
        pass

    def onComment(self, content):
        pass

    def onPreset(self, content):
        pass

    def onPositionType(self, value):
        pass

    def onPosition(self, content):
        pass