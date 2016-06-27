#ifndef MULTILAUEMAIN_H
#define MULTILAUEMAIN_H

#include <QMainWindow>

namespace Ui {
class MultiLaueMain;
}

class MultiLaueGUI : public QMainWindow
{
    Q_OBJECT

public:
    explicit MultiLaueGUI(QWidget *parent = 0);
    ~MultiLaueGUI();

private:
    Ui::MultiLaueMain *ui;
};

#endif // MULTILAUEMAIN_H
