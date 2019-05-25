import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def drawInferences(values, names):
    nb_classes = len(values)
    left_margin = 200
    margin = 50
    thickness = 40

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    fontColor = (255, 255, 255)
    lineType = 2

    b, g, r, a = 0, 255, 0, 0
    ## Use simsum.ttc to write Chinese.
    fontpath = "simsun.ttf"
    font = ImageFont.truetype(fontpath, 26)

    blank = np.zeros((600, 600, 3), np.uint8)

    for i in range(nb_classes):
        if (values[i] > 0.7):
            cv2.rectangle(blank, (left_margin, margin + int(margin * i)),
                          (left_margin + int(values[i] * 200), margin + thickness + int(margin * i)), (0, 255, 0), -1)
        else:
            cv2.rectangle(blank, (left_margin, margin + int(margin * i)),
                          (left_margin + int(values[i] * 200), margin + thickness + int(margin * i)), (255, 0, 0), -1)

        img_pil = Image.fromarray(blank)
        draw = ImageDraw.Draw(img_pil)
        draw.text((0, margin + int(margin * (i)) + int(thickness / 2) - 10), names[i], font=font, fill=(b, g, r, a))
        blank = np.array(img_pil)
        #cv2.putText(blank, names[i], (0, margin + int(margin * i) + int(thickness / 2)), cv2.FONT_HERSHEY_SIMPLEX, fontScale, fontColor,
        #            lineType)
        try:
            cv2.putText(blank, str(values[i]), (left_margin + 200, margin + int(margin * i) + int(thickness / 2)), cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale, fontColor, lineType)
        except Exception as e:
            print(e)

    cv2.imshow("Inferences", blank)