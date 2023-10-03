from infer import Infer
from api_post import API
from rtsp import RTSP
if __name__=="__main__":
    inferob = Infer()
    api = API()
    rtspob = RTSP(inferob,api,"rtsp://admin:Sheraton123@10.111.111.106:554/Streaming/Channels/501/")
    rtspob.run_threads()
    