#include "multilauemainwindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    MultiLaueMainWindow w;
    w.show();

    return a.exec();
}
