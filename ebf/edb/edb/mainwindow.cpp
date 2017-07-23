#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "edbconfig.h"

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow),
    edbConfigWindow(new Ui::EdbConfig)
{
    ui->setupUi(this);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::on_actionConfigure_triggered()
{
    edbConfigWindow->setupUi(this);
}
