from bs4 import BeautifulSoup
import setting as s
import pdfkit, os
from pathlib import Path
from pdf2image import convert_from_path
import requests
from urllib.parse import urljoin
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models.send_messages import ImageSendMessage
import key as key

def pdf(data):
    insert = ''
    for i in data:
        insert += '<p>'+i+'</p>'
    return pdfkit.from_string(
        '<!DOCTYPE html>'
        '<html lang="ja">'
        '<head>'
        '<meta charset="utf-8"/>'
        '</head>'
        '<body>'
        +insert+
        '</body>'
        '</html>',
        'sample.pdf')



# -------------------------------------------------------------------------------------------

# ダウンロードしたhtmlファイルをスクレイピング------------------------------------------------------

# -------------------------------------------------------------------------------------------

soup = BeautifulSoup(open('aaaa.html'),'html.parser')
property_info = [soup.select_one(i[1]).text.strip() for i in s.detail_selector_list]

# -------------------------------------------------------------------------------------------

# スクレイピング情報をPDF化----------------------------------------------------------------------

# -------------------------------------------------------------------------------------------

pdf(property_info)


# -------------------------------------------------------------------------------------------

# PDFを画像に変換------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------


# PDFファイルのパス
pdf_path = Path("sample.pdf")

# PDF -> Image に変換（150dpi）
pages = convert_from_path(str(pdf_path), 150)

# 画像ファイルを１ページずつ保存
image_dir = Path("./image_file")
for i, page in enumerate(pages):
    file_name = pdf_path.stem + "_{:02d}".format(i + 1) + ".jpeg"
    image_path = image_dir / file_name
    # JPEGで保存
    page.save(str(image_path), "JPEG")

# -------------------------------------------------------------------------------------------

# 画像をサーバーにアップ（wordpress経由)----------------------------------------------------------

# -------------------------------------------------------------------------------------------


url_base = key.WP_URL #WPのURL
url = urljoin(url_base, 'wp-json/wp/v2/media/')
user = key.WP_USER
password = key.WP_PASS

filename = 'image_file/sample_01.jpeg'
file_path = os.path.join(os.getcwd(), filename)
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
image_url = res_dict['source_url']

# -------------------------------------------------------------------------------------------

# 画像をLINEで送付-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
line_bot_api = LineBotApi(key.LINE_ACCESS_TOKEN)

user_id = key.LINE_USER_ID
profile = line_bot_api.get_profile(user_id)
user_name = profile.display_name
# messages = TextSendMessage(text=f"こんにちは😁\n\n"
#                                 f"最近はいかがお過ごしでしょうか?"+user_name)
messages = ImageSendMessage(
    original_content_url=image_url,
    preview_image_url=image_url
)
line_bot_api.push_message(user_id, messages=messages)
