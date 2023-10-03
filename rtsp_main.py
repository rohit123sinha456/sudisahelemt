from infer import Infer
from api_post import API
from rtsp import RTSP
import json
if __name__=="__main__":
    inferob = Infer()
    api = API()
    f = open('camera_config.json')
    data = json.load(f)
    for camera_config in data['cameras']:
        rtspob = RTSP(inferob,api,camera_config)
        rtspob.run_threads()
    