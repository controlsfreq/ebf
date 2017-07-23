#include "edbconfig.h"
#include "ui_edbconfig.h"

EdbConfig::EdbConfig(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::EdbConfig)
{
    ui->setupUi(this);
}

EdbConfig::~EdbConfig()
{
    delete ui;
}
