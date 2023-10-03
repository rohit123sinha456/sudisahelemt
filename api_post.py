import requests
import yaml
import os
class API:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.url = self.config['url']['upload']
        self.save_url = self.config['url']['save']
        self.image_folder = self.config['output']['folder']

    def posting(self,filename,camera_config):
        imgencode = ""
        x = ""
        print("reading filename",filename)
        filepath = os.path.join('.', self.image_folder, filename)
        with open(filepath, "rb") as img_file:
            x = requests.post(self.url, files= {"image": img_file})
            try:
                serverfilepath = x.json()['data']['fileName']
                msgbody = {"dept_name": camera_config['dept_name'],
                           "camera": camera_config['camera'],
                           "alarm_type": camera_config['alarm_type'],
                           "image": serverfilepath}
                x = requests.post(self.save_url, json=msgbody)
                print(x.content)
            except:
                pass
        return x
