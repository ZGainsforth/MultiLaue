#include "MultiLaueGUI.h"
#include "ui_multilauemain.h"

MultiLaueGUI::MultiLaueGUI(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MultiLaueMain)
{
    ui->setupUi(this);
}

MultiLaueGUI::~MultiLaueGUI()
{
    delete ui;
}
