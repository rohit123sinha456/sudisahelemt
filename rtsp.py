import cv2
import time
import logging
import numpy as np
import os
import queue 
import threading
import uuid


class RTSP():
    def __init__(self,Inference,API,camera_config,MaxRetries=3):
        self.inferob = Inference
        self.api = API
        self.camera_config = camera_config
        self.rtsp_url = camera_config['rtsp_url']
        self.maxretries = MaxRetries
        self.retryinterval = 30
        self.framequeue = queue.Queue()
        self.MaxCorruptFrameDuration = 30
        self.cap = None
        
    # def setup_connection(self):
        Retry = 0
        for Retry in range(self.maxretries):
            try:
                # Connect to the RTSP stream
                self.cap = cv2.VideoCapture(self.rtsp_url)
                ret, Frame = self.cap.read()
                # cv2.imwrite("hello.jpeg",Frame)
                print("In setup",ret)
                if not ret:
                    print("No video feed available. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                if not self.cap.isOpened():
                    print("Failed to Open RTSP Stream. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                    time.sleep(self.retryinterval)
                    continue
                else:
                    print("Connection Successfully Established")
                    break
                
            except Exception as e:
                logging.exception(e)
                Retry += 1
                time.sleep(self.retryinterval)
                
    
    def check_frame_corruption(self,Frame):
        AveragePixelValue = np.mean(Frame)
        CorruptThreshold = 10
        return AveragePixelValue < CorruptThreshold



    def enqueue_frame_buffer(self):
        print("Reading and Enqueing Frames")
        print("Capture Status",self.cap.isOpened())
        while True:
            CorruptFrameStartTime = None
            try:
                ret, Frame = self.cap.read()
            except:
                print("Problem in reading Frames")
                
            if not ret:
                print("No video feed available")
                break
                
            # Handling Corrupt Frames
            if self.check_frame_corruption(Frame):
                if CorruptFrameStartTime is None:
                    CorruptFrameStartTime = time.time()
                elif (time.time() - CorruptFrameStartTime) >= self.MaxCorruptFrameDuration:
                    print("Corrupt frames received")
                    break
            # Enqueue the frame for saving
            try:
                self.framequeue.put(Frame)
            except:
                print("Problem with pusing to queue")
            
    def dequeue_frame_buffer(self):
        while True:
            try:
                Frame = self.framequeue.get()
                if Frame is not None:
                    dets = self.inferob.detection(Frame)
                    frames = self.inferob.tracking(Frame,dets)
                    i = uuid.uuid4()
                    fnmae = "frame" + str(i) + '.jpg'
                    frame_name = os.path.join('.', 'images', fnmae)
                    print("Frame processing Done")
                    
                    if(frames is not None):
                        cv2.imwrite(frame_name,frames)
                        self.api.posting(fnmae,self.camera_config)
                        print("Frame posting done")

            except:
                print("Error in getting and running AI model")

    def run_threads(self):
        QueueThread = threading.Thread(target=self.enqueue_frame_buffer)
        DequeueThread = threading.Thread(target=self.dequeue_frame_buffer)
        DequeueThread.daemon = True
        QueueThread.daemon = True
        QueueThread.start()
        DequeueThread.start()
        while True:
            print("Queue Thread Status :- ", QueueThread.is_alive())
            print("Dequeue Thread Status :- ", DequeueThread.is_alive())
            time.sleep(60)