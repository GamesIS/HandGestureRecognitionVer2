# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gestures.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_new_form(object):
    def setupUi(self, new_form):
        new_form.setObjectName("new_form")
        new_form.resize(268, 336)
        self.gesture_table = QtWidgets.QTableWidget(new_form)
        self.gesture_table.setGeometry(QtCore.QRect(10, 10, 251, 271))
        self.gesture_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.gesture_table.setWordWrap(True)
        self.gesture_table.setRowCount(1)
        self.gesture_table.setColumnCount(2)
        self.gesture_table.setObjectName("gesture_table")
        item = QtWidgets.QTableWidgetItem()
        self.gesture_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.gesture_table.setHorizontalHeaderItem(1, item)
        self.add_gesture = QtWidgets.QPushButton(new_form)
        self.add_gesture.setGeometry(QtCore.QRect(140, 290, 111, 31))
        self.add_gesture.setObjectName("add_gesture")
        self.save_gesture = QtWidgets.QPushButton(new_form)
        self.save_gesture.setGeometry(QtCore.QRect(20, 290, 101, 31))
        self.save_gesture.setObjectName("save_gesture")

        self.retranslateUi(new_form)
        QtCore.QMetaObject.connectSlotsByName(new_form)

    def retranslateUi(self, new_form):
        _translate = QtCore.QCoreApplication.translate
        new_form.setWindowTitle(_translate("new_form", "Список жестов"))
        item = self.gesture_table.horizontalHeaderItem(0)
        item.setText(_translate("new_form", "Название"))
        item = self.gesture_table.horizontalHeaderItem(1)
        item.setText(_translate("new_form", "Группа"))
        self.add_gesture.setText(_translate("new_form", "Добавить жест"))
        self.save_gesture.setText(_translate("new_form", "Сохранить"))


