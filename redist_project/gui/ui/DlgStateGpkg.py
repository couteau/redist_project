# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/stuart/Source/redist_project/ui/DlgStateGpkg.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlgDownloadStateGpkg(object):
    def setupUi(self, dlgDownloadStateGpkg):
        dlgDownloadStateGpkg.setObjectName("dlgDownloadStateGpkg")
        dlgDownloadStateGpkg.resize(476, 294)
        self.gridLayout = QtWidgets.QGridLayout(dlgDownloadStateGpkg)
        self.gridLayout.setObjectName("gridLayout")
        self.cbIncludeCVAP = QtWidgets.QCheckBox(dlgDownloadStateGpkg)
        self.cbIncludeCVAP.setEnabled(False)
        self.cbIncludeCVAP.setObjectName("cbIncludeCVAP")
        self.gridLayout.addWidget(self.cbIncludeCVAP, 4, 0, 1, 1)
        self.rbStandardPackage = QtWidgets.QRadioButton(dlgDownloadStateGpkg)
        self.rbStandardPackage.setChecked(True)
        self.rbStandardPackage.setObjectName("rbStandardPackage")
        self.gridLayout.addWidget(self.rbStandardPackage, 2, 0, 1, 2)
        self.cmCVAPYear = QtWidgets.QComboBox(dlgDownloadStateGpkg)
        self.cmCVAPYear.setEnabled(False)
        self.cmCVAPYear.setObjectName("cmCVAPYear")
        self.gridLayout.addWidget(self.cmCVAPYear, 4, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(dlgDownloadStateGpkg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)
        self.fwL2VRData = QgsFileWidget(dlgDownloadStateGpkg)
        self.fwL2VRData.setEnabled(False)
        self.fwL2VRData.setObjectName("fwL2VRData")
        self.gridLayout.addWidget(self.fwL2VRData, 5, 1, 1, 1)
        self.cbIncludeVoterReg = QtWidgets.QCheckBox(dlgDownloadStateGpkg)
        self.cbIncludeVoterReg.setEnabled(False)
        self.cbIncludeVoterReg.setObjectName("cbIncludeVoterReg")
        self.gridLayout.addWidget(self.cbIncludeVoterReg, 5, 0, 1, 1)
        self.cmDecennialYear = QtWidgets.QComboBox(dlgDownloadStateGpkg)
        self.cmDecennialYear.setObjectName("cmDecennialYear")
        self.cmDecennialYear.addItem("")
        self.cmDecennialYear.addItem("")
        self.gridLayout.addWidget(self.cmDecennialYear, 1, 1, 1, 1)
        self.lbDecennialYear = QtWidgets.QLabel(dlgDownloadStateGpkg)
        self.lbDecennialYear.setObjectName("lbDecennialYear")
        self.gridLayout.addWidget(self.lbDecennialYear, 1, 0, 1, 1)
        self.lbIntro = QtWidgets.QLabel(dlgDownloadStateGpkg)
        self.lbIntro.setWordWrap(True)
        self.lbIntro.setObjectName("lbIntro")
        self.gridLayout.addWidget(self.lbIntro, 0, 0, 1, 2)
        self.rbCustomPackage = QtWidgets.QRadioButton(dlgDownloadStateGpkg)
        self.rbCustomPackage.setObjectName("rbCustomPackage")
        self.gridLayout.addWidget(self.rbCustomPackage, 3, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 2)
        self.lbDecennialYear.setBuddy(self.cmDecennialYear)

        self.retranslateUi(dlgDownloadStateGpkg)
        self.cmDecennialYear.setCurrentIndex(1)
        self.buttonBox.accepted.connect(dlgDownloadStateGpkg.accept) # type: ignore
        self.buttonBox.rejected.connect(dlgDownloadStateGpkg.reject) # type: ignore
        self.rbCustomPackage.toggled['bool'].connect(self.cbIncludeCVAP.setEnabled) # type: ignore
        self.rbCustomPackage.toggled['bool'].connect(self.cbIncludeVoterReg.setEnabled) # type: ignore
        self.rbCustomPackage.toggled['bool'].connect(self.cmCVAPYear.setEnabled) # type: ignore
        self.rbCustomPackage.toggled['bool'].connect(self.fwL2VRData.setEnabled) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(dlgDownloadStateGpkg)
        dlgDownloadStateGpkg.setTabOrder(self.cmDecennialYear, self.rbStandardPackage)
        dlgDownloadStateGpkg.setTabOrder(self.rbStandardPackage, self.rbCustomPackage)
        dlgDownloadStateGpkg.setTabOrder(self.rbCustomPackage, self.cbIncludeCVAP)
        dlgDownloadStateGpkg.setTabOrder(self.cbIncludeCVAP, self.cmCVAPYear)
        dlgDownloadStateGpkg.setTabOrder(self.cmCVAPYear, self.cbIncludeVoterReg)

    def retranslateUi(self, dlgDownloadStateGpkg):
        _translate = QtCore.QCoreApplication.translate
        dlgDownloadStateGpkg.setWindowTitle(_translate("dlgDownloadStateGpkg", "Redistricting Data Package"))
        self.cbIncludeCVAP.setToolTip(_translate("dlgDownloadStateGpkg", "<html><head/><body><p>QGIS Redistricting Plugin can include Citizen Voting Age Population data from the US Census Bureau in the redistricting data package. Please select the 5-Year ACS year for the CVAP data you would like to include.</p></body></html>"))
        self.cbIncludeCVAP.setText(_translate("dlgDownloadStateGpkg", "Include CVAP data"))
        self.rbStandardPackage.setText(_translate("dlgDownloadStateGpkg", "Download redistricting data package for {state}"))
        self.fwL2VRData.setToolTip(_translate("dlgDownloadStateGpkg", "<html><head/><body><p>Select the block-level L2 Voter Registration csv file downloaded from Redistricting Data Hub</p></body></html>"))
        self.fwL2VRData.setDialogTitle(_translate("dlgDownloadStateGpkg", "L2 Voter Registration Data"))
        self.fwL2VRData.setFilter(_translate("dlgDownloadStateGpkg", "*.csv"))
        self.cbIncludeVoterReg.setToolTip(_translate("dlgDownloadStateGpkg", "<html><head/><body><p>QGIS Redistricting Plugin can add voter registration data in the redistricting data package. To include voter registration data,  you must obtain a L2 block-level voter registration package provided by Redistricting Data Hub. </p></body></html>"))
        self.cbIncludeVoterReg.setText(_translate("dlgDownloadStateGpkg", "Include L2 Voter Registration \n"
"Data from RDH"))
        self.cmDecennialYear.setItemText(0, _translate("dlgDownloadStateGpkg", "2010"))
        self.cmDecennialYear.setItemText(1, _translate("dlgDownloadStateGpkg", "2020"))
        self.lbDecennialYear.setText(_translate("dlgDownloadStateGpkg", "Decennial Census"))
        self.lbIntro.setText(_translate("dlgDownloadStateGpkg", "<html><head/><body><p>To create a redistricting plan for {state}, you must install a redistricting data package. Prepackaged redistricting data is available for download or you may create a custom package.</p></body></html>"))
        self.rbCustomPackage.setText(_translate("dlgDownloadStateGpkg", "Create a custom redistricting data package for {state}"))
from qgsfilewidget import QgsFileWidget
