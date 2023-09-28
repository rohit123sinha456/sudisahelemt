import requests
with open('frame0.jpg', "rb") as img_file:
    x = requests.post('http://10.12.1.151:4002/api/v1/upload', files= {"image": img_file})
    print(x.json()['data']['filePath'])