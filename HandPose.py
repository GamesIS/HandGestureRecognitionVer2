import os;
import time
from multiprocessing import Queue, Pool

import cv2
import tensorflow as tf

from utils import detector_utils as detector_utils, json_sender
from utils import pose_classification_utils as classifier
from utils.detector_utils import WebcamVideoStream

os.environ['KERAS_BACKEND'] = 'tensorflow'
import gui
import monitoring as mon

frame_processed = 0
score_thresh = 0.27
window_name = 'Camera'

CLASS_NO_GESTURE = "Нет жеста"

def worker(input_q, output_q, cropped_output_q, inferences_q, cap_params, frame_processed, settings_q,
           version_segm_cnn, poses, enable_gesture, job_time, status_cnn_q, finded_gest_q):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph(version_segm_cnn)
    sess = tf.Session(graph=detection_graph)

    print(">> loading keras model for worker")
    model, classification_graph, session = classifier.load_KerasGraph("cnn/models/hand_poses_wGarbage_every.h5")

    monitor = mon.Monitor(False, enable_gesture, 15)

    active_cnn_class = False
    gest_eq = False

    if enable_gesture == CLASS_NO_GESTURE:
        gest_eq = True
        active_cnn_class = True
    else:
        gest_eq = False
        active_cnn_class = False
    last_start_time = -1
    while True:
        finded_gest = finded_gest_q.get()
        if last_start_time != -1:
            if finded_gest is not None:
                if finded_gest:
                    last_start_time = int(time.time())
            curTime = int(time.time())
            if curTime - last_start_time >= job_time:
                last_start_time = -1
                monitor.last_start_time = -1
                active_cnn_class = False
        frame = input_q.get()
        if frame is not None:

            settings = settings_q.get()
            thresh = settings.threshold
            boxes, scores = detector_utils.detect_objects(
                frame, detection_graph, sess)

            res = detector_utils.get_box_image(settings.countHands, thresh,
                                               scores, boxes, cap_params['im_width'], cap_params['im_height'],
                                               frame)

            detector_utils.draw_box_on_image(settings.countHands, thresh,
                                             scores, boxes, cap_params['im_width'], cap_params['im_height'], frame)

            if res is not None:
                class_res = classifier.classify(model, classification_graph, session, res)
                if not gest_eq and last_start_time == -1:
                    last_start_time = monitor.monitoring(names=poses, predictions=class_res, threshold=0.7, main=None)
                    if last_start_time == -1:
                        res = None
                    else:
                        active_cnn_class = True
                else:
                    inferences_q.put(class_res)

            cropped_output_q.put(res)
            output_q.put(frame)
            status_cnn_q.put(active_cnn_class)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()


class Settings:
    threshold = score_thresh
    fpsISEnabled = True
    detailsISEnabled = True
    details_run = True
    countHands = 1

    def __init__(self):
        pass


class HandPose:
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_INDEX = 0
    QUEUE_SIZE = 5
    main = None
    recognition_started = False
    settings = Settings()
    version_segm_cnn = "Нет жеста"

    def __init__(self, mainController):
        self.main = mainController

    def start(self):
        self.recognition_started = True
        input_q = Queue(maxsize=self.QUEUE_SIZE)
        output_q = Queue(maxsize=self.QUEUE_SIZE)
        settings_q = Queue(maxsize=self.QUEUE_SIZE)
        cropped_output_q = Queue(maxsize=self.QUEUE_SIZE)
        inferences_q = Queue(maxsize=self.QUEUE_SIZE)
        status_cnn_q = Queue(maxsize=self.QUEUE_SIZE)
        fi_q = Queue(maxsize=self.QUEUE_SIZE)

        if self.main.rb_ip_cam.isChecked():
            video_capture = WebcamVideoStream(
                self.main.address_cam.toPlainText(), width=self.CAMERA_WIDTH, height=self.CAMERA_HEIGHT).start()
        else:
            video_capture = WebcamVideoStream(
                src=self.CAMERA_INDEX, width=self.CAMERA_WIDTH, height=self.CAMERA_HEIGHT).start()

        cap_params = {}
        frame_processed = 0
        cap_params['im_width'], cap_params['im_height'] = video_capture.size()
        print(cap_params['im_width'], cap_params['im_height'])
        cap_params['score_thresh'] = score_thresh

        poses = self.main.Gestures.gestures

        num_workers = 1

        pool = Pool(num_workers, worker,
                    (input_q, output_q, cropped_output_q, inferences_q, cap_params, frame_processed, settings_q,
                     self.version_segm_cnn, poses, self.main.class_gest_cb.currentText(), 10, status_cnn_q, fi_q))

        start_time_millis = int(round(time.time() * 1000))
        fps = 0
        index = 0

        last_sett_o = False
        finded_gest = False

        monitor = mon.Monitor(True, None, 15)
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while cv2.getWindowProperty(window_name, 0) >= 0 and self.recognition_started:
            fi_q.put(finded_gest)
            if not self.settings.detailsISEnabled and self.settings.details_run:
                cv2.destroyWindow('Cropped')
                cv2.destroyWindow('Inferences')
                self.settings.details_run = False
            if self.settings.fpsISEnabled:
                start_time_millis = int(round(time.time() * 1000))
            settings_q.put(self.settings)

            frame = video_capture.read()
            frame = cv2.flip(frame, 1)
            index += 1

            try:
                input_q.put(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            except Exception:
                input_q.put(cv2.cvtColor(cv2.imread("no_signal.jpg"), cv2.COLOR_BGR2RGB))
                video_capture.noSignal = True

            output_frame = output_q.get()
            cropped_output = cropped_output_q.get()
            st_sett_o = status_cnn_q.get()

            if st_sett_o != None:
                if last_sett_o != st_sett_o:
                    self.main.change_en_cnn(st_sett_o)
                    last_sett_o = st_sett_o

            inferences = None

            try:
                inferences = inferences_q.get_nowait()
            except Exception as e:
                pass

            if self.settings.fpsISEnabled:
                fps = int(1000 / (int(round(time.time() * 1000)) - start_time_millis))

            # Display inferences
            if inferences is not None:
                if self.settings.detailsISEnabled:
                    gui.drawInferences(inferences, poses)
                if self.main.cb_json.isChecked():
                    json_sender.send_json(inferences, poses, self.main.ip_host.toPlainText(),
                                          int(self.main.port_host.toPlainText()))
                if 0 == monitor.monitoring(names=poses, predictions=inferences, threshold=0.7, main=self.main):
                    finded_gest = True
                else:
                    finded_gest = False


            if cropped_output is not None:
                if self.settings.detailsISEnabled:
                    cropped_output = cv2.cvtColor(cropped_output, cv2.COLOR_RGB2BGR)
                    cv2.namedWindow('Cropped', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Cropped', 450, 300)
                    cv2.imshow('Cropped', cropped_output)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            if output_frame is not None:
                output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)
                if self.settings.fpsISEnabled:
                    detector_utils.draw_fps_on_image("FPS : " + str(int(fps)),
                                                     output_frame)
                cv2.imshow(window_name, output_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            else:
                print("video end")
                break
        pool.terminate()
        video_capture.stop()
        cv2.destroyAllWindows()
        self.recognition_off()

    def recognition_off(self):
        if (self.recognition_started != False):
            self.main.start_detection()

    def power_details(self, bool):
        self.settings.detailsISEnabled = bool
        if(bool == True):
            self.settings.details_run = bool
    def power_fps(self, bool):
        self.settings.fpsISEnabled = bool

