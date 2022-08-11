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
"""Class for drawing fins"""

__title__ = "FreeCAD Fins"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"

import FreeCAD
import Part
import math

from App.Constants import FIN_CROSS_SQUARE, FIN_CROSS_ROUND, FIN_CROSS_AIRFOIL, FIN_CROSS_WEDGE, \
    FIN_CROSS_DIAMOND, FIN_CROSS_TAPER_LE, FIN_CROSS_TAPER_TE, FIN_CROSS_TAPER_LETE
from App.Constants import FIN_CROSS_SAME

from App.FinShapeHandler import FinShapeHandler

from App.ConcaveFillet import tubeFillet, planeFillet

class FinTrapezoidShapeHandler(FinShapeHandler):

    def __init__(self, obj):
        super().__init__(obj)

    def _makeRootProfile(self):
        # Create the root profile, casting everything to float to avoid typing issues
        if self._obj.RootPerCent:
            rootLength2 = float(self._obj.RootLength2)
        else:
            rootLength2 = float(self._obj.RootChord) - float(self._obj.RootLength2)
        return self._makeChordProfile(self._obj.RootCrossSection, float(self._obj.RootChord), float(self._obj.RootChord), float(self._obj.RootThickness), 0.0, self._obj.RootPerCent, float(self._obj.RootLength1), rootLength2)

    def _makeFilletRootProfile(self):
        # Create the root profile, casting everything to float to avoid typing issues
        if self._obj.RootPerCent:
            rootLength2 = float(self._obj.RootLength2)
        else:
            rootLength2 = float(self._obj.RootChord) - float(self._obj.RootLength2)
        fillet = float(self._obj.FilletRadius)
        return self._makeChordProfile(self._obj.RootCrossSection, 
                                        float(self._obj.RootChord) + fillet, 
                                        float(self._obj.RootChord) + 2 * fillet, 
                                        float(self._obj.RootThickness) + 2 * fillet,
                                        0.0, 
                                        self._obj.RootPerCent, 
                                        float(self._obj.RootLength1), 
                                        rootLength2)

    def _makeTipProfile(self):
        # Create the tip profile, casting everything to float to avoid typing issues
        crossSection = self._obj.TipCrossSection
        if crossSection == FIN_CROSS_SAME:
            crossSection = self._obj.RootCrossSection
        if self._obj.TipPerCent:
            tipLength2 = float(self._obj.TipLength2)
        else:
            tipLength2 = float(self._obj.TipChord) - float(self._obj.TipLength2)
        return self._makeChordProfile(crossSection, float(self._obj.RootChord - self._obj.SweepLength), float(self._obj.TipChord), float(self._obj.TipThickness), float(self._obj.Height), self._obj.TipPerCent, float(self._obj.TipLength1), tipLength2)

    def _makeFilletTipProfile(self):
        # Create the tip profile, casting everything to float to avoid typing issues
        crossSection = self._obj.TipCrossSection
        if crossSection == FIN_CROSS_SAME:
            crossSection = self._obj.RootCrossSection
        if self._obj.TipPerCent:
            tipLength2 = float(self._obj.TipLength2)
        else:
            tipLength2 = float(self._obj.TipChord) - float(self._obj.TipLength2)
        return self._makeChordProfile(crossSection, float(self._obj.RootChord - self._obj.SweepLength), float(self._obj.TipChord), float(self._obj.TipThickness), float(self._obj.Height), self._obj.TipPerCent, float(self._obj.TipLength1), tipLength2)

    def _makeProfiles(self):
        profiles = []
        profiles.append(self._makeRootProfile())
        profiles.append(self._makeTipProfile())
        return profiles

    def _showPoint(self, message, point):
        print("%s (%f, %f, %f)" %
            (
                message,
                point.x,
                point.y,
                point.z
            ))

    def _makeSquare(x, y1, y2, z1, z2):
        line1 = Part.makeLine()

    def _xAtZ(self, point1, point2, z):
        x1 = point1.x
        z1 = point1.z
        x2 = point2.x # Assume z2 = 0

        x = x2 - z * (x2 - x1) / z1
        return x

    def _yAtZ(self, point1, point2, z):
        y1 = point1.y
        z1 = point1.z
        y2 = point2.y # Assume z2 = 0

        y = y2 - z * (y2 - y1) / z1
        return y

    def _xyAtZ(self, point1, point2, z):
        return self._xAtZ(point1, point2, z), self._yAtZ(point1, point2, z)
        
    def _makeAftFillet(self):
        aft, aftTan = self._aftFillet()

        # Need a 3D object to cut the face
        cylinder = Part.makeCylinder(float(self._obj.FilletRadius), 1.0, aft, FreeCAD.Vector(0, 1, 0))

        v1 = FreeCAD.Vector(aft.x, aft.y, 0)
        v2 = FreeCAD.Vector(0, 0, 0)
        v3 = FreeCAD.Vector(aftTan.x, aftTan.y, aftTan.z)
        profile = Part.makePolygon([v1, v2, v3, v1])

        face = Part.Face(profile)
        face = face.cut(cylinder)

        # Need to give the face some depth to see it
        # fillet = face.extrude(FreeCAD.Vector(0,-1,0))
        # Part.show(fillet)

        return face.Wires[0]
        # return face.OuterWire
        
    def _makeForeFillet(self):
        fore, foreTan = self._foreFillet()

        # Need a 3D object to cut the face
        cylinder = Part.makeCylinder(float(self._obj.FilletRadius), 1.0, fore, FreeCAD.Vector(0, 1, 0))

        v1 = FreeCAD.Vector(foreTan.x, foreTan.y, foreTan.z)
        v2 = FreeCAD.Vector(float(self._obj.RootChord), 0, 0)
        v3 = FreeCAD.Vector(fore.x, fore.y, 0)
        profile = Part.makePolygon([v1, v2, v3, v1])

        face = Part.Face(profile)
        # face = face.cut(cylinder)

        # Need to give the face some depth to see it
        # fillet = face.extrude(FreeCAD.Vector(0,-1,0))
        # Part.show(fillet)

        return face.OuterWire
        
    def _makeAftSideFillet(self):
        chord = self._chordFillet()

        # Need a 3D object to cut the face
        point = FreeCAD.Vector(-float(self._obj.SweepLength), chord.y, chord.z)
        length = float(self._obj.RootChord + self._obj.SweepLength)
        cylinder = Part.makeCylinder(float(self._obj.FilletRadius), length, point, FreeCAD.Vector(1, 0, 0))

        x, y = self._xyAtZ(
            FreeCAD.Vector(float(self._obj.RootChord - self._obj.SweepLength - self._obj.TipChord), float(self._obj.TipThickness) / 2.0, float(self._obj.Height)), 
            FreeCAD.Vector(0, float(self._obj.RootThickness) / 2.0, 0.0),
            float(self._obj.FilletRadius))
        v1 = FreeCAD.Vector(x, -y, float(self._obj.FilletRadius))
        v2 = FreeCAD.Vector(0, -float(self._obj.RootThickness) / 2.0, 0)
        v3 = FreeCAD.Vector(0, -(float(self._obj.RootThickness) / 2.0 + float(self._obj.FilletRadius)), 0)
        profile = Part.makePolygon([v1, v2, v3, v1])

        face = Part.Face(profile)
        face = face.cut(cylinder)

        # Need to give the face some depth to see it
        # fillet = face.extrude(FreeCAD.Vector(1,0,0))
        # Part.show(fillet)

        return face.Wires[0]
        # return face.OuterWire
        
    def _makeForeSideFillet(self):
        chord = self._chordFillet()

        # Need a 3D object to cut the face
        point = FreeCAD.Vector(-float(self._obj.SweepLength), chord.y, chord.z)
        length = float(self._obj.RootChord + self._obj.SweepLength)
        cylinder = Part.makeCylinder(float(self._obj.FilletRadius), length, point, FreeCAD.Vector(1, 0, 0))

        x, y = self._xyAtZ(
            FreeCAD.Vector(float(self._obj.RootChord - self._obj.SweepLength), float(self._obj.TipThickness) / 2.0, float(self._obj.Height)), 
            FreeCAD.Vector(float(self._obj.RootChord), float(self._obj.RootThickness) / 2.0, 0.0),
            float(self._obj.FilletRadius))
        v1 = FreeCAD.Vector(x, -y, float(self._obj.FilletRadius))
        v2 = FreeCAD.Vector(float(self._obj.RootChord), -float(self._obj.RootThickness) / 2.0, 0)
        v3 = FreeCAD.Vector(float(self._obj.RootChord), -(float(self._obj.RootThickness) / 2.0 + float(self._obj.FilletRadius)), 0)
        profile = Part.makePolygon([v1, v2, v3, v1])

        face = Part.Face(profile)
        # face = face.cut(cylinder)

        # Need to give the face some depth to see it
        # fillet = face.extrude(FreeCAD.Vector(-1,0,0))
        # Part.show(fillet)

        return face.OuterWire
        
    def _drawFilletSquare(self):
        aftFace = self._makeAftFillet()
        foreFace = self._makeForeFillet()
        aftSideFace = self._makeAftSideFillet()
        foreSideFace = self._makeForeSideFillet()

        # wire = aftSideFace.Wires[0]
        # loft = Part.makeLoft([aftFace, aftSideFace], True)
        # loft = loft.fuse(Part.makeLoft([aftSideFace, foreSideFace], True))
        # loft = loft.fuse(Part.makeLoft([foreSideFace, foreFace], True))
        loft = Part.makeLoft([aftSideFace, foreSideFace], True)

        # Part.show(loft)

        fore, foreTan = self._foreFillet()
        aft, aftTan = self._aftFillet()
        chord = self._chordFillet()

        length = fore.x - aft.x
        width = 2 * math.fabs(chord.y)
        height = chord.z
        point = FreeCAD.Vector(aft.x, chord.y, 0)
        dir = FreeCAD.Vector(0, 0, 1)
        # loft = Part.makeBox(length, width, height, point, dir)

        # thickness = float(self._obj.RootThickness) / 2.0
        radius = math.fabs(chord.y)
        arc1 = Part.Arc(
            FreeCAD.Vector(aft.x + radius,  -radius, chord.z), 
            FreeCAD.Vector(aft.x,  0.0, chord.z), 
            FreeCAD.Vector(aft.x + radius,  radius, chord.z))
        line1 = Part.LineSegment( FreeCAD.Vector(aft.x + radius,  radius, chord.z),
             FreeCAD.Vector(fore.x - radius,  radius, chord.z))
        arc2 = Part.Arc(
            FreeCAD.Vector(fore.x - radius,  radius, chord.z), 
            FreeCAD.Vector(fore.x,  0.0, chord.z), 
            FreeCAD.Vector(fore.x - radius,  -radius, chord.z))
        line2 = Part.LineSegment( FreeCAD.Vector(fore.x - radius,  -radius, chord.z),
             FreeCAD.Vector(aft.x + radius,  -radius, chord.z))

        wire = Part.Wire([arc1.toShape(), line1.toShape(), arc2.toShape(), line2.toShape()])
        path = Part.Shape(wire)

        sweep = Part.BRepOffsetAPI.MakePipeShell(Part.Wire(path))

        # add the profile "wire"
        circle = Part.makeCircle(float(self._obj.FilletRadius), chord, FreeCAD.Vector(1, 0, 0))
        # sweep.add(Part.Wire(circle))
        sweep.add(aftSideFace)

        # check and build
        if sweep.isReady():
            sweep.build()

        # make solid ( if you wish )
        sweep.makeSolid()
        # cShape = sweep.shape()

        # display the result :
        # loft = loft.cut(sweep.shape())
        # Part.show(loft)
        # Part.show(sweep.shape())

        # path = None
        return sweep.shape()
        
    def _drawFilletAirfoil(self):
        radius = math.fabs(self._obj.FilletRadius)

        print("start calc")

        point1 = FreeCAD.Vector(float(self._obj.RootChord) - float(self._obj.SweepLength), 0, float(self._obj.Height))
        point2 = FreeCAD.Vector(float(self._obj.RootChord), 0, 0)
        fore = self._xAtZ(point1, point2, radius)

        point1 = FreeCAD.Vector(float(self._obj.RootChord) - float(self._obj.SweepLength) - float(self._obj.TipChord), 0, float(self._obj.Height))
        point2 = FreeCAD.Vector(0,0,0)
        aft = self._xAtZ(point1, point2, radius)

        point1 = FreeCAD.Vector(0, float(self._obj.TipThickness) / 2.0, float(self._obj.Height))
        point2 = FreeCAD.Vector(0, float(self._obj.RootThickness) / 2.0, 0)
        chord = self._yAtZ(point1, point2, radius)

        print("fore %f" % fore)
        print("aft %f" % aft)
        print("chord %f" % chord)

        # fore, foreTan = self._foreFillet()
        # aft, aftTan = self._aftFillet()
        # chord = self._chordFillet()

        upper = self._makeChordProfileAirfoil(
            fore, 
            fore - aft, 
            2 * chord, 
            radius)
        lower = self._makeChordProfileAirfoil(float(self._obj.RootChord) + radius, float(self._obj.RootChord) + 2 * radius, float(self._obj.RootThickness) + 2 * radius, 0.0)
        path = self._makeChordProfileAirfoilHalf(float(self._obj.RootChord) + radius, float(self._obj.RootChord) + 2 * radius, float(self._obj.RootThickness) + 2 * radius, radius)


        loft = Part.makeLoft([upper, lower], True)

        sweep = Part.BRepOffsetAPI.MakePipeShell(Part.Wire(path))

        # add the profile "wire"
        circle = Part.makeCircle(float(self._obj.FilletRadius), FreeCAD.Vector(-radius, 0, radius), FreeCAD.Vector(1, 0, 0))
        # circle = Part.makeCircle(float(self._obj.FilletRadius), FreeCAD.Vector(fore + radius, 0, radius), FreeCAD.Vector(0, 1, 0))
        sweep.add(Part.Wire(circle))
        # sweep.add(aftSideFace)

        # check and build
        if sweep.isReady():
            sweep.build()

        # make solid ( if you wish )
        sweep.makeSolid()
        # cShape = sweep.shape()

        # display the result :
        # loft = loft.cut(sweep.shape())
        # Part.show(loft)
        Part.show(sweep.shape())
        # Part.show(path)

        # path = None
        # return sweep.shape()
        return loft
        
    def _drawFillet(self):
        crossSection = self._obj.RootCrossSection

        if crossSection == FIN_CROSS_SQUARE:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_ROUND:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_AIRFOIL:
            return self._drawFilletAirfoil()
        elif crossSection == FIN_CROSS_WEDGE:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_DIAMOND:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_TAPER_LE:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_TAPER_TE:
            return self._drawFilletSquare()
        elif crossSection == FIN_CROSS_TAPER_LETE:
            return self._drawFilletSquare()

        return None

    def _aftFillet(self):
        point1 = FreeCAD.Vector(0,0,0)
        point2 = FreeCAD.Vector(float(self._obj.RootChord) - float(self._obj.SweepLength) - float(self._obj.TipChord), float(self._obj.Height),0)
        point3 = point1
        point4 = FreeCAD.Vector(-1,0,0)
        fillet, tan1, tan2 = planeFillet(float(self._obj.FilletRadius), point1, point2, point3, point4)
        return FreeCAD.Vector(fillet.x, 0, fillet.y), FreeCAD.Vector(tan1.x, 0, tan1.y)

    def _chordFillet(self):
        point1 = FreeCAD.Vector(-float(self._obj.RootThickness) / 2.0, 0, 0)
        point2 = FreeCAD.Vector(-float(self._obj.TipThickness) / 2.0, float(self._obj.Height), 0)
        fillet, tan1, tan2 = tubeFillet(float(self._obj.FilletRadius), float(self._obj.ParentRadius), point1, point2)
        return FreeCAD.Vector(0, fillet.x, fillet.y)

    def _foreFillet(self):
        point1 = FreeCAD.Vector(0,0,0)
        point2 = FreeCAD.Vector(float(self._obj.SweepLength), float(self._obj.Height),0)
        point3 = point1
        point4 = FreeCAD.Vector(-1,0,0)
        fillet, tan1, tan2 = planeFillet(float(self._obj.FilletRadius), point1, point2, point3, point4)

        # v0 = FreeCAD.Vector(float(self._obj.RootChord) - fillet.x, 0, fillet.y)
        # v1 = FreeCAD.Vector(float(self._obj.RootChord) - tan1.x, 0, tan1.y)
        # v2 = FreeCAD.Vector(float(self._obj.RootChord) - tan2.x, 0, tan2.y)
        # line1 = Part.LineSegment(v0, v1)
        # Part.show(line1.toShape())
        # line2 = Part.LineSegment(v0, v2)
        # Part.show(line2.toShape())

        # self._showPoint("fore fillet", fillet)
        # self._showPoint("fore fillet tan1", tan1)
        # self._showPoint("fore fillet tan2", tan2)
        return FreeCAD.Vector(float(self._obj.RootChord) - fillet.x, 0, fillet.y), FreeCAD.Vector(float(self._obj.RootChord) - tan1.x, 0, tan1.y)

    def _foreCrossFillet(self):
        point1 = FreeCAD.Vector(0,0,0)
        point2 = FreeCAD.Vector(float(self._obj.SweepLength), float(self._obj.Height),0)
        point3 = point1
        point4 = FreeCAD.Vector(-1,0,0)
        fillet, tan1, tan2 = planeFillet(float(self._obj.FilletRadius), point1, point2, point3, point4)
        self._showPoint("fore fillet", fillet)
        return FreeCAD.Vector(float(self._obj.RootChord) - fillet.x, 0, fillet.y)

    def _makeFilletProfileSquare(self):
        fore = self._foreFillet()
        aft = self._aftFillet()
        chord = self._chordFillet()
        return None

    def _makeFilletProfiles(self):
        crossSection = self._obj.RootCrossSection

        if crossSection == FIN_CROSS_SQUARE:
            return self._makeFilletProfileSquare()
        # elif crossSection == FIN_CROSS_ROUND:
        #     return self._makeChordProfileRound(foreX, chord, thickness, height)
        # elif crossSection == FIN_CROSS_AIRFOIL:
        #     return self._makeChordProfileAirfoil(foreX, chord, thickness, height)
        # elif crossSection == FIN_CROSS_WEDGE:
        #     return self._makeChordProfileWedge(foreX, chord, thickness, height)
        # elif crossSection == FIN_CROSS_DIAMOND:
        #     return self._makeChordProfileDiamond(foreX, chord, thickness, height, l1)
        # elif crossSection == FIN_CROSS_TAPER_LE:
        #     return self._makeChordProfileTaperLE(foreX, chord, thickness, height, l1)
        # elif crossSection == FIN_CROSS_TAPER_TE:
        #     return self._makeChordProfileTaperTE(foreX, chord, thickness, height, l1)
        # elif crossSection == FIN_CROSS_TAPER_LETE:
        #     return self._makeChordProfileTaperLETE(foreX, chord, thickness, height, l1, l2, midChordLimit)

        return None

    def _makeFilletProfiles(self):
        profiles = []
        profiles.append(self._makeFilletRootProfile())
        profiles.append(self._makeFilletTipProfile())
        return profiles
