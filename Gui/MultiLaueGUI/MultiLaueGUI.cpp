#include "multilauemain.h"
#include "ui_multilauemain.h"

MultiLaueMain::MultiLaueMain(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MultiLaueMain)
{
    ui->setupUi(this);
}

MultiLaueMain::~MultiLaueMain()
{
    delete ui;
}
