#include "multilauemainwindow.h"
#include "ui_multilauemainwindow.h"

MultiLaueMainWindow::MultiLaueMainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MultiLaueMainWindow)
{
    ui->setupUi(this);
}

MultiLaueMainWindow::~MultiLaueMainWindow()
{
    delete ui;
}
