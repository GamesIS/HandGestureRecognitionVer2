import os

import cv2
import cyrtranslit


def normalize(gesture, index):
    #gesture = cyrtranslit.to_latin(gesture, 'ru')
    print(os.listdir("Poses/"))

    poses = os.listdir('Poses/')

    if gesture != "":
        abs_path = 'Poses/' + gesture + '/' + gesture + '_' + str(index) + '/'
        files = os.listdir(abs_path)
        print(">> Working on examples : " + gesture + '_' + str(index))
        for file in files:
            if (file.endswith(".png")):
                path = abs_path + file
                # Read image
                im = cv2.imread(path)

                height, width, channels = im.shape
                if not height == width == 28:
                    if not os.path.exists('Poses_notNormalized/' + gesture + '/' + gesture + '_' + str(index) + '/'):
                        os.makedirs('Poses_notNormalized/' + gesture + '/' + gesture + '_' + str(index) + '/')
                    cv2.imwrite('Poses_notNormalized/' + gesture + '/' + gesture + '_' + str(index) + '/' + file, im)
                    # Resize image
                    im = cv2.resize(im, (28, 28), interpolation=cv2.INTER_AREA)
                    # Write image
                    cv2.imwrite(path, im)
        return


    for pose in poses:
        print(">> Working on pose : " + pose)
        subdirs = os.listdir('Poses/' + pose + '/')
        for subdir in subdirs:
            files = os.listdir('Poses/' + pose + '/' + subdir + '/')
            print(">> Working on examples : " + subdir)
            for file in files:
                if (file.endswith(".png")):
                    path = 'Poses/' + pose + '/' + subdir + '/' + file
                    # Read image
                    im = cv2.imread(path)

                    height, width, channels = im.shape
                    if not height == width == 28:
                        if not os.path.exists('Poses_notNormalized/' + pose + '/' + subdir + '/'):
                            os.makedirs('Poses_notNormalized/' + pose + '/' + subdir + '/')
                        cv2.imwrite('Poses_notNormalized/' + pose + '/' + subdir + '/' + file, im)
                        # Resize image
                        im = cv2.resize(im, (28, 28), interpolation=cv2.INTER_AREA)
                        # Write image
                        cv2.imwrite(path, im)
