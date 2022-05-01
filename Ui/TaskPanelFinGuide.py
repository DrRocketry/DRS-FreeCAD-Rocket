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
"""Class for drawing fin guides"""

__title__ = "FreeCAD Fin Guides"
__author__ = "David Carter"
__url__ = "https://www.davesrocketshop.com"
    

import FreeCAD
import FreeCADGui

from PySide import QtGui, QtCore
from PySide2.QtWidgets import QDialog, QGridLayout, QVBoxLayout, QSizePolicy

from DraftTools import translate

from App.Utilities import _toFloat, _valueWithUnits

class _FinGuideDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # define our window
        self.setGeometry(250, 250, 400, 350)
        self.setWindowTitle(translate('Rocket', "Fin Guide Parameter"))

        ui = FreeCADGui.UiLoader()

        # Get the fin guide  parameters
        self.diameterLabel = QtGui.QLabel(translate('Rocket', "Diameter"), self)

        self.diameterInput = ui.createWidget("Gui::InputField")
        self.diameterInput.unit = 'mm'
        self.diameterInput.setFixedWidth(80)

        self.rootThicknessLabel = QtGui.QLabel(translate('Rocket', "Root Thickness"), self)

        self.rootThicknessInput = ui.createWidget("Gui::InputField")
        self.rootThicknessInput.unit = 'mm'
        self.rootThicknessInput.setFixedWidth(80)

        self.tipThicknessLabel = QtGui.QLabel(translate('Rocket', "Tip Thickness"), self)

        self.tipThicknessInput = ui.createWidget("Gui::InputField")
        self.tipThicknessInput.unit = 'mm'
        self.tipThicknessInput.setFixedWidth(80)

        self.spanLabel = QtGui.QLabel(translate('Rocket', "Span"), self)

        self.spanInput = ui.createWidget("Gui::InputField")
        self.spanInput.unit = 'mm'
        self.spanInput.setFixedWidth(80)

        self.finCountLabel = QtGui.QLabel(translate('Rocket', "Fin Count"), self)

        self.finCountSpinBox = QtGui.QSpinBox(self)
        self.finCountSpinBox.setFixedWidth(100)
        self.finCountSpinBox.setMinimum(1)
        self.finCountSpinBox.setMaximum(10000)

        self.glueRadiusLabel = QtGui.QLabel(translate('Rocket', "Glue Radius"), self)

        self.glueRadiusInput = ui.createWidget("Gui::InputField")
        self.glueRadiusInput.unit = 'mm'
        self.glueRadiusInput.setFixedWidth(80)

        self.lengthLabel = QtGui.QLabel(translate('Rocket', "Length"), self)

        self.lengthInput = ui.createWidget("Gui::InputField")
        self.lengthInput.unit = 'mm'
        self.lengthInput.setFixedWidth(80)
        
        self.thicknessLabel = QtGui.QLabel(translate('Rocket', "Thickness"), self)

        self.thicknessInput = ui.createWidget("Gui::InputField")
        self.thicknessInput.unit = 'mm'
        self.thicknessInput.setFixedWidth(80)

        layout = QGridLayout()
        row = 0

        layout.addWidget(self.diameterLabel, row, 0, 1, 2)
        layout.addWidget(self.diameterInput, row, 1)
        row += 1

        layout.addWidget(self.rootThicknessLabel, row, 0)
        layout.addWidget(self.rootThicknessInput, row, 1)
        row += 1

        layout.addWidget(self.tipThicknessLabel, row, 0)
        layout.addWidget(self.tipThicknessInput, row, 1)
        row += 1

        layout.addWidget(self.spanLabel, row, 0)
        layout.addWidget(self.spanInput, row, 1)
        row += 1

        layout.addWidget(self.finCountLabel, row, 0)
        layout.addWidget(self.finCountSpinBox, row, 1)
        row += 1

        layout.addWidget(self.glueRadiusLabel, row, 0)
        layout.addWidget(self.glueRadiusInput, row, 1)
        row += 1

        layout.addWidget(self.lengthLabel, row, 0)
        layout.addWidget(self.lengthInput, row, 1)
        row += 1

        layout.addWidget(self.thicknessLabel, row, 0)
        layout.addWidget(self.thicknessInput, row, 1)
        # row += 1

        layout.addItem(QtGui.QSpacerItem(0,0, QSizePolicy.Expanding, QSizePolicy.Expanding))

        self.setLayout(layout)

