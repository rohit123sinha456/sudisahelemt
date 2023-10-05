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
        self.img_folder = camera_config['camera']
        self.maxretries = MaxRetries
        self.retryinterval = 30
        self.framequeue = queue.Queue()
        self.MaxCorruptFrameDuration = 30
        self.cap = None
        logging.basicConfig(filename=os.path.join('.', 'logs', 'rtsp.log'),format='%(asctime)s:%(levelname)s: %(message)s')
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)
    # def setup_connection(self):
        Retry = 0
        for Retry in range(self.maxretries):
            try:
                # Connect to the RTSP stream
                self.cap = cv2.VideoCapture(self.rtsp_url)
                ret, Frame = self.cap.read()
                # cv2.imwrite("hello.jpeg",Frame)
                # print("In setup",ret)
                if not ret:
                    logging.info("No video feed available. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                if not self.cap.isOpened():
                    logging.info("Failed to Open RTSP Stream. Retrying in {} seconds (Retry {}/{})".format(self.retryinterval, Retry + 1, self.maxretries))
                    time.sleep(self.retryinterval)
                    continue
                else:
                    logging.info("Connection Successfully Established")
                    break
                
            except Exception as e:
                logging.warning(e)
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
                logging.warning("Problem in reading Frames")
                
            if not ret:
                logging.warning("No video feed available")
                break
                
            # Handling Corrupt Frames
            if self.check_frame_corruption(Frame):
                if CorruptFrameStartTime is None:
                    CorruptFrameStartTime = time.time()
                elif (time.time() - CorruptFrameStartTime) >= self.MaxCorruptFrameDuration:
                    logging.warning("Corrupt frames received")
                    break
            # Enqueue the frame for saving
            try:
                self.framequeue.put(Frame)
            except:
                logging.warning("Problem with pusing to queue")
            
    def dequeue_frame_buffer(self):
        while True:
            try:
                Frame = self.framequeue.get()
                if Frame is not None:
                    dets = self.inferob.detection(Frame)
                    frames = self.inferob.tracking(Frame,dets)
                    i = uuid.uuid4()
                    fnmae = "frame" + str(i) + '.jpg'
                    frame_name = os.path.join('.', self.img_folder, fnmae)
                    # print("Frame processing Done")
                    
                    if(frames is not None):
                        logging.info("Sending Image")
                        cv2.imwrite(frame_name,frames)
                        self.api.posting(frame_name,self.camera_config)
                        logging.info("Frame posting done")

            except:
                logging.warning("Error in getting and running AI model")

    def run_threads(self):
        self.QueueThread = threading.Thread(target=self.enqueue_frame_buffer)
        self.DequeueThread = threading.Thread(target=self.dequeue_frame_buffer)
        self.DequeueThread.daemon = True
        self.QueueThread.daemon = True
        self.QueueThread.start()
        self.DequeueThread.start()
        # print("Queue Thread Status :- ", QueueThread.is_alive())
        # print("Dequeue Thread Status :- ", DequeueThread.is_alive())
        # while True:
        #     print("Queue Thread Status :- ", QueueThread.is_alive())
        #     print("Dequeue Thread Status :- ", DequeueThread.is_alive())
        #     time.sleep(60)