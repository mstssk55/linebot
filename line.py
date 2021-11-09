import setting as s
from linebot import LineBotApi
from linebot.models import TextSendMessage
import key as key
import gspread
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys


def line_send_message(name,property_data):
    send_text = f'{name}様\n\nこんにちは。\n'
    send_text +=f'{name}様のご希望の条件に近い不動産新着情報がございます。\n\n'
    for i in property_data:
        send_text += f'{i[0]}：{i[1]}\n'
    send_text +=f'\n\n如何でしょうか。\nもしご興味ございましたら、その旨返信ください。\n詳細情報に関して担当者からご連絡させて頂きます。'
    return send_text


#万円削除
def remove_price(price):
    new_p = price.rstrip("万円")
    new_p = new_p.replace(',','')
    return float(new_p)


#坪に変換
def remove_m(area,kind):
    if kind != s.kind[2]:
        new_a = area.rstrip("m²")
        new_a = new_a.rstrip("㎡")
        new_a = new_a.replace(',','')
    else:
        new_a = area.split("m²")[0]
        new_a = new_a.replace(',','')
    return float(new_a)


gauth = GoogleAuth()
gauth.credentials = key.credentials
drive = GoogleDrive(gauth)


#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(key.credentials)


#driveフォルダ内のファイル名一覧
sc_file_list = [f['title'] for f in drive.ListFile({'q': '"{}" in parents'.format(key.FOLDER_ID)}).GetList()]

ws_sc_list = gc.open("2021-11-09").worksheet("中古マンション")
sc_list = ws_sc_list.get_all_values()
sc_list_title = sc_list[0]
del sc_list[0]
print(sc_list)
sys.exit()


#共有設定したスプレッドシートのシート1を開く
ws_conditions_list = gc.open_by_key(key.SPREADSHEET_KEY).worksheet("希望条件")

conditions_list = ws_conditions_list.get_all_values()
del conditions_list[0]
conditions_list = [i for i in conditions_list if i[7] == "●" ]
conditions = conditions_list[0]



sc_list_area = [i for i in sc_list if conditions[4] in i[4]]
sc_list_price = [i for i in sc_list_area if int(conditions[5]) > remove_price(i[3])]
sc_list_m = [i for i in sc_list_price if int(conditions[6]) > remove_m(i[8],"中古マンション")]


send_data = [{i: k for i,k in zip(sc_list_title,s)} for s in sc_list_m]
send_data = send_data[0]

send_data = [[i,send_data[i]] for i in s.send_categories]



# -------------------------------------------------------------------------------------------

# 画像をLINEで送付-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
line_bot_api = LineBotApi(key.LINE_ACCESS_TOKEN)
user_id = conditions[11]
profile = line_bot_api.get_profile(user_id)
user_name = profile.display_name
messages = TextSendMessage(text=line_send_message(user_name,send_data))
line_bot_api.push_message(user_id, messages=messages)