class TaskPanelFinGuide:

    def __init__(self,obj,mode):
        self._obj = obj
        
        self._finGuideForm = _FinGuideDialog()

        self.form = [self._finGuideForm]
        self._finGuideForm.setWindowIcon(QtGui.QIcon(FreeCAD.getUserAppDataDir() + "Mod/Rocket/Resources/icons/Rocket_FinGuide.svg"))

        self._finGuideForm.diameterInput.textEdited.connect(self.onDiameter)
        self._finGuideForm.rootThicknessInput.textEdited.connect(self.onRootThickness)
        self._finGuideForm.tipThicknessInput.textEdited.connect(self.onTipThickness)
        self._finGuideForm.spanInput.textEdited.connect(self.onSpan)
        self._finGuideForm.finCountSpinBox.valueChanged.connect(self.onFinCount)
        self._finGuideForm.glueRadiusInput.textEdited.connect(self.onGlueRadius)

        self._finGuideForm.lengthInput.textEdited.connect(self.onLength)
        self._finGuideForm.thicknessInput.textEdited.connect(self.onThickness)
        
        self.update()
        
        if mode == 0: # fresh created
            self._obj.Proxy.execute(self._obj)  # calculate once 
            FreeCAD.Gui.SendMsgToActiveView("ViewFit")
        
    def transferTo(self):
        "Transfer from the dialog to the object" 
        self._obj.Diameter = self._finGuideForm.diameterInput.text()
        self._obj.RootThickness = self._finGuideForm.rootThicknessInput.text()
        self._obj.TipThickness = self._finGuideForm.tipThicknessInput.text()
        self._obj.Span = self._finGuideForm.spanInput.text()
        self._obj.FinCount = self._finGuideForm.finCountSpinBox.value()
        self._obj.GlueRadius = self._finGuideForm.glueRadiusInput.text()
        self._obj.Length = self._finGuideForm.lengthInput.text()
        self._obj.Thickness = self._finGuideForm.thicknessInput.text()

    def transferFrom(self):
        "Transfer from the object to the dialog"
        self._finGuideForm.diameterInput.setText(self._obj.Diameter.UserString)
        self._finGuideForm.rootThicknessInput.setText(self._obj.RootThickness.UserString)
        self._finGuideForm.tipThicknessInput.setText(self._obj.TipThickness.UserString)
        self._finGuideForm.spanInput.setText(self._obj.Span.UserString)
        self._finGuideForm.finCountSpinBox.setValue(self._obj.FinCount)
        self._finGuideForm.glueRadiusInput.setText(self._obj.GlueRadius.UserString)
        self._finGuideForm.lengthInput.setText(self._obj.Length.UserString)
        self._finGuideForm.thicknessInput.setText(self._obj.Thickness.UserString)
        
    def onDiameter(self, value):
        try:
            self._obj.Diameter = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onRootThickness(self, value):
        try:
            self._obj.RootThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onTipThickness(self, value):
        try:
            self._obj.TipThickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onSpan(self, value):
        try:
            self._obj.Span = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onFinCount(self, value):
        self._obj.HoleCount = int(value)
        self._obj.Proxy.execute(self._obj)
        
    def onGlueRadius(self, value):
        try:
            self._obj.GlueRadius = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onLength(self, value):
        try:
            self._obj.Length = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
        
    def onThickness(self, value):
        try:
            self._obj.Thickness = FreeCAD.Units.Quantity(value).Value
            self._obj.Proxy.execute(self._obj)
        except ValueError:
            pass
       
    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok) | int(QtGui.QDialogButtonBox.Cancel)| int(QtGui.QDialogButtonBox.Apply)

    def clicked(self,button):
        if button == QtGui.QDialogButtonBox.Apply:
            self.transferTo()
            self._obj.Proxy.execute(self._obj) 
        
    def update(self):
        'fills the widgets'
        self.transferFrom()
                
    def accept(self):
        self.transferTo()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
        
                    
    def reject(self):
        FreeCAD.ActiveDocument.abortTransaction()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.ActiveDocument.resetEdit()
