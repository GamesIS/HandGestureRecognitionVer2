import os
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets, QtGui
import design  # Это наш конвертированный файл дизайна
import gui
from multiprocessing import Queue, Pool
from utils import db_utils as db_utils
import ctypes
import HandPose as rec_class

# Установка значка приложения в taskBar
my_app_id = 'ilku.hrs.cnn.1.0'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)

class MainController(QtWidgets.QMainWindow, design.Ui_HandGestureRecognitionSystem):
    recognition = None

    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.startButton.clicked.connect(self.start_hand_pose)
        self.recognition = rec_class.HandPose(mainController=self)
        self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)

        self.startDetection.clicked.connect(self.start_detection)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.close

        self.rb_def_cam.mode = 0
        self.rb_ip_cam.mode = 1
        self.rb_def_cam.toggled.connect(self.on_clicked_rb)
        self.rb_ip_cam.toggled.connect(self.on_clicked_rb)
        self.trsh_segm_sldr.valueChanged.connect(lambda: self.value_change(self.trsh_segm_sldr))
        self.trsh_class_sldr.valueChanged.connect(lambda: self.value_change(self.trsh_class_sldr))

        self.countHandsCB.addItems(["1 рука", "2 руки", "10 рук(демо)"])

    def value_change(self, trsh):
        if(trsh.objectName() == 'trsh_segm_sldr'):
            self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
            self.thr_lbl_segm_val.setText(str(self.recognition.settings.threshold))
        else:
            #self.recognition.settings.threshold = float(self.trsh_segm_sldr.value() / 100)
            #TODO здесь для классификации
            self.thr_lbl_class_val.setText(str(self.recognition.settings.threshold))

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
            self.send_json_group.setEnabled(True)
        else:
            self.send_json_group.setEnabled(False)
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
            self.address_cam.setEnabled(False)
        elif self.rb_ip_cam.isChecked():
            self.address_cam.setEnabled(True)

    def closeEvent(self, event):
        self.destory()


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = MainController()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
