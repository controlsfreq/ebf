#ifndef EDBCONFIG_H
#define EDBCONFIG_H

#include <QWidget>

namespace Ui {
class EdbConfig;
}

class EdbConfig : public QWidget
{
    Q_OBJECT

public:
    explicit EdbConfig(QWidget *parent = 0);
    ~EdbConfig();

private:
    Ui::EdbConfig *ui;
};

#endif // EDBCONFIG_H
