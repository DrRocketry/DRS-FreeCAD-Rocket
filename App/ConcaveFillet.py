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
"""Class for drawing concave fillets"""

__title__ = "FreeCAD Concave Fillets"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

from DraftTools import translate

def _isVertical(point1, point2):
    return (point1.y == point2.y)

def _isHorizontal(point1, point2)
    return (point1.x == point2.x)

def _line(point1, point2):
    # Line is not vertical
    rise = point1.y - point2.y
    run = point1.x - point2.x
    slope = rise / run
    intercept = point1.y - (slope * point1.x)
    return slope, intercept

def _parallel(point1, point2, distance):
    slope, intercept = _line(point1, point2)
    if slope < 0:                   # This needs more work to ensure we're in the upper left (or right?) quadrant
        distance = -distance
    b2 = distance * math.sqrt(slope * slope + 1) + intercept
    return slope, b2

def tubeFillet(filletRadius, tubeRadius, point1, point2):
    #
    # Returns the center point for the fillet radius that is tangent to the body tube
    # and the line formed by the two points.
    #
    # The body tube diameter and the line need to be coplanar in the x,y plane
    #
    return FreeCAD.Vector(0, 0, 0)

def planeFillet(filletRadius, point1, point2, point3, point4):
    #
    # Returns the center point for the fillet radius that is tangent to the lines formed
    # by (point1, point2) and (point3, point4). The lines can not be parallel
    #
    # The lines need to be coplanar in the x,y plane
    #
    if _isVertical(point1, point2):
        x = point1.x - filletRadius
        if _isHorizontal(point3, point4):
            y = point3.y + filletRadius
        else:
            slope, intercept = _parallel(point3, point4, filletRadius)
            y = slope * x + intercept
        return FreeCAD.Vector(x, y, 0)
    elif _isVertical(point3, point4):
        x = point3.x - filletRadius
        if _isHorizontal(point1, point2):
            y = point1.y + filletRadius
        else:
            slope, intercept = _parallel(point1, point2, filletRadius)
            y = slope * x + intercept
        return FreeCAD.Vector(x, y, 0)

    slope1, intercept1 = _parallel(point1, point2, filletRadius)
    slope2, intercept2 = _parallel(point3, point4, filletRadius)
    x = (intercept2 - intercept1) / (slope1 - slope2)
    y = slope1 * x + intercept1
    return FreeCAD.Vector(x, y, 0)
