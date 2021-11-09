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
    send_text +=f'{name}様のご希望の条件に近い不動産新着情報が{len(property_data)}件ございます。\n\n'
    for num,d in enumerate(property_data):
        send_text += f'【{num+1}件目】\n'
        for i in d:
            send_text += f'{i[0]}：{i[1]}\n'
        send_text += f'\n\n'
    send_text +=f'如何でしょうか。\nもしご興味ございましたら、その旨返信ください。\n詳細情報に関して担当者からご連絡させて頂きます。'
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

ws_sc_file = gc.open("2021-11-09")
sc_all_list = {}
sc_all_title = {}
for i in s.kind:
    sc_list = ws_sc_file.worksheet(i).get_all_values()
    sc_all_title[i] = sc_list[0]
    del sc_list[0]
    sc_all_list[i] = sc_list



#共有設定したスプレッドシートのシート1を開く
ws_conditions_list = gc.open_by_key(key.SPREADSHEET_KEY).worksheet("希望条件")

conditions_list = ws_conditions_list.get_all_values()
del conditions_list[0]
conditions_list = [i for i in conditions_list if i[7] == "●" ]
conditions = conditions_list[0]


sc_list = sc_all_list[conditions[1]]
sc_list_title = sc_all_title[conditions[1]]
filter_col = s.filter_col[conditions[1]]
sc_list = [i for i in sc_list if conditions[4] in i[filter_col[0]]]
sc_list = [i for i in sc_list if int(conditions[5]) > remove_price(i[filter_col[2]])]
sc_list = [i for i in sc_list if int(conditions[6]) < remove_m(i[filter_col[3]],conditions[1])]
send_data = [{i: k for i,k in zip(sc_list_title,s)} for s in sc_list]
send_data = [[[i,d[i]] for i in s.send_categories[conditions[1]]]for d in send_data]


# -------------------------------------------------------------------------------------------

# 画像をLINEで送付-----------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------
line_bot_api = LineBotApi(key.LINE_ACCESS_TOKEN)
user_id = conditions[11]
profile = line_bot_api.get_profile(user_id)
user_name = profile.display_name
messages = TextSendMessage(text=line_send_message(user_name,send_data))
line_bot_api.push_message(user_id, messages=messages)
