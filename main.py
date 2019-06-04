import ctypes
import os
import re
import sys  # sys нужен для передачи argv в QApplication

import cyrtranslit
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox

import AddPose
import HandPose as rec_class
import class_cnn
import design  # Это наш конвертированный файл дизайна
import gestures
import gui_monitoring
from cnn import cnn
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

    reset_gesture_mon = False

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.recognition = rec_class.HandPose(mainController=self)
        self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
        self.recognition.version_segm_cnn = SEGM_CNN_VERSION_1
        self.startDetection.clicked.connect(self.start_detection)
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.rb_def_cam.mode = 0
        self.rb_ip_cam.mode = 1
        self.rb_def_cam.toggled.connect(self.on_clicked_rb)
        self.rb_ip_cam.toggled.connect(self.on_clicked_rb)
        self.trsh_segm_sldr.valueChanged.connect(lambda: self.value_change_thrsh(self.trsh_segm_sldr))
        self.trsh_class_sldr.valueChanged.connect(lambda: self.value_change_thrsh(self.trsh_class_sldr))

        self.trsh_class_sldr.setHidden(True)
        self.thr_lbl_class_val.setHidden(True)
        self.thr_lbl_class.setHidden(True)
        self.cb_json.clicked.connect(self.set_def_ip_port)

        self.ip_host.textChanged.connect(self.value_change_ip)
        self.port_host.textChanged.connect(self.value_change_port)
        self.address_cam.textChanged.connect(self.value_change_ip_cam)

        self.rb_segm_1.clicked.connect(self.change_segm_cnn)
        self.rb_segm_2.clicked.connect(self.change_segm_cnn)

        self.countHandsCB.addItems(["1 рука", "2 руки(демо)", "10 рук(демо)"])
        self.countHandsCB.activated.connect(self.count_hands_changed)

        self.gestures_win = None
        self.open_list_gestures.clicked.connect(self.open_gestures_win)

        self.class_cnn_win = None
        self.sett_class_cnn.clicked.connect(self.open_class_cnn_win)

        self.monitor = None
        self.open_monitor_btn.clicked.connect(self.open_monitor_win)

        poses = self.Gestures.gestures.copy()
        poses.insert(0, "Нет жеста")
        self.class_gest_cb.addItems(poses)
        self.class_gest_cb.activated.connect(self.class_gest_cb_changed)

        self.details_cb.clicked.connect(self.destroy_cv2)
        self.fps_enabled.clicked.connect(self.power_fps)

        pixmap = QPixmap('off_led.png')
        self.on_off_image.setPixmap(pixmap)
        self.on_off_image.setScaledContents(True)

    def change_en_cnn(self, bool):
        if bool:
            pixmap = QPixmap('on_led.png')
            self.on_off_image.setPixmap(pixmap)
            self.on_off_image.setScaledContents(True)
        else:
            pixmap = QPixmap('off_led.png')
            self.on_off_image.setPixmap(pixmap)
            self.on_off_image.setScaledContents(True)

    def power_fps(self):
        self.recognition.power_fps(self.fps_enabled.isChecked())

    def destroy_cv2(self):
        self.recognition.power_details(self.details_cb.isChecked())

    def count_hands_changed(self):
        if self.countHandsCB.currentIndex() == 0:
            self.recognition.settings.countHands = 1
        elif self.countHandsCB.currentIndex() == 1:
            self.recognition.settings.countHands = 2
        elif self.countHandsCB.currentIndex() == 2:
            self.recognition.settings.countHands = 10

    def class_gest_cb_changed(self):
        pass

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

    def start_detection(self):
        if self.recognition.recognition_started:
            self.recognition.recognition_started = False
            self.startDetection.setText("Включить отслеживание")
            self.change_en_cnn(False)
            self.class_gest_cb.setEnabled(True)
            if self.cb_json.isChecked():
                self.ip_host.setEnabled(True)
                self.port_host.setEnabled(True)
        else:
            self.class_gest_cb.setEnabled(False)
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
        self.destroy()

    def open_gestures_win(self):
        if not self.gestures_win:
            self.gestures_win = GesturesWin(self)
        if self.gestures_win.isVisible():
            self.gestures_win.hide()
        else:
            self.gestures_win.show()
            self.gestures_win.init_table()

    def open_class_cnn_win(self):
        if not self.class_cnn_win:
            self.class_cnn_win = ClassCNN(self)
        if self.class_cnn_win.isVisible():
            self.class_cnn_win.hide()
        else:
            self.class_cnn_win.show()
            self.class_cnn_win.update_gestures_cb()

    def open_monitor_win(self):
        if not self.monitor:
            self.monitor = Monitor(self)
        if self.monitor.isVisible():
            self.monitor.hide()
        else:
            self.monitor.show()
            # self.monitor.update_gestures_cb()


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
        one_cellinfo = QTableWidgetItem("Жест")
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
            # self.ui.gesture_table.setCellWidget(row, 1, combo)
            row += 1

    def save_gesture_json(self):
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
        minIndex = len(poses.gestures)
        if minIndex > len(gestures):
            minIndex = len(gestures)
        minIndex = minIndex - 1
        index = 0
        for oldGesture in poses.gestures:
            if index > minIndex:
                break
            if gestures[index] != oldGesture:
                rename_folders(oldGesture, gestures[index])
            index = index + 1
        poses.gestures = gestures
        # check_folders(poses.gestures)
        poses.group = group
        poses.gestures_group = gestures_group
        db_utils.save_json_poses(poses)

    def validate_table(self):
        poses = self.main.Gestures
        poses.__class__ = db_utils.Poses
        current_gest = self.get_all_gest_str()

        for row in range(self.ui.gesture_table.rowCount()):
            if current_gest.count(self.ui.gesture_table.item(row, 0).text()) > 1:
                self.ui.save_gesture.setEnabled(False)
                self.ui.add_gesture.setEnabled(False)
                show_error("Название жеста должно быть уникальным.", "Предупреждение")
                return
            if self.ui.gesture_table.item(row, 0).text() == "":
                show_error("Названи жеста не может быть пустым", "Предупреждение")

        self.ui.save_gesture.setEnabled(True)
        self.ui.add_gesture.setEnabled(True)

    def get_all_gest_str(self):
        gestures = []
        for row in range(self.ui.gesture_table.rowCount()):
            gestures.append(self.ui.gesture_table.item(row, 0).text())
        return gestures


