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

    def posting(self,filename):
        imgencode = ""
        x = ""
        print("reading filename",filename)
        filepath = os.path.join('.', self.image_folder, filename)
        with open(filepath, "rb") as img_file:
            x = requests.post(self.url, files= {"image": img_file})
            try:
                serverfilepath = x.json()['data']['fileName']
                msgbody = {"dept_name": "Manufacturing",
                           "camera": "Camera 1",
                           "alarm_type": "Alarm",
                           "image": serverfilepath}
                x = requests.post(self.save_url, json=msgbody)
                print(x.content)
            except:
                pass
        return x
