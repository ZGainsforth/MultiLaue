# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MultiLaueGUI.ui'
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

class Ui_MultiLaueGUI(object):
    def setupUi(self, MultiLaueGUI):
        MultiLaueGUI.setObjectName(_fromUtf8("MultiLaueGUI"))
        MultiLaueGUI.resize(903, 482)
        self.centralWidget = QtGui.QWidget(MultiLaueGUI)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setMargin(11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.centralWidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.MacroImageFrame = QtGui.QFrame(self.splitter)
        self.MacroImageFrame.setMinimumSize(QtCore.QSize(256, 256))
        self.MacroImageFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MacroImageFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MacroImageFrame.setObjectName(_fromUtf8("MacroImageFrame"))
        self.MiddleFrame = QtGui.QFrame(self.splitter)
        self.MiddleFrame.setMinimumSize(QtCore.QSize(128, 128))
        self.MiddleFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MiddleFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MiddleFrame.setObjectName(_fromUtf8("MiddleFrame"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.MiddleFrame)
        self.verticalLayout_2.setMargin(11)
        self.verticalLayout_2.setSpacing(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.MacroZoominFrame = QtGui.QFrame(self.MiddleFrame)
        self.MacroZoominFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MacroZoominFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MacroZoominFrame.setObjectName(_fromUtf8("MacroZoominFrame"))
        self.verticalLayout_2.addWidget(self.MacroZoominFrame)
        self.Topograph = QtGui.QFrame(self.MiddleFrame)
        self.Topograph.setFrameShape(QtGui.QFrame.StyledPanel)
        self.Topograph.setFrameShadow(QtGui.QFrame.Raised)
        self.Topograph.setObjectName(_fromUtf8("Topograph"))
        self.verticalLayout_2.addWidget(self.Topograph)
        self.MicroZoominFrame = QtGui.QFrame(self.MiddleFrame)
        self.MicroZoominFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MicroZoominFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MicroZoominFrame.setObjectName(_fromUtf8("MicroZoominFrame"))
        self.verticalLayout_2.addWidget(self.MicroZoominFrame)
        self.MicroImageFrame = QtGui.QFrame(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MicroImageFrame.sizePolicy().hasHeightForWidth())
        self.MicroImageFrame.setSizePolicy(sizePolicy)
        self.MicroImageFrame.setMinimumSize(QtCore.QSize(256, 256))
        self.MicroImageFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.MicroImageFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.MicroImageFrame.setObjectName(_fromUtf8("MicroImageFrame"))
        self.verticalLayout.addWidget(self.splitter)
        MultiLaueGUI.setCentralWidget(self.centralWidget)
        self.menuBar = QtGui.QMenuBar(MultiLaueGUI)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 903, 22))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menu_File = QtGui.QMenu(self.menuBar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        MultiLaueGUI.setMenuBar(self.menuBar)
        self.mainToolBar = QtGui.QToolBar(MultiLaueGUI)
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        MultiLaueGUI.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtGui.QStatusBar(MultiLaueGUI)
        self.statusBar.setObjectName(_fromUtf8("statusBar"))
        MultiLaueGUI.setStatusBar(self.statusBar)
        self.action_Open = QtGui.QAction(MultiLaueGUI)
        self.action_Open.setObjectName(_fromUtf8("action_Open"))
        self.action_Quit = QtGui.QAction(MultiLaueGUI)
        self.action_Quit.setObjectName(_fromUtf8("action_Quit"))
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.action_Quit)
        self.menuBar.addAction(self.menu_File.menuAction())

        self.retranslateUi(MultiLaueGUI)
        QtCore.QMetaObject.connectSlotsByName(MultiLaueGUI)

    def retranslateUi(self, MultiLaueGUI):
        MultiLaueGUI.setWindowTitle(_translate("MultiLaueGUI", "MultiLaueMain", None))
        self.menu_File.setTitle(_translate("MultiLaueGUI", "&File", None))
        self.action_Open.setText(_translate("MultiLaueGUI", "&Open ...", None))
        self.action_Quit.setText(_translate("MultiLaueGUI", "&Quit", None))

