from infer import Infer
from api_post import API
from rtsp import RTSP
import json
import time
from threading import Event
import os
if __name__=="__main__":
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    inferob = Infer()
    api = API()
    f = open('camera_config.json')
    data = json.load(f)
    rtsp_object_list = []
    for camera_config in data['cameras']:
        rtspob = RTSP(inferob,api,camera_config)
        rtspobevent = Event()
        rtsp_object_list.append([rtspob,rtspobevent,camera_config])

    for rtsp_object,rtspobevent,_ in rtsp_object_list:
        rtsp_object.run_threads(rtspobevent)
    
    while True:
        for rtsp_object,rtspob_event,camera_config in rtsp_object_list:
            print(rtsp_object.framequeue.qsize())
            print("Queue Thread Status :- ", rtsp_object.QueueThread.is_alive())
            if(rtsp_object.QueueThread.is_alive() == False):
                print("killing Dequeue")
                rtspob_event.set()
                # rtsp_object.DequeueThread.join()
                print("GC Object")
                # rtsp_object_list.remove(rtsp_object)
                print("Creating New object")
                rtspob = RTSP(inferob,api,camera_config)
                rtspobevent = Event()
                print("Running Threads")
                rtspob.run_threads(rtspobevent)
                print("appending object")
                rtsp_object_list.append([rtspob,rtspobevent,camera_config])

            # print("Dequeue Thread Status :- ", rtsp_object.DequeueThread.is_alive())
            # if(rtsp_object.DequeueThread.is_alive() == False):
            #     print("killing EnQueue")
            #     rtspob_event.set()
            #     rtsp_object.QueueThread.join()
            #     print("GC Object")
            #     # rtsp_object_list.remove(rtsp_object)
            #     print("Creating New object")
            #     rtspob = RTSP(inferob,api,camera_config)
            #     rtspobevent = Event()
            #     print("Running Threads")
            #     rtspob.run_threads(rtspobevent)
            #     print("appending object")
            #     rtsp_object_list.append([rtspob,rtspobevent,camera_config])
            
        time.sleep(60)
    