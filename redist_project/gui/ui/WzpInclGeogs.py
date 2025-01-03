# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/stuart/Source/redist_project/ui/WzpInclGeogs.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_wzpIncludeGeography(object):
    def setupUi(self, wzpIncludeGeography):
        wzpIncludeGeography.setObjectName("wzpIncludeGeography")
        wzpIncludeGeography.resize(400, 303)
        self.verticalLayout = QtWidgets.QVBoxLayout(wzpIncludeGeography)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gbxGeogLayers = QtWidgets.QGroupBox(wzpIncludeGeography)
        self.gbxGeogLayers.setObjectName("gbxGeogLayers")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.gbxGeogLayers)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.cbCounty = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbCounty.setChecked(True)
        self.cbCounty.setObjectName("cbCounty")
        self.verticalLayout_3.addWidget(self.cbCounty)
        self.cbVTD = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbVTD.setChecked(True)
        self.cbVTD.setObjectName("cbVTD")
        self.verticalLayout_3.addWidget(self.cbVTD)
        self.cbPlace = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbPlace.setChecked(True)
        self.cbPlace.setObjectName("cbPlace")
        self.verticalLayout_3.addWidget(self.cbPlace)
        self.cbAIANNH = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbAIANNH.setObjectName("cbAIANNH")
        self.verticalLayout_3.addWidget(self.cbAIANNH)
        self.cbCousub = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbCousub.setObjectName("cbCousub")
        self.verticalLayout_3.addWidget(self.cbCousub)
        self.cbConcity = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbConcity.setObjectName("cbConcity")
        self.verticalLayout_3.addWidget(self.cbConcity)
        self.cbBlkGrp = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbBlkGrp.setObjectName("cbBlkGrp")
        self.verticalLayout_3.addWidget(self.cbBlkGrp)
        self.cbTract = QtWidgets.QCheckBox(self.gbxGeogLayers)
        self.cbTract.setObjectName("cbTract")
        self.verticalLayout_3.addWidget(self.cbTract)
        self.verticalLayout.addWidget(self.gbxGeogLayers)
        self.gbxBaseMap = QtWidgets.QGroupBox(wzpIncludeGeography)
        self.gbxBaseMap.setObjectName("gbxBaseMap")
        self.gridLayout = QtWidgets.QGridLayout(self.gbxBaseMap)
        self.gridLayout.setObjectName("gridLayout")
        self.cbCustomLayers = QtWidgets.QCheckBox(self.gbxBaseMap)
        self.cbCustomLayers.setObjectName("cbCustomLayers")
        self.gridLayout.addWidget(self.cbCustomLayers, 0, 0, 1, 1)
        self.cbBaseMap = QtWidgets.QCheckBox(self.gbxBaseMap)
        self.cbBaseMap.setObjectName("cbBaseMap")
        self.gridLayout.addWidget(self.cbBaseMap, 1, 0, 1, 1)
        self.cmbBaseMap = QtWidgets.QComboBox(self.gbxBaseMap)
        self.cmbBaseMap.setObjectName("cmbBaseMap")
        self.gridLayout.addWidget(self.cmbBaseMap, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.gbxBaseMap)

        self.retranslateUi(wzpIncludeGeography)
        QtCore.QMetaObject.connectSlotsByName(wzpIncludeGeography)

    def retranslateUi(self, wzpIncludeGeography):
        _translate = QtCore.QCoreApplication.translate
        wzpIncludeGeography.setWindowTitle(_translate("wzpIncludeGeography", "WizardPage"))
        wzpIncludeGeography.setTitle(_translate("wzpIncludeGeography", "Geography Layers and Base Map"))
        self.gbxGeogLayers.setTitle(_translate("wzpIncludeGeography", "Geography Layers"))
        self.cbCounty.setText(_translate("wzpIncludeGeography", "County/Parish"))
        self.cbVTD.setText(_translate("wzpIncludeGeography", "VTDs"))
        self.cbPlace.setText(_translate("wzpIncludeGeography", "Census Places"))
        self.cbAIANNH.setText(_translate("wzpIncludeGeography", "American Indian/Alaska Native/Native Hawaiian Areas"))
        self.cbCousub.setText(_translate("wzpIncludeGeography", "County Subdivisions"))
        self.cbConcity.setText(_translate("wzpIncludeGeography", "Consolidated Cities"))
        self.cbBlkGrp.setText(_translate("wzpIncludeGeography", "Block Groups"))
        self.cbTract.setText(_translate("wzpIncludeGeography", "Census Tracts"))
        self.gbxBaseMap.setTitle(_translate("wzpIncludeGeography", "Other Layers"))
        self.cbCustomLayers.setText(_translate("wzpIncludeGeography", "Include Custom Layers"))
        self.cbBaseMap.setToolTip(_translate("wzpIncludeGeography", "Add a vector tile base map from MapTiler or HCMGIS plugin"))
        self.cbBaseMap.setText(_translate("wzpIncludeGeography", "Include Base-map"))
        self.cmbBaseMap.setPlaceholderText(_translate("wzpIncludeGeography", "Select base map provider..."))
