import os
import threading

import cv2
import numpy as np
import tensorflow as tf
import normalize as nm
from PIL import ImageFont, ImageDraw, Image

from utils import detector_utils as detector_utils


def main(gestureName, version_cnn):
    name_pose = gestureName
    currentPath = ''
    currentExample = ''

    # Count number of files to increment new example directory
    if not os.path.exists('Poses/' + gestureName + '/'):
        os.makedirs('Poses/' + gestureName + '/')
    subdirs = os.listdir('Poses/' + gestureName + '/')
    index = len(subdirs) + 1

    # Create new example directory
    if not os.path.exists('Poses/' + gestureName + '/' + gestureName + '_' + str(index) + '/'):
        os.makedirs('Poses/' + gestureName + '/' + gestureName + '_' + str(index) + '/')

        # Update current path
        currentPath = 'Poses/' + gestureName + '/' + gestureName + '_' + str(index) + '/'
        currentExample = gestureName + '_' + str(index) + '_'

    print('You\'ll now be prompted to record the pose you want to add. \n \
                Please place your hand beforehand facing the camera, and press any key when ready. \n \
                When finished press \'q\'.')
    # Begin capturing
    cap = cv2.VideoCapture(0)
    #cap = cv2.VideoCapture('http://192.168.0.84:8080/video')


    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(currentPath + name_pose + '.avi', fourcc, 25.0, (width, height))

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret:
            # write the frame
            out.write(frame)

            b, g, r, a = 0, 0, 255, 0
            ## Use simsum.ttc to write Chinese.
            fontpath = "simsun.ttf"
            font = ImageFont.truetype(fontpath, 32)
            img_pil = Image.fromarray(frame)
            draw = ImageDraw.Draw(img_pil)
            draw.text((10, 10), "Нажмите Q чтобы завершить процесс", font=font, fill=(b, g, r, a))
            frame = np.array(img_pil)

            #TODO НАЖМИТЕ Q чтобы завершить процесс
            cv2.imshow('frame', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    thread1 = threading.Thread(target=start_create_imgs, args=(currentPath, name_pose, currentExample, gestureName, index, version_cnn))
    thread1.start()

def start_create_imgs(currentPath, name_pose, currentExample, gestureName, index, version_cnn):
    vid = cv2.VideoCapture(currentPath + name_pose + '.avi')

    # Check if the video
    if (not vid.isOpened()):
        print('Error opening video stream or file')
        return

    print('>> loading frozen model..')
    detection_graph, sess = detector_utils.load_inference_graph(version_cnn)
    sess = tf.Session(graph=detection_graph)
    print('>> model loaded!')

    _iter = 1
    # Read until video is completed
    while (vid.isOpened()):
        # Capture frame-by-frame
        ret, frame = vid.read()
        if ret:
            print('   Processing frame: ' + str(_iter))
            # Resize and convert to RGB for NN to work with
            # frame = cv2.resize(frame, (320, 180), interpolation=cv2.INTER_AREA)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect object
            boxes, scores = detector_utils.detect_objects(frame, detection_graph, sess)

            # get region of interest
            res = detector_utils.get_box_image(1, 0.2, scores, boxes, 640, 480, frame)

            # Save cropped image 
            if (res is not None):
                cv2.imwrite(currentPath + currentExample + str(_iter) + '.png', cv2.cvtColor(res, cv2.COLOR_RGB2BGR))

            _iter += 1
        # Break the loop
        else:
            break

    print('   Processed ' + str(_iter) + ' frames!')

    vid.release()
    nm.normalize(gestureName, index)


if __name__ == '__main__':
    main()
