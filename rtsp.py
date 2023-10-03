import cv2
import time
import logging
import numpy as np
import os
import queue 
import threading


class RTSP():
    def __init__(self,Inference,API,RTSP_URL,MaxRetries=3):
        self.inferob = Inference
        self.api = API
        self.rtsp_url = RTSP_URL
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
                cv2.imwrite("hello.jpeg",Frame)
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
                    print("Corrupt frames received for over {} seconds. Retry (Retry {}/{})".format(MaxCorruptFrameDuration, Retry + 1, MaxRetries))
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
                    print("Frame is OK")
                    dets = self.inferob.detection(Frame)
                    print("Detection Frame")
                    frames = self.inferob.tracking(Frame,dets)
                    print("tracking Frame")
                    
                    fnmae = "frame" + str(i) + '.jpg'
                    print("Frame processing Done")
                    
                    if(frames is not None):
                        cv2.imwrite(fnmae,frames)
                        self.api.posting(fnmae)
            except:
                print("Error in getting and running AI model")

    def run_threads(self):
        QueueThread = threading.Thread(target=self.enqueue_frame_buffer)
        DequeueThread = threading.Thread(target=self.dequeue_frame_buffer)
        # DequeueThread.daemon = True
        QueueThread.daemon = True
        QueueThread.start()
        DequeueThread.start()