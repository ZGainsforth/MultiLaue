# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'aboutbox.ui'
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

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName(_fromUtf8("AboutDialog"))
        AboutDialog.resize(534, 356)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(534, 356))
        AboutDialog.setMaximumSize(QtCore.QSize(534, 356))
        self.pushOK = QtGui.QPushButton(AboutDialog)
        self.pushOK.setGeometry(QtCore.QRect(410, 320, 113, 32))
        self.pushOK.setObjectName(_fromUtf8("pushOK"))
        self.label = QtGui.QLabel(AboutDialog)
        self.label.setGeometry(QtCore.QRect(140, 10, 381, 301))
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.lblImage = QtGui.QLabel(AboutDialog)
        self.lblImage.setGeometry(QtCore.QRect(20, 140, 96, 96))
        self.lblImage.setObjectName(_fromUtf8("lblImage"))
        self.label_3 = QtGui.QLabel(AboutDialog)
        self.label_3.setGeometry(QtCore.QRect(0, 80, 141, 51))
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(AboutDialog)
        QtCore.QObject.connect(self.pushOK, QtCore.SIGNAL(_fromUtf8("clicked()")), AboutDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(_translate("AboutDialog", "Dialog", None))
        self.pushOK.setText(_translate("AboutDialog", "OK", None))
        self.label.setText(_translate("AboutDialog", "<html><head/><body><p align=\"center\">A software for monochromatic, Laue and MultiLaue X-ray diffraction datasets. Allows one to view, create topographs, and extract energies out of MultiLaue datasets.<br/><br/>Written in 2016 by Zack Gainsforth using funds from NASA. <br/><br/>The source code available on <a href=\"http://www.github.com/ZGainsforth/MultiLaue\"><span style=\" text-decoration: underline; color:#0000ff;\">GitHub</span></a>, via the <a href=\"https://github.com/ZGainsforth/MultiLaue/blob/master/LICENSE\"><span style=\" text-decoration: underline; color:#0000ff;\">Eclipse Public License</span></a>.<br/><br/>Feel free to give feedback and request improvements to <a href=\"mailto:xraysoftware@ssl.berkeley.edu\"><span style=\" text-decoration: underline; color:#0000ff;\">xraysoftware@ssl.berkeley.edu</span></a>.<br><br>MultiLaue makes use of freely available science tools and open source software.  Thank you to the <a href=\"https://www-als.lbl.gov\"><span style=\" text-decoration: underline; color:#0000ff;\">Advanced Light Source Synchrotron</span></a>,  <a href=\"http://henke.lbl.gov/optical_constants/\"><span style=\" text-decoration: underline; color:#0000ff;\">CXRO</span></a>, <a href=\"https://www.python.org\"><span style=\" text-decoration: underline; color:#0000ff;\">Python</span></a>, <a href=\"http://www.numpy.org\"><span style=\" text-decoration: underline; color:#0000ff;\">NumPy</span></a>, <a href=\"http://matplotlib.org\"><span style=\" text-decoration: underline; color:#0000ff;\">matplotlib</span></a>, <a href=\"https://ipython.org\"><span style=\" text-decoration: underline; color:#0000ff;\">iPython</span></a> and <a href=\"http://jupyter.org\"><span style=\" text-decoration: underline; color:#0000ff;\">Jupyter</span></a>, <a href=\"http://www.qt.io\"><span style=\" text-decoration: underline; color:#0000ff;\">Qt</span></a>, and <a href=\"http://icons8.com\"><span style=\" text-decoration: underline; color:#0000ff;\">Icons8</span></a>. </p></body></html>", None))
        self.lblImage.setText(_translate("AboutDialog", "<html><head/><body><p><img src=\"MultiLaueGui/Icons8/LaueIcon96x96.png\"></p></body></html>", None))
        self.label_3.setText(_translate("AboutDialog", "<p align=\"center\"><span style=\" font-size:24pt; font-weight:600;\">MultiLaue</span></p>", None))

