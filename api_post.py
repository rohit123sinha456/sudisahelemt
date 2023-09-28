import requests
import yaml
import base64
class API:
    def __init__(self):
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        self.url = self.config['url']['upload']
        self.save_url = self.config['url']['save']

    def posting(self,filename):
        imgencode = ""
        x = ""
        print("reading filename",filename)
        with open(filename, "rb") as img_file:
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
