#ifndef MULTILAUEMAINWINDOW_H
#define MULTILAUEMAINWINDOW_H

#include <QMainWindow>

namespace Ui {
class MultiLaueMainWindow;
}

class MultiLaueMainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MultiLaueMainWindow(QWidget *parent = 0);
    ~MultiLaueMainWindow();

private:
    Ui::MultiLaueMainWindow *ui;
};

#endif // MULTILAUEMAINWINDOW_H
