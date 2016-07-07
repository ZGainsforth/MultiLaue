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
        MultiLaueMainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MultiLaueMainWindow)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MultiLaueMainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MultiLaueMainWindow)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MultiLaueMainWindow.setStatusBar(self.statusBar)
        self.action_Import_Scan = QtGui.QAction(MultiLaueMainWindow)
        self.action_Import_Scan.setObjectName(_fromUtf8("action_Import_Scan"))
        self.action_Open_Scan = QtGui.QAction(MultiLaueMainWindow)
        self.action_Open_Scan.setObjectName(_fromUtf8("action_Open_Scan"))
        self.menu_File.addAction(self.action_Import_Scan)
        self.menu_File.addAction(self.action_Open_Scan)
        self.menuBar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MultiLaueMainWindow)
        QtCore.QMetaObject.connectSlotsByName(MultiLaueMainWindow)

    def retranslateUi(self, MultiLaueMainWindow):
        MultiLaueMainWindow.setWindowTitle(_translate("MultiLaueMainWindow", "MultiLaue", None))
        self.menu_File.setTitle(_translate("MultiLaueMainWindow", "&File", None))
        self.action_Import_Scan.setText(_translate("MultiLaueMainWindow", "&Import Scan", None))
        self.action_Open_Scan.setText(_translate("MultiLaueMainWindow", "&Open Scan", None))

