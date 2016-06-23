/********************************************************************************
** Form generated from reading UI file 'multilauemain.ui'
**
** Created by: Qt User Interface Compiler version 5.7.0
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_MULTILAUEMAIN_H
#define UI_MULTILAUEMAIN_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QToolBar>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MultiLaueMain
{
public:
    QMenuBar *menuBar;
    QToolBar *mainToolBar;
    QWidget *centralWidget;
    QStatusBar *statusBar;

    void setupUi(QMainWindow *MultiLaueMain)
    {
        if (MultiLaueMain->objectName().isEmpty())
            MultiLaueMain->setObjectName(QStringLiteral("MultiLaueMain"));
        MultiLaueMain->resize(400, 300);
        menuBar = new QMenuBar(MultiLaueMain);
        menuBar->setObjectName(QStringLiteral("menuBar"));
        MultiLaueMain->setMenuBar(menuBar);
        mainToolBar = new QToolBar(MultiLaueMain);
        mainToolBar->setObjectName(QStringLiteral("mainToolBar"));
        MultiLaueMain->addToolBar(mainToolBar);
        centralWidget = new QWidget(MultiLaueMain);
        centralWidget->setObjectName(QStringLiteral("centralWidget"));
        MultiLaueMain->setCentralWidget(centralWidget);
        statusBar = new QStatusBar(MultiLaueMain);
        statusBar->setObjectName(QStringLiteral("statusBar"));
        MultiLaueMain->setStatusBar(statusBar);

        retranslateUi(MultiLaueMain);

        QMetaObject::connectSlotsByName(MultiLaueMain);
    } // setupUi

    void retranslateUi(QMainWindow *MultiLaueMain)
    {
        MultiLaueMain->setWindowTitle(QApplication::translate("MultiLaueMain", "MultiLaueMain", 0));
    } // retranslateUi

};

namespace Ui {
    class MultiLaueMain: public Ui_MultiLaueMain {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_MULTILAUEMAIN_H
