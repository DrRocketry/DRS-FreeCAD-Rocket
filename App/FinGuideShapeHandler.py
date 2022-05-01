# ***************************************************************************
# *   Copyright (c) 2022 David Carter <dcarter@davidcarter.ca>              *
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
"""Class for drawing fin guides"""

__title__ = "FreeCAD Fin Guide Handler"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
import FreeCAD
import Part
import math

from App.Utilities import _err
from DraftTools import translate

class FinGuideShapeHandler():
    def __init__(self, obj):

        # This gets changed when redrawn so it's very important to save a copy
        self._placement = obj.Placement

        self._diameter = float(obj.Diameter)
        self._radius = self._diameter / 2.0
        self._rootThickness = float(obj.RootThickness)
        self._tipThickness = float(obj.TipThickness)
        self._span = float(obj.Span)
        self._finCount = int(obj.FinCount)
        self._glueRadius = float(obj.GlueRadius)
        self._length = float(obj.Length)
        self._thickness = float(obj.Thickness)

        self._obj = obj

    def isValidShape(self):
        # Perform some general validations
        # if self._diameter <= 0:
        #     _err(translate('Rocket', "Outer diameter must be greater than zero"))
        #     return False

        # if self._step:
        #     if self._stepDiameter <= 0:
        #         _err(translate('Rocket', "Step diameter must be greater than zero"))
        #         return False
        #     if self._stepDiameter >= self._diameter:
        #         _err(translate('Rocket', "Step diameter must less than the outer diameter"))
        #         return False

        # if self._holes:
        #     if self._holeDiameter <= 0:
        #         _err(translate('Rocket', "Hole diameter must be greater than zero"))
        #         return False
        #     if self._holeCenter + (self._holeDiameter / 2.0) >= (self._diameter / 2.0):
        #         _err(translate('Rocket', "Hole extends outside the outer diameter"))
        #         return False
        #     if self._step:
        #         if self._holeCenter + (self._holeDiameter / 2.0) >= (self._stepDiameter / 2.0):
        #             _err(translate('Rocket', "Hole extends outside the step diameter"))
        #             return False

        return True

    def _makeFace(self, obj):
        return Part.Face(Part.Wire(obj))

    def _makeProfile(self, offset = 0.0):
        profile = Part.makeCircle(self._radius + offset)
        profileFace = self._makeFace(profile)

        fin = Part.makePolygon([
            FreeCAD.Vector(0, 0),
            FreeCAD.Vector(0, self._radius + self._span + offset),
            FreeCAD.Vector(self._tipThickness / 2.0 + offset, self._radius + self._span + offset),
            FreeCAD.Vector(self._rootThickness / 2.0 + offset, self._radius + offset),
            FreeCAD.Vector(self._rootThickness / 2.0 + offset, 0),
            FreeCAD.Vector(0, 0)
        ])

        mirror = FreeCAD.Matrix()
        mirror.rotateY(math.pi)

        finFace = self._makeFace(fin)

        mirrorFin = finFace.copy()
        mirrorFin.transformShape(mirror)

        fusedFin = finFace.fuse(mirrorFin)

        if self._glueRadius > 0:
            circle = Part.makeCircle(self._glueRadius + offset, FreeCAD.Vector(self._rootThickness / 2.0, self._radius), FreeCAD.Vector(0, 0, 1))
            circleFace = self._makeFace(circle)

            mirrorCircle = circleFace.copy()
            mirrorCircle.transformShape(mirror)
            fusedFin = fusedFin.fuse(circleFace)
            fusedFin = fusedFin.fuse(mirrorCircle)

        fused = profileFace.fuse(fusedFin)
        for i in range(1, self._finCount):
            print(i)
            mirror = FreeCAD.Matrix()
            mirror.rotateZ((2 / self._finCount) * i * math.pi)
            rotatedFin = fusedFin.copy()
            rotatedFin.transformShape(mirror)
            fused = fused.fuse(rotatedFin)

        return fused

    def _drawFinGuide(self):
        innerProfile = self._makeProfile()
        outerProfile = self._makeProfile(self._thickness)
        profile = outerProfile.cut(innerProfile)

        guide = profile.extrude(FreeCAD.Vector(0, 0, self._length))
        return guide
        
    def draw(self):
        if not self.isValidShape():
            return

        try:
            self._obj.Shape = self._drawFinGuide()
        except (Part.OCCError):
            _err(translate('Rocket', "Fin guide parameters produce an invalid shape"))
            return
