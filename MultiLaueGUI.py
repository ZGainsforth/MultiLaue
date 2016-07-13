# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'multilauemainwindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MultiLaueMainWindow(object):
    def setupUi(self, MultiLaueMainWindow):
        MultiLaueMainWindow.setObjectName(_fromUtf8("MultiLaueMainWindow"))
        MultiLaueMainWindow.resize(1100, 551)
        self.widgetMain = QtGui.QWidget(MultiLaueMainWindow)
        self.widgetMain.setObjectName(_fromUtf8("widgetMain"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.widgetMain)
        self.verticalLayout_2.setMargin(11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.frameImages = QtGui.QFrame(self.widgetMain)
        self.frameImages.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameImages.setFrameShadow(QtGui.QFrame.Raised)
        self.frameImages.setObjectName(_fromUtf8("frameImages"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frameImages)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.splitter = QtGui.QSplitter(self.frameImages)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.widgetSumImage = QtGui.QWidget(self.splitter)
        self.widgetSumImage.setObjectName(_fromUtf8("widgetSumImage"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.widgetSumImage)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.layoutSumImage = QtGui.QVBoxLayout()
        self.layoutSumImage.setMargin(11)
        self.layoutSumImage.setSpacing(6)
        self.layoutSumImage.setObjectName(_fromUtf8("layoutSumImage"))
        self.verticalLayout_3.addLayout(self.layoutSumImage)
        self.widgetTopograph = QtGui.QWidget(self.splitter)
        self.widgetTopograph.setObjectName(_fromUtf8("widgetTopograph"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.widgetTopograph)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setSpacing(6)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.layoutTopograph = QtGui.QVBoxLayout()
        self.layoutTopograph.setMargin(11)
        self.layoutTopograph.setSpacing(6)
        self.layoutTopograph.setObjectName(_fromUtf8("layoutTopograph"))
        self.verticalLayout_4.addLayout(self.layoutTopograph)
        self.widgetSingleImage = QtGui.QWidget(self.splitter)
        self.widgetSingleImage.setObjectName(_fromUtf8("widgetSingleImage"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.widgetSingleImage)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.layoutSingleImage = QtGui.QVBoxLayout()
        self.layoutSingleImage.setMargin(11)
        self.layoutSingleImage.setSpacing(6)
        self.layoutSingleImage.setObjectName(_fromUtf8("layoutSingleImage"))
        self.verticalLayout_5.addLayout(self.layoutSingleImage)
        self.horizontalLayout.addWidget(self.splitter)
        self.verticalLayout_2.addWidget(self.frameImages)
        self.frameControls = QtGui.QFrame(self.widgetMain)
        self.frameControls.setMaximumSize(QtCore.QSize(16777215, 150))
        self.frameControls.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frameControls.setFrameShadow(QtGui.QFrame.Raised)
        self.frameControls.setObjectName(_fromUtf8("frameControls"))
        self.verticalLayout_2.addWidget(self.frameControls)
        MultiLaueMainWindow.setCentralWidget(self.widgetMain)
        self.menuBar = QtGui.QMenuBar(MultiLaueMainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1100, 22))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menu_File = QtGui.QMenu(self.menuBar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menuHelp = QtGui.QMenu(self.menuBar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        MultiLaueMainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MultiLaueMainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MultiLaueMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MultiLaueMainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MultiLaueMainWindow.setStatusBar(self.statusBar)
        self.action_Import_Scan = QtGui.QAction(MultiLaueMainWindow)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Import")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Import_Scan.setIcon(icon)
        self.action_Import_Scan.setObjectName(_fromUtf8("action_Import_Scan"))
        self.action_Open_Scan = QtGui.QAction(MultiLaueMainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Open")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open_Scan.setIcon(icon1)
        self.action_Open_Scan.setObjectName(_fromUtf8("action_Open_Scan"))
        self.actionProcess_MultiLaue = QtGui.QAction(MultiLaueMainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Compute")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionProcess_MultiLaue.setIcon(icon2)
        self.actionProcess_MultiLaue.setObjectName(_fromUtf8("actionProcess_MultiLaue"))
        self.actionSave_Aggregate_Image = QtGui.QAction(MultiLaueMainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Save Aggregate")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_Aggregate_Image.setIcon(icon3)
        self.actionSave_Aggregate_Image.setObjectName(_fromUtf8("actionSave_Aggregate_Image"))
        self.actionSave_Topograph_Image = QtGui.QAction(MultiLaueMainWindow)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Save Topograph")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_Topograph_Image.setIcon(icon4)
        self.actionSave_Topograph_Image.setObjectName(_fromUtf8("actionSave_Topograph_Image"))
        self.actionSave_Single_Image = QtGui.QAction(MultiLaueMainWindow)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Save Single")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_Single_Image.setIcon(icon5)
        self.actionSave_Single_Image.setObjectName(_fromUtf8("actionSave_Single_Image"))
        self.actionSave_All_Three_Images = QtGui.QAction(MultiLaueMainWindow)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/Icons/Save")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_All_Three_Images.setIcon(icon6)
        self.actionSave_All_Three_Images.setObjectName(_fromUtf8("actionSave_All_Three_Images"))
        self.actionClose = QtGui.QAction(MultiLaueMainWindow)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionOpen_GitHub_Website = QtGui.QAction(MultiLaueMainWindow)
        self.actionOpen_GitHub_Website.setObjectName(_fromUtf8("actionOpen_GitHub_Website"))
        self.actionAbout_MultiLaue = QtGui.QAction(MultiLaueMainWindow)
        self.actionAbout_MultiLaue.setIconVisibleInMenu(True)
        self.actionAbout_MultiLaue.setObjectName(_fromUtf8("actionAbout_MultiLaue"))
        self.menu_File.addAction(self.action_Open_Scan)
        self.menu_File.addAction(self.actionSave_Aggregate_Image)
        self.menu_File.addAction(self.actionSave_Topograph_Image)
        self.menu_File.addAction(self.actionSave_Single_Image)
        self.menu_File.addAction(self.actionSave_All_Three_Images)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Import_Scan)
        self.menu_File.addAction(self.actionProcess_MultiLaue)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionClose)
        self.menuHelp.addAction(self.actionAbout_MultiLaue)
        self.menuHelp.addAction(self.actionOpen_GitHub_Website)
        self.menuBar.addAction(self.menu_File.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.mainToolBar.addAction(self.action_Open_Scan)
        self.mainToolBar.addAction(self.actionSave_Aggregate_Image)
        self.mainToolBar.addAction(self.actionSave_Topograph_Image)
        self.mainToolBar.addAction(self.actionSave_Single_Image)
        self.mainToolBar.addAction(self.actionSave_All_Three_Images)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.action_Import_Scan)
        self.mainToolBar.addAction(self.actionProcess_MultiLaue)

        self.retranslateUi(MultiLaueMainWindow)
        QtCore.QMetaObject.connectSlotsByName(MultiLaueMainWindow)

    def retranslateUi(self, MultiLaueMainWindow):
        MultiLaueMainWindow.setWindowTitle(_translate("MultiLaueMainWindow", "MultiLaue", None))
        self.menu_File.setTitle(_translate("MultiLaueMainWindow", "&File", None))
        self.menuHelp.setTitle(_translate("MultiLaueMainWindow", "Help", None))
        self.action_Import_Scan.setText(_translate("MultiLaueMainWindow", "&Import Scan", None))
        self.action_Open_Scan.setText(_translate("MultiLaueMainWindow", "&Open Scan", None))
        self.actionProcess_MultiLaue.setText(_translate("MultiLaueMainWindow", "Process &MultiLaue", None))
        self.actionSave_Aggregate_Image.setText(_translate("MultiLaueMainWindow", "Save Aggregate Image", None))
        self.actionSave_Topograph_Image.setText(_translate("MultiLaueMainWindow", "Save Topograph Image", None))
        self.actionSave_Topograph_Image.setToolTip(_translate("MultiLaueMainWindow", "Save Topograph Image", None))
        self.actionSave_Single_Image.setText(_translate("MultiLaueMainWindow", "Save Single Image", None))
        self.actionSave_All_Three_Images.setText(_translate("MultiLaueMainWindow", "Save All Three Images", None))
        self.actionClose.setText(_translate("MultiLaueMainWindow", "Close Scan", None))
        self.actionOpen_GitHub_Website.setText(_translate("MultiLaueMainWindow", "Open GitHub Website", None))
        self.actionAbout_MultiLaue.setText(_translate("MultiLaueMainWindow", "About MultiLaue", None))

import icons_rc
