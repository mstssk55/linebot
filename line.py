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

def remove_walk(time):
    minite = time.split("徒歩")[1]
    minite = minite.split("分")[0]
    return int(minite)

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
conditions_list = [{k:i for i,k in zip(c,conditions_list[0])} for c in conditions_list]
del conditions_list[0]
conditions_list = [i for i in conditions_list if i["配信"] == "●" ]


for p in conditions_list:
    c_kind = p["物件種別"]
    sc_list = sc_all_list[c_kind]
    sc_list_title = sc_all_title[c_kind]
    filter_col = s.filter_col[c_kind]
    if p["エリアの検索方法"] == "地域から選ぶ":
        if p["地域"] is not "":
            sc_list = [i for i in sc_list if p["地域"] in i[filter_col[0]]]
    elif p["エリアの検索方法"] == "路線から選ぶ":
        if p["路線"] is not "":
            sc_list = [i for i in sc_list if p["路線"] in i[filter_col[1]]]
            if p["駅名"] is not "":
                sc_list = [i for i in sc_list if p["駅名"] in i[filter_col[1]]]
                sc_list = [i for i in sc_list if "バス" not in i[filter_col[1]].split("」")[1]]
        if p["分数（徒歩）"] is not "":
            sc_list = [i for i in sc_list if int(p["分数（徒歩）"]) >= remove_walk(i[filter_col[1]])]
    if p["上限価格（万円）"] is not "":
        sc_list = [i for i in sc_list if int(p["上限価格（万円）"]) > remove_price(i[filter_col[2]])]
    if p["下限平米数（㎡）"] is not "":
        sc_list = [i for i in sc_list if int(p["下限平米数（㎡）"]) < remove_m(i[filter_col[3]],c_kind)]


    if len(sc_list) >0:
        send_data = [{i: k for i,k in zip(sc_list_title,s)} for s in sc_list]
        send_data = [[[i,d[i]] for i in s.send_categories[c_kind]]for d in send_data]
        # -------------------------------------------------------------------------------------------

        # 画像をLINEで送付-----------------------------------------------------------------------------

        # -------------------------------------------------------------------------------------------
        line_bot_api = LineBotApi(key.LINE_ACCESS_TOKEN)
        user_id = p["lineID"]
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        messages = TextSendMessage(text=line_send_message(user_name,send_data))
        line_bot_api.push_message(user_id, messages=messages)
