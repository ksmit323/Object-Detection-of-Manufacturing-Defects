import sys
import numpy as np
import cv2

def click_callback(event, x, y, flags, params):
    global cap
    if event == cv2.EVENT_LBUTTONDOWN:
        try:
            cap.release()
        except:
            print("")
        cv2.destroyAllWindows()
        exit()

def show_error(msg):
    print(msg)
window_name = "View Camera"
cv2.namedWindow(window_name)
cv2.moveWindow(window_name, 40,30)
cv2.setMouseCallback(window_name, click_callback)

camera_to_use = int(0)
cap = cv2.VideoCapture(camera_to_use)
font = cv2.FONT_HERSHEY_SIMPLEX

if cap is None or not cap.isOpened():

    text = "No Camera Detected"
    textsize = cv2.getTextSize(text, font, 1, 2)[0]

    text2 = "Please connect camera and restart the app"
    textsize2 = cv2.getTextSize(text2, font, 0.5, 1)[0]

    while(True):
        frame = np.zeros((480,640))
        # get coords based on boundary
        textX = int((frame.shape[1] - textsize[0]) / 2)
        textY = int((frame.shape[0] + textsize[1]) / 2)

        textX2 = int((frame.shape[1] - textsize2[0]) / 2)
        textY2 = int((frame.shape[0] + textsize2[1]) / 2) + 50

        cv2.putText(frame, text, (textX, textY ), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, text2, (textX2, textY2 ), font, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, "Click anywhere on this window to exit.", (10,20), font, 0.5, (255, 255, 255), 1)
        cv2.imshow(window_name,frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
else:
    #camera is good
    while(True):
        ret, frame = cap.read()
        cv2.putText(frame, "Click anywhere on the video to exit.", (10,20), font, 0.5, (255, 255, 255), 1)
        cv2.imshow(window_name,frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
