from infer import Infer
from api_post import API
from rtsp import RTSP
import json
import time
if __name__=="__main__":
    inferob = Infer()
    api = API()
    f = open('camera_config.json')
    data = json.load(f)
    rtsp_object_list = []
    for camera_config in data['cameras']:
        rtspob = RTSP(inferob,api,camera_config)
        rtsp_object_list.append(rtspob)

    for rtsp_object in rtsp_object_list:
        rtsp_object.run_threads()
    
    while True:
        for rtsp_object in rtsp_object_list:
            print("Queue Thread Status :- ", rtsp_object.QueueThread.is_alive())
            print("Dequeue Thread Status :- ", rtsp_object.DequeueThread.is_alive())
        time.sleep(60)
    