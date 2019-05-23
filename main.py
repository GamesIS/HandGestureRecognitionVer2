import ctypes
import os
import re
import sys  # sys нужен для передачи argv в QApplication
from multiprocessing import Queue

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

import HandPose as rec_class
import design  # Это наш конвертированный файл дизайна
import gestures
import gui
from utils import db_utils as db_utils

# Установка значка приложения в taskBar
my_app_id = 'ilku.hrs.cnn.1.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = '9876'
DEFAULT_ADDRESS_CAM = 'http://192.168.0.84:8080/video'

SEGM_CNN_VERSION_1 = '/frozen_inference_graph.pb'
SEGM_CNN_VERSION_2 = '/frozen_inference_graph2.pb'


class MainController(QtWidgets.QMainWindow, design.Ui_HandGestureRecognitionSystem):
    Gestures = db_utils.load_json_poses()

    recognition = None

    ip_valid = True
    port_valid = True
    ip_cam_valid = True

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.startButton.clicked.connect(self.start_hand_pose)
        self.recognition = rec_class.HandPose(mainController=self)
        self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
        self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
        self.recognition.version_segm_cnn = SEGM_CNN_VERSION_1

        self.startDetection.clicked.connect(self.start_detection)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.close

        self.rb_def_cam.mode = 0
        self.rb_ip_cam.mode = 1
        self.rb_def_cam.toggled.connect(self.on_clicked_rb)
        self.rb_ip_cam.toggled.connect(self.on_clicked_rb)
        self.trsh_segm_sldr.valueChanged.connect(lambda: self.value_change_thrsh(self.trsh_segm_sldr))
        self.trsh_class_sldr.valueChanged.connect(lambda: self.value_change_thrsh(self.trsh_class_sldr))
        self.cb_json.clicked.connect(self.set_def_ip_port)

        self.ip_host.textChanged.connect(self.value_change_ip)
        self.port_host.textChanged.connect(self.value_change_port)
        self.address_cam.textChanged.connect(self.value_change_ip_cam)

        self.rb_segm_1.clicked.connect(self.change_segm_cnn)
        self.rb_segm_2.clicked.connect(self.change_segm_cnn)

        self.countHandsCB.addItems(["1 рука", "2 руки", "10 рук(демо)"])
        self.countHandsCB.activated.connect(self.count_hands_changed)

        self.gestures_win = None
        self.open_list_gestures.clicked.connect(self.open_gestures_win)

    def count_hands_changed(self):
        if self.countHandsCB.currentIndex() == 0:
            self.recognition.settings.countHands = 1
        elif self.countHandsCB.currentIndex() == 1:
            self.recognition.settings.countHands = 2
        elif self.countHandsCB.currentIndex() == 2:
            self.recognition.settings.countHands = 10

    def change_segm_cnn(self):
        if self.rb_segm_1.isChecked():
            self.recognition.version_segm_cnn = SEGM_CNN_VERSION_1
        else:
            self.recognition.version_segm_cnn = SEGM_CNN_VERSION_2

    def set_def_ip_port(self):
        if self.recognition.recognition_started == False:
            if self.cb_json.isChecked():
                self.ip_host.setEnabled(True)
                self.port_host.setEnabled(True)
            else:
                self.ip_host.setEnabled(False)
                self.port_host.setEnabled(False)
            self.ip_host.setPlainText(DEFAULT_IP)
            self.port_host.setPlainText(DEFAULT_PORT)
            if self.ip_cam_valid:
                self.startDetection.setEnabled(True)

    def value_change_thrsh(self, trsh):
        if (trsh.objectName() == 'trsh_segm_sldr'):
            self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
            self.thr_lbl_segm_val.setText(str(self.recognition.settings.threshold))
        else:
            # self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
            # TODO здесь для классификации
            self.thr_lbl_class_val.setText(str(self.recognition.settings.threshold))

    def value_change_port(self):
        pattern = re.compile("^()([1-9]|[1-5]?[0-9]{2,4}|6[1-4][0-9]{3}|65[1-4][0-9]{2}|655[1-2][0-9]|6553[1-5])$")
        value = pattern.match(self.port_host.toPlainText())
        if value == None:
            self.port_valid = False
            self.port_host.setStyleSheet("border: 2px solid red;")
            self.startDetection.setEnabled(False)
            return
        else:
            self.port_valid = True
            self.port_host.setStyleSheet("")

        if self.validate():
            self.startDetection.setEnabled(True)

    def value_change_ip_cam(self):
        pattern = re.compile("^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$")
        value = pattern.match(self.address_cam.toPlainText())
        if value == None:
            self.ip_cam_valid = False
            self.address_cam.setStyleSheet("border: 2px solid red;")
            self.startDetection.setEnabled(False)
            return
        else:
            self.ip_cam_valid = True
            self.address_cam.setStyleSheet("")
        if self.validate():
            self.startDetection.setEnabled(True)

    def value_change_ip(self):
        pattern = re.compile(
            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
        value = pattern.match(self.ip_host.toPlainText())
        if value == None:
            self.ip_valid = False
            self.ip_host.setStyleSheet("border: 2px solid red;")
            self.startDetection.setEnabled(False)
            return
        else:
            self.ip_valid = True
            self.ip_host.setStyleSheet("")
        if self.validate():
            self.startDetection.setEnabled(True)

    def validate(self):
        if (self.ip_cam_valid and self.ip_valid and self.port_valid):
            return True
        return False

    def start_hand_pose(self):
        poses = db_utils.load_poses_names("poses.txt")
        queue_size = 5
        inferences_q = Queue(maxsize=queue_size)
        inferences = None
        try:
            inferences = inferences_q.get_nowait()
        except Exception as e:
            pass
        values = [0.5, 0.2, 0.3]
        gui.drawInferences(values, poses)

    def start_detection(self):
        if self.recognition.recognition_started:
            self.recognition.recognition_started = False
            self.startDetection.setText("Включить отслеживание")
            if self.cb_json.isChecked():
                self.ip_host.setEnabled(True)
                self.port_host.setEnabled(True)
        else:
            self.ip_host.setEnabled(False)
            self.port_host.setEnabled(False)
            self.startDetection.setText("Выключить отслеживание")
            self.recognition.start()

    def browse_folder(self):
        self.listWidget.clear()  # На случай, если в списке уже есть элементы
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            for file_name in os.listdir(directory):  # для каждого файла в директории
                self.listWidget.addItem(file_name)  # добавить файл в listWidget

    def on_clicked_rb(self):
        if self.rb_def_cam.isChecked():
            self.address_cam.setPlainText(DEFAULT_ADDRESS_CAM)
            self.address_cam.setEnabled(False)
        elif self.rb_ip_cam.isChecked():
            self.address_cam.setEnabled(True)

    def closeEvent(self, event):
        self.destory()

    def open_gestures_win(self):
        if not self.gestures_win:
            self.gestures_win = GesturesWin(self)
        if self.gestures_win.isVisible():
            self.gestures_win.hide()
        else:
            self.gestures_win.show()
            self.gestures_win.init_table()


class GesturesWin(QtWidgets.QMainWindow):
    main = None

    def __init__(self, parent):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.main = parent
        self.ui = gestures.Ui_new_form()
        self.ui.setupUi(self)
        self.ui.save_gesture.clicked.connect(self.save_gesture_json)
        self.init_table()
        self.ui.gesture_table.resizeColumnsToContents()
        self.ui.gesture_table.cellChanged.connect(self.validate_table)
        self.ui.add_gesture.clicked.connect(self.add_gesture)

    def add_gesture(self):
        self.ui.save_gesture.setEnabled(False)
        self.ui.add_gesture.setEnabled(False)
        row_count = self.ui.gesture_table.rowCount() + 1
        self.ui.gesture_table.setRowCount(row_count)
        one_cellinfo = QTableWidgetItem("")
        two_cellinfo = QTableWidgetItem("")
        self.ui.gesture_table.setItem(row_count - 1, 0, one_cellinfo)
        self.ui.gesture_table.setItem(row_count - 1, 1, two_cellinfo)

    def init_table(self):
        poses = self.main.Gestures
        poses.__class__ = db_utils.Poses
        self.ui.gesture_table.setRowCount(len(poses.gestures))

        row = 0
        for item in poses.gestures:
            one_cellinfo = QTableWidgetItem(item)
            two_cellinfo = QTableWidgetItem(poses.group[poses.gestures_group[row]])

            # combo = QtWidgets.QComboBox()
            # combo.addItem("Изучить")
            # combo.addItem("Забыть")
            # combo.addItem("Удалить")

            self.ui.gesture_table.setItem(row, 0, one_cellinfo)
            self.ui.gesture_table.setItem(row, 1, two_cellinfo)
            #self.ui.gesture_table.setCellWidget(row, 1, combo)
            row += 1

    def save_gesture_json(self):
        try:

            poses = self.main.Gestures
            poses.__class__ = db_utils.Poses

            gestures = []
            group = poses.group
            gestures_group = []
            for row in range(self.ui.gesture_table.rowCount()):
                gestures.append(self.ui.gesture_table.item(row, 0).text())
                grp = self.ui.gesture_table.item(row, 1).text()
                if grp not in poses.group:
                    group.append(grp)
                gestures_group.append(group.index(grp))
            poses.gestures = gestures
            poses.group = group
            poses.gestures_group = gestures_group
            db_utils.save_json_poses(poses)
        except Exception as e:
            print(e)

    def rename_folders(self):
        pass

    def validate_table(self):
        try:
            poses = self.main.Gestures
            poses.__class__ = db_utils.Poses
            current_gest = self.get_all_gest_str()

            for row in range(self.ui.gesture_table.rowCount()):
                if current_gest.count(self.ui.gesture_table.item(row, 0).text()) > 1:
                    self.ui.save_gesture.setEnabled(False)
                    self.ui.add_gesture.setEnabled(False)
                    show_error("Название жеста должно быть уникальным.", "Предупреждение")
                    return

            self.ui.save_gesture.setEnabled(True)
            self.ui.add_gesture.setEnabled(True)
        except Exception as e:
            print(e)

    def get_all_gest_str(self):
        gestures = []
        for row in range(self.ui.gesture_table.rowCount()):
            gestures.append(self.ui.gesture_table.item(row, 0).text())
        return gestures



def show_error(message, title):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.exec_()

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainController()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