class ClassCNN(QtWidgets.QMainWindow):
    main = None

    def __init__(self, parent):
        try:
            QtWidgets.QMainWindow.__init__(self, parent)
            self.main = parent
            self.ui = class_cnn.Ui_class_cnn_form()
            self.ui.setupUi(self)
            self.update_gestures_cb()
            self.ui.add_pose.clicked.connect(self.add_pose)
            self.ui.start_training.clicked.connect(self.start_training_cnn)
        except Exception as e:
            print(e)

    def start_training_cnn(self):
        cnn.train(int(self.ui.count_epoch.toPlainText()))

    def add_pose(self):
        AddPose.main(self.ui.gestures_cb.currentText(), self.main.recognition.version_segm_cnn)

    def init_table(self):
        poses = self.main.Gestures
        poses.__class__ = db_utils.Poses
        self.ui.gest_table.setRowCount(len(poses.gestures))

        row = 0
        for item in poses.gestures:
            one_cellinfo = QTableWidgetItem(item)
            two_cellinfo = QTableWidgetItem(str(get_count_examples(item)))
            one_cellinfo.setFlags(QtCore.Qt.ItemIsEnabled)
            two_cellinfo.setFlags(QtCore.Qt.ItemIsEnabled)

            self.ui.gest_table.setItem(row, 0, one_cellinfo)
            self.ui.gest_table.setItem(row, 1, two_cellinfo)

            row += 1
        self.ui.gest_table.resizeColumnsToContents()

    def update_gestures_cb(self):
        self.ui.gestures_cb.clear()
        self.init_table()
        self.ui.gestures_cb.addItems(self.main.Gestures.gestures)


