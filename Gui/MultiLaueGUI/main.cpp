#include "MultiLaueGUI.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MultiLaueGUI w;
    w.show();

    return a.exec();
}
