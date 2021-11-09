import requests
from urllib.parse import urljoin
import os
import json

url_base = ''
url = urljoin(url_base, 'wp-json/wp/v2/media/')

user = '' # ユーザー名
password = '' # アプリケーションパスワードで発行したパスワード

filename = 'image_file/sample_01.jpeg'
file_path = os.path.join(os.getcwd(), filename)
print(file_path)
f = open(file_path, 'rb')
image_data = f.read()
f.close()

headers = {
    'Content-Type': 'image/jpeg',
    'Content-Disposition': 'attachment; filename=' + filename,
}

res = requests.post(
    url,
    data=image_data,
    headers=headers,
    auth=(user, password),
    )
res_dict = res.json()
print(json.dumps(res_dict, indent=4))
print(res_dict['source_url'])
unique_id = res_dict['id'] # アップロードした画像のID