class Monitor(QtWidgets.QMainWindow):
    main = None

    abs_general_list = []
    abs_group_list = []

    def __init__(self, parent):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.main = parent
        self.ui = gui_monitoring.Ui_monitoring_form()
        self.ui.setupUi(self)
        self.init_table()
        self.ui.clear_btn_gest.clicked.connect(self.reset_gesture)
        self.ui.thr_lbl_class_2.setHidden(True)
        self.ui.trsh_class_sldr_2.setHidden(True)
        self.ui.thr_lbl_class_val_2.setHidden(True)

    def reset_gesture(self):
        self.main.reset_gesture_mon = True
        self.last_general_colored_row = -1
        self.last_group_colored_row = -1
        self.abs_general_list = []
        self.init_table()


    def init_table(self):
        self.ui.overall_gest.setText("Всего распознано жестов: ")

        row = 0
        self.ui.general_table_gest.setRowCount(len(self.main.Gestures.gestures))
        for group in self.main.Gestures.gestures:
            one_cellinfo = QTableWidgetItem(group)
            abs = 0

            self.ui.general_table_gest.setItem(row, 0, one_cellinfo)

            # Создаем QProgressBar
            abs_progr = QtWidgets.QProgressBar()
            abs_progr.setMinimum(0)
            abs_progr.setMaximum(100)

            # Формат вывода: 10.50%
            abs_progr.setValue(abs)
            abs_progr.setFormat('{0:.2f}%'.format(abs))

            self.ui.general_table_gest.setCellWidget(row, 1, abs_progr)

            self.abs_general_list.append(abs_progr)

            row += 1

        self.ui.general_table_gest.resizeColumnsToContents()
            ########################################################
        row = 0
        self.ui.group_table.setRowCount(len(self.main.Gestures.group))
        for group in self.main.Gestures.group:
            one_cellinfo = QTableWidgetItem(group)
            if group == "":
                one_cellinfo = QTableWidgetItem("Нет группы")
            abs = 0

            self.ui.group_table.setItem(row, 0, one_cellinfo)

            # Создаем QProgressBar
            abs_progr = QtWidgets.QProgressBar()
            abs_progr.setMinimum(0)
            abs_progr.setMaximum(100)

            # Формат вывода: 10.50%
            abs_progr.setValue(abs)
            abs_progr.setFormat('{0:.2f}%'.format(abs))

            self.ui.group_table.setCellWidget(row, 1, abs_progr)

            self.abs_group_list.append(abs_progr)

            row += 1

        self.ui.group_table.resizeColumnsToContents()

    last_general_colored_row = -1
    last_group_colored_row = -1
    white = QtGui.QColor(255, 255, 255)
    green = QtGui.QColor(0, 255, 0)

    def fill_general_table(self, names, count_gestures, overall_count, finish_gesture):
        row = 0
        for name in names:
            abs = 0
            if overall_count != 0:
                abs = (count_gestures[row] / overall_count) * 100

            self.abs_general_list[row].setValue(abs)
            self.abs_general_list[row].setFormat('{0:.2f}%'.format(abs))

            if finish_gesture.name == name:
                if self.last_general_colored_row != row:
                    self.ui.general_table_gest.item(row, 0).setBackground(self.green)
                    if self.last_general_colored_row != -1:
                        self.ui.general_table_gest.item(self.last_general_colored_row, 0).setBackground(
                            self.white)
                    self.last_general_colored_row = row

            row += 1
        self.ui.overall_gest.setText("Всего распознано жестов: " + str(overall_count))
        self.ui.general_table_gest.resizeColumnsToContents()

    def setColortoRow(self, table, rowIndex, color):
        for j in range(table.columnCount()):
            table.item(rowIndex, j).setBackground(color)

    start_color = 50
    end_color = 255
    def calc_color(self, min, max, count):
        x = (count - min) / (max - min)
        color = x * self.start_color + (x - 1) * self.end_color

        return QtGui.QColor(color, 0, 0)


    def fill_group_table(self, groups, count_groups, overall_count, finish_group):
        min = overall_count
        max = 0
        for val in count_groups:
            if val > max:
                max = val
            if val < min:
                min = val

        row = 0
        for name in groups:

            abs = 0
            if overall_count != 0:
                abs = (count_groups[row] / overall_count) * 100

            self.abs_group_list[row].setValue(abs)
            self.abs_group_list[row].setFormat('{0:.2f}%'.format(abs))

            if finish_group == name:
                if self.last_group_colored_row != row:
                    self.ui.group_table.item(row, 0).setBackground(self.green)
                    if self.last_group_colored_row != -1:
                        self.ui.group_table.item(self.last_group_colored_row, 0).setBackground(
                            self.white)
                    self.last_group_colored_row = row

            if finish_group == name and overall_count > 10 and name != "":
                if self.last_group_colored_row != row:
                    self.setColortoRow(self.ui.group_table, row, self.calc_color(min, max, count_groups[row]))
                    self.ui.group_table.item(row, 0).setBackground(self.green)

            row += 1
        self.ui.group_table.resizeColumnsToContents()


def get_count_examples(pose):
    pose = cyrtranslit.to_latin(pose, 'ru')
    poses = os.listdir('Poses/')
    count = 0
    if not os.path.exists('Poses/' + pose + '/'):
        os.makedirs('Poses/' + pose + '/')
    subdirs = os.listdir('Poses/' + pose + '/')
    for subdir in subdirs:
        files = os.listdir('Poses/' + pose + '/' + subdir + '/')
        count = count + len(files)
    return count


def rename_folders(oldName, newName):
    oldName = cyrtranslit.to_latin(oldName, 'ru')
    newName = cyrtranslit.to_latin(newName, 'ru')
    index = 1
    oldPath = 'Poses/' + oldName + '/'
    if os.path.exists(oldPath):
        subdirs = os.listdir(oldPath)
        for sub in subdirs:
            print(sub)
            os.rename(oldPath + sub, oldPath + newName + "_" + str(index))
            index = index + 1
        os.rename(oldPath, 'Poses/' + newName + '/')


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
