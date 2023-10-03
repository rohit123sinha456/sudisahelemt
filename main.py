from infer import Infer
from api_post import API
import cv2
import time
import os
if __name__=="__main__":
    inferob = Infer()
    api = API()
    cap = cv2.VideoCapture('v2.mp4')
    i = 0
    while cap.isOpened():
        ret, Frame = cap.read()
        if Frame is not None:
            dets = inferob.detection(Frame)
            frames = inferob.tracking(Frame,dets)
            fnmae = "frame" + str(i) + '.jpg'
            frame_name = os.path.join('.', 'images', fnmae)
            if(frames is not None):
                cv2.imwrite(frame_name,frames)
                api.posting(fnmae)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                i +=1
        else:
            break
    cap.release()
    