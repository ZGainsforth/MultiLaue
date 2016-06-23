#ifndef MULTILAUEMAIN_H
#define MULTILAUEMAIN_H

#include <QMainWindow>

namespace Ui {
class MultiLaueMain;
}

class MultiLaueMain : public QMainWindow
{
    Q_OBJECT

public:
    explicit MultiLaueMain(QWidget *parent = 0);
    ~MultiLaueMain();

private:
    Ui::MultiLaueMain *ui;
};

#endif // MULTILAUEMAIN_H
