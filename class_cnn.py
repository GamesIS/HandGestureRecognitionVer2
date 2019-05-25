# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'class_cnn.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_class_cnn_form(object):
    def setupUi(self, class_cnn_form):
        class_cnn_form.setObjectName("class_cnn_form")
        class_cnn_form.resize(368, 388)
        self.gestures_cb = QtWidgets.QComboBox(class_cnn_form)
        self.gestures_cb.setGeometry(QtCore.QRect(230, 10, 131, 22))
        self.gestures_cb.setObjectName("gestures_cb")
        self.start_training = QtWidgets.QPushButton(class_cnn_form)
        self.start_training.setGeometry(QtCore.QRect(10, 50, 151, 41))
        self.start_training.setObjectName("start_training")
        self.count_epoch = QtWidgets.QTextEdit(class_cnn_form)
        self.count_epoch.setEnabled(True)
        self.count_epoch.setGeometry(QtCore.QRect(100, 10, 41, 31))
        self.count_epoch.setObjectName("count_epoch")
        self.ver_segm_lbl_4 = QtWidgets.QLabel(class_cnn_form)
        self.ver_segm_lbl_4.setGeometry(QtCore.QRect(10, 10, 91, 31))
        self.ver_segm_lbl_4.setWordWrap(True)
        self.ver_segm_lbl_4.setObjectName("ver_segm_lbl_4")
        self.add_pose = QtWidgets.QPushButton(class_cnn_form)
        self.add_pose.setGeometry(QtCore.QRect(190, 50, 171, 41))
        self.add_pose.setObjectName("add_pose")
        self.ver_segm_lbl_5 = QtWidgets.QLabel(class_cnn_form)
        self.ver_segm_lbl_5.setGeometry(QtCore.QRect(190, 0, 31, 31))
        self.ver_segm_lbl_5.setWordWrap(True)
        self.ver_segm_lbl_5.setObjectName("ver_segm_lbl_5")
        self.gest_table = QtWidgets.QTableWidget(class_cnn_form)
        self.gest_table.setGeometry(QtCore.QRect(10, 100, 261, 281))
        self.gest_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.gest_table.setWordWrap(True)
        self.gest_table.setRowCount(1)
        self.gest_table.setColumnCount(2)
        self.gest_table.setObjectName("gest_table")
        item = QtWidgets.QTableWidgetItem()
        self.gest_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.gest_table.setHorizontalHeaderItem(1, item)

        self.retranslateUi(class_cnn_form)
        QtCore.QMetaObject.connectSlotsByName(class_cnn_form)

    def retranslateUi(self, class_cnn_form):
        _translate = QtCore.QCoreApplication.translate
        class_cnn_form.setWindowTitle(_translate("class_cnn_form", "Редактирование классифицирующей нейросети"))
        self.start_training.setText(_translate("class_cnn_form", "Запустить обучение"))
        self.count_epoch.setHtml(_translate("class_cnn_form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">10</p></body></html>"))
        self.ver_segm_lbl_4.setText(_translate("class_cnn_form", "Количество эпох"))
        self.add_pose.setText(_translate("class_cnn_form", "Добавить пример жеста"))
        self.ver_segm_lbl_5.setText(_translate("class_cnn_form", "Жест"))
        item = self.gest_table.horizontalHeaderItem(0)
        item.setText(_translate("class_cnn_form", "Название"))
        item = self.gest_table.horizontalHeaderItem(1)
        item.setText(_translate("class_cnn_form", "Количество примеров"))


