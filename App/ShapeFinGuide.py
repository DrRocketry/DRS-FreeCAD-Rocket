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
"""Class for fin guides"""

__title__ = "FreeCAD Fin Guides"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    
from App.ShapeComponent import ShapeComponent

from App.FinGuideShapeHandler import FinGuideShapeHandler

from DraftTools import translate

class ShapeFinGuide(ShapeComponent):

    def __init__(self, obj):
        super().__init__(obj)

        if not hasattr(obj,"Diameter"):
            obj.addProperty('App::PropertyLength', 'Diameter', 'FinGuide', translate('App::Property', 'Outer diameter of the body tube')).Diameter = 25.0
        if not hasattr(obj,"RootThickness"):
            obj.addProperty('App::PropertyLength', 'RootThickness', 'FinGuide', translate('App::Property', 'Thickness of the fin at the root')).RootThickness = 3.0
        if not hasattr(obj,"TipThickness"):
            obj.addProperty('App::PropertyLength', 'TipThickness', 'FinGuide', translate('App::Property', 'Thickness of the fin at the tip')).TipThickness = 3.0
        if not hasattr(obj,"Span"):
            obj.addProperty('App::PropertyLength', 'Span', 'FinGuide', translate('App::Property', 'Fin length from the root to the tip')).Span = 100.0
        if not hasattr(obj,"FinCount"):
            obj.addProperty('App::PropertyInteger', 'FinCount', 'FinCount', translate('App::Property', 'The number of equally spaced fins')).FinCount = 4

        if not hasattr(obj,"GlueRadius"):
            obj.addProperty('App::PropertyLength', 'GlueRadius', 'FinGuide', translate('App::Property', 'Radius of the cutout along the fillet of the fin')).GlueRadius = 5.0

        if not hasattr(obj,"Length"):
            obj.addProperty('App::PropertyLength', 'Length', 'FinGuide', translate('App::Property', 'Length of the fin guide along the body tube')).Length = 2.0
        if not hasattr(obj,"Thickness"):
            obj.addProperty('App::PropertyLength', 'Thickness', 'FinGuide', translate('App::Property', 'Thickness of the fin guide')).Thickness = 2.0

        if not hasattr(obj,"Shape"):
            obj.addProperty('Part::PropertyPartShape', 'Shape', 'FinGuide', translate('App::Property', 'Shape of the fin guide'))

    def execute(self, obj):
        shape = FinGuideShapeHandler(obj)
        if shape is not None:
            shape.draw()
