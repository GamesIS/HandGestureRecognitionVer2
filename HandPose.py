import argparse
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


# Create a worker thread that loads graph and
# does detection on images in an input queue and puts it on an output queue
def worker(input_q, output_q, cropped_output_q, inferences_q, cap_params, frame_processed, settings_q,
           version_segm_cnn):
    print(">> loading frozen model for worker")
    detection_graph, sess = detector_utils.load_inference_graph(version_segm_cnn)
    sess = tf.Session(graph=detection_graph)

    print(">> loading keras model for worker")
    model, classification_graph, session = classifier.load_KerasGraph("cnn/models/hand_poses_wGarbage_13.h5")

    while True:
        # print("> ===== in worker loop, frame ", frame_processed)
        frame = input_q.get()
        if (frame is not None):
            # Actual detection. Variable boxes contains the bounding box cordinates for hands detected,
            # while scores contains the confidence for each of these boxes.
            # Hint: If len(boxes) > 1 , you may assume you have found atleast one hand (within your score threshold)
            settings = settings_q.get()
            thresh = settings.threshold
            boxes, scores = detector_utils.detect_objects(
                frame, detection_graph, sess)

            # get region of interest
            res = detector_utils.get_box_image(settings.countHands, thresh,
                                               scores, boxes, cap_params['im_width'], cap_params['im_height'],
                                               frame)

            # draw bounding boxes
            detector_utils.draw_box_on_image(settings.countHands, thresh,
                                             scores, boxes, cap_params['im_width'], cap_params['im_height'], frame)

            # classify hand pose
            if res is not None:
                class_res = classifier.classify(model, classification_graph, session, res)
                inferences_q.put(class_res)

                # add frame annotated with bounding box to queue
            cropped_output_q.put(res)
            output_q.put(frame)
            frame_processed += 1
        else:
            output_q.put(frame)
    sess.close()


class Settings:
    threshold = score_thresh
    fpsISEnabled = True
    countHands = 1

    def __init__(self):
        pass


class HandPose:
    main = None
    recognition_started = False
    settings = Settings()
    version_segm_cnn = ""

    def __init__(self, mainController):
        self.main = mainController

    def start(self):
        self.recognition_started = True
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-src',
            '--source',
            dest='video_source',
            type=int,
            default=0,
            help='Device index of the camera.')
        parser.add_argument(
            '-wd',
            '--width',
            dest='width',
            type=int,
            default=300,
            help='Width of the frames in the video stream.')
        parser.add_argument(
            '-ht',
            '--height',
            dest='height',
            type=int,
            default=200,
            help='Height of the frames in the video stream.')
        parser.add_argument(
            '-ds',
            '--display',
            dest='display',
            type=int,
            default=1,
            help='Display the detected images using OpenCV. This reduces FPS')
        parser.add_argument(
            '-q-size',
            '--queue-size',
            dest='queue_size',
            type=int,
            default=5,
            help='Size of the queue.')
        args = parser.parse_args()

        input_q = Queue(maxsize=args.queue_size)
        output_q = Queue(maxsize=args.queue_size)
        settings_q = Queue(maxsize=args.queue_size)
        cropped_output_q = Queue(maxsize=args.queue_size)
        inferences_q = Queue(maxsize=args.queue_size)

        if self.main.rb_ip_cam.isChecked():
            video_capture = WebcamVideoStream(
                self.main.address_cam.toPlainText(), width=args.width, height=args.height).start()
        else:
            video_capture = WebcamVideoStream(
                src=args.video_source, width=args.width, height=args.height).start()

        cap_params = {}
        frame_processed = 0
        cap_params['im_width'], cap_params['im_height'] = video_capture.size()
        print(cap_params['im_width'], cap_params['im_height'])
        cap_params['score_thresh'] = score_thresh

        print(cap_params, args)

        # Count number of files to increment new example directory
        poses = self.main.Gestures.gestures

        num_workers = 1  # TODO 4
        # spin up workers to paralleize detection.
        pool = Pool(num_workers, worker,
                    (input_q, output_q, cropped_output_q, inferences_q, cap_params, frame_processed, settings_q,
                     self.version_segm_cnn))

        start_time_millis = int(round(time.time() * 1000))
        fps = 0
        index = 0

        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        while cv2.getWindowProperty(window_name, 0) >= 0 and self.recognition_started:
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

            inferences = None

            try:
                inferences = inferences_q.get_nowait()
            except Exception as e:
                pass

            if self.settings.fpsISEnabled:
                fps = int(1000 / (int(round(time.time() * 1000)) - start_time_millis))

            # Display inferences
            if (inferences is not None):
                gui.drawInferences(inferences, poses)
                mon.monitoring(names=poses, predictions=inferences, threshold=0.7, main=self.main)
                if (self.main.cb_json.isChecked()):
                    json_sender.send_json(inferences, poses, self.main.ip_host.toPlainText(),
                                          int(self.main.port_host.toPlainText()))

            if (cropped_output is not None):
                cropped_output = cv2.cvtColor(cropped_output, cv2.COLOR_RGB2BGR)
                if (args.display > 0):
                    cv2.namedWindow('Cropped', cv2.WINDOW_NORMAL)
                    cv2.resizeWindow('Cropped', 450, 300)
                    cv2.imshow('Cropped', cropped_output)
                    # cv2.imwrite('image_' + str(num_frames) + '.png', cropped_output)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

            if (output_frame is not None):
                output_frame = cv2.cvtColor(output_frame, cv2.COLOR_RGB2BGR)
                if (args.display > 0):
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
