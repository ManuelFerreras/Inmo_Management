# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 5.14.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import (QCoreApplication, QDate, QDateTime, QMetaObject,
    QObject, QPoint, QRect, QSize, QTime, QUrl, Qt)
from PySide2.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont,
    QFontDatabase, QIcon, QKeySequence, QLinearGradient, QPalette, QPainter,
    QPixmap, QRadialGradient)
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(211, 283)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.btn_extraer_info = QPushButton(self.centralwidget)
        self.btn_extraer_info.setObjectName(u"btn_extraer_info")
        self.btn_extraer_info.setEnabled(False)
        self.btn_extraer_info.setGeometry(QRect(10, 90, 191, 31))
        self.btn_funcionamiento = QPushButton(self.centralwidget)
        self.btn_funcionamiento.setObjectName(u"btn_funcionamiento")
        self.btn_funcionamiento.setGeometry(QRect(10, 190, 191, 31))
        self.btn_exit = QPushButton(self.centralwidget)
        self.btn_exit.setObjectName(u"btn_exit")
        self.btn_exit.setGeometry(QRect(10, 230, 191, 31))
        self.lineEdit = QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setEnabled(False)
        self.lineEdit.setGeometry(QRect(10, 130, 191, 31))
        self.btn_elegir_archivo_access = QPushButton(self.centralwidget)
        self.btn_elegir_archivo_access.setObjectName(u"btn_elegir_archivo_access")
        self.btn_elegir_archivo_access.setGeometry(QRect(10, 10, 191, 31))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Aguas", None))
        self.btn_extraer_info.setText(QCoreApplication.translate("MainWindow", u"Extraer Informacion de las Cuentas", None))
        self.btn_funcionamiento.setText(QCoreApplication.translate("MainWindow", u"\u00bfComo funciona el programa?", None))
        self.btn_exit.setText(QCoreApplication.translate("MainWindow", u"SALIR", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Periodo a Buscar", None))
        self.btn_elegir_archivo_access.setText(QCoreApplication.translate("MainWindow", u"Elegir Archivo Access", None))
    # retranslateUi

