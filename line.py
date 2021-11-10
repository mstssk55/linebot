import setting as s
from linebot import LineBotApi
from linebot.models import TextSendMessage
import key as key
import gspread
import json
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import sys
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors



# ---------------------------------------------------------------------------------------------------------------

# 関数設定

# ---------------------------------------------------------------------------------------------------------------


# 【mail通知】メール本文の作成
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': encode_message.decode()}

# 【mail通知】メール送信の実行
def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        # print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)

# 【LINE・MAIL共通】メール本文作成
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


#【物件情報検索】万円削除
def remove_price(price):
    new_p = price.rstrip("万円")
    new_p = new_p.replace(',','')
    return float(new_p)


#【物件情報検索】㎡削除
def remove_m(area,kind):
    if kind != s.kind[2]:
        new_a = area.rstrip("m²")
        new_a = new_a.rstrip("㎡")
        new_a = new_a.replace(',','')
    else:
        new_a = area.split("m²")[0]
        new_a = new_a.replace(',','')
    return float(new_a)

#【物件情報検索】分の取得
def remove_walk(time):
    minite = time.split("徒歩")[1]
    minite = minite.split("分")[0]
    return int(minite)

# ---------------------------------------------------------------------------------------------------------------

# 関数設定ここまで

# ---------------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------------

# 処理開始

# ---------------------------------------------------------------------------------------------------------------

#【google apiの設定】
gauth = GoogleAuth()
gauth.credentials = key.credentials
drive = GoogleDrive(gauth)
gc = gspread.authorize(key.credentials) #OAuth2の資格情報を使用してGoogle APIにログインします。

#driveフォルダ内のファイル名一覧取得
sc_file_list = [f['title'] for f in drive.ListFile({'q': '"{}" in parents'.format(key.FOLDER_ID)}).GetList()]

#該当ファイルの物件情報取得
ws_sc_file = gc.open("2021-11-09")#該当ファイルを開く
sc_all_list = {} #物件情報を格納するリスト
sc_all_title = {} #物件情報のキー格納
for i in s.kind: #種類別に物件情報を格納
    sc_list = ws_sc_file.worksheet(i).get_all_values()
    sc_all_title[i] = sc_list[0]
    del sc_list[0]
    sc_all_list[i] = sc_list

#ユーザーの希望条件リストを習得
ws_conditions_list = gc.open_by_key(key.SPREADSHEET_KEY).worksheet("希望条件") #スプレッドシート【LINE物件情報自動通知】の"希望条件"シートを開く
conditions_list = ws_conditions_list.get_all_values() #希望条件シートの全データ取得
conditions_list = [{k:i for i,k in zip(c,conditions_list[0])} for c in conditions_list] #辞書型に変換
del conditions_list[0] #1行目削除
conditions_list = [i for i in conditions_list if i["配信"] == "●" ] #配信設定しているものだけにフィルター

#配信希望ユーザーが1人以上の場合実行
if len(conditions_list) > 0:
    #ユーザーの希望条件リストの数だけ繰り返し
    for p in conditions_list:
        print(f'{p["お客様名"]}様の希望物件検索を開始します。')
        #変数の設定
        c_kind = p["物件種別"] #物件種別
        sc_list = sc_all_list[c_kind] #物件種別の物件情報一覧
        sc_list_title = sc_all_title[c_kind] #物件情報一覧のキー
        filter_col = s.filter_col[c_kind] #物件情報のインデックス番号

        #希望条件でフィルター---------------------------------------------------------------------------------------

        #エリアの検索方法で分岐
        #地域から選ぶ場合
        print(f'{c_kind}の物件情報は{len(sc_list)}件です')
        if p["エリアの検索方法"] == "地域から選ぶ":
            if p["地域"] is not "": #地域が空白じゃなければ
                print(f'エリアを地域から検索します。')
                sc_list = [i for i in sc_list if p["地域"] in i[filter_col[0]]]
                print(f'{p["地域"]}に該当する物件は{len(sc_list)}件でした。')
            else:
                print(f'エリアの条件設定はありません。')
        #路線から選ぶ場合
        elif p["エリアの検索方法"] == "路線から選ぶ":
            if p["路線"] is not "": #路線が空白じゃなければ
                print(f'エリアを路線から検索します。')
                sc_list = [i for i in sc_list if p["路線"] in i[filter_col[1]]]
                print(f'{p["路線"]}に該当する物件は{len(sc_list)}件でした。')
                if p["駅名"] is not "":
                    print(f'駅名で絞り込みをします。')
                    sc_list = [i for i in sc_list if p["駅名"] in i[filter_col[1]]]
                    sc_list = [i for i in sc_list if "バス" not in i[filter_col[1]].split("」")[1]]
                    print(f'{p["駅名"]}に該当する物件は{len(sc_list)}件でした。')
                else:
                    print(f'駅名の条件設定はありません。')
            else:
                print(f'路線の条件設定はありません。')
            if p["分数（徒歩）"] is not "":
                print(f'駅までの分数で絞り込みをします。')
                sc_list = [i for i in sc_list if int(p["分数（徒歩）"]) >= remove_walk(i[filter_col[1]])]
                print(f'徒歩{p["分数（徒歩）"]}以内に該当する物件は{len(sc_list)}件でした。')
            else:
                print(f'分数の条件設定はありません。')

        #上限価格でフィルター
        if p["上限価格（万円）"] is not "":
            print(f'上限価格で検索します。')
            sc_list = [i for i in sc_list if int(p["上限価格（万円）"]) > remove_price(i[filter_col[2]])]
            print(f'{p["上限価格（万円）"]}万円以下に該当する物件は{len(sc_list)}件でした。')
        else:
            print(f'上限価格の条件設定はありません。')

        #下限平米数でフィルター
        if p["下限平米数（㎡）"] is not "":
            print(f'下限平米数で検索します。')
            sc_list = [i for i in sc_list if int(p["下限平米数（㎡）"]) < remove_m(i[filter_col[3]],c_kind)]
            print(f'{p["下限平米数（㎡）"]}㎡以上に該当する物件は{len(sc_list)}件でした。')
        else:
            print(f'下限平米数の条件設定はありません。')
        #希望条件でフィルタここまでー---------------------------------------------------------------------------------------

        #条件に合致する物件があるか確認
        if len(sc_list) >0:
            print(f'希望条件に合致する物件が{len(sc_list)}件ありました')
            send_data = [{i: k for i,k in zip(sc_list_title,s)} for s in sc_list]
            send_data = [[[i,d[i]] for i in s.send_categories[c_kind]]for d in send_data]

            #配信方法で分岐

            #LINEの場合
            if p["配信方法"] == "LINE":
                if p["lineID"]:
                # -------------------------------------------------------------------------------------------
                # LINEで送付----------------------------------------------------------------------------------
                # -------------------------------------------------------------------------------------------
                    line_bot_api = LineBotApi(key.LINE_ACCESS_TOKEN)
                    user_id = p["lineID"]
                    profile = line_bot_api.get_profile(user_id)
                    user_name = profile.display_name
                    messages = TextSendMessage(text=line_send_message(user_name,send_data))
                    line_bot_api.push_message(user_id, messages=messages)
                    print(f'{len(sc_list)}件の物件情報を{p["お客様名"]}様にLINEで送付しました')
                # -------------------------------------------------------------------------------------------
                # LINEで送付ここまで---------------------------------------------------------------------------
                # -------------------------------------------------------------------------------------------
                else:
                    print(f'{p["お客様名"]}様のLINE IDが設定されていません。')

            #MAILの場合
            elif p["配信方法"] == "MAIL":
                if p["mail"]:
                # -------------------------------------------------------------------------------------------
                # MAILで送付----------------------------------------------------------------------------------
                # -------------------------------------------------------------------------------------------
                    creds = None
                    if os.path.exists('token.pickle'):
                        with open('token.pickle', 'rb') as token:
                            creds = pickle.load(token)
                    if not creds or not creds.valid:
                        if creds and creds.expired and creds.refresh_token:
                            creds.refresh(Request())
                        else:
                            flow = InstalledAppFlow.from_client_secrets_file(
                                'js/credentials.json', key.SCOPES)
                            creds = flow.run_local_server()
                        with open('token.pickle', 'wb') as token:
                            pickle.dump(creds, token)
                    service = build('gmail', 'v1', credentials=creds)
                    # 6. メール本文の作成
                    sender = 'm.tobcreation@gmail.com'
                    to = p["mail"]
                    subject = '希望条件に近い不動産情報が見つかりました。'
                    message_text = line_send_message(p["お客様名"],send_data)
                    message = create_message(sender, to, subject, message_text)
                    # 7. Gmail APIを呼び出してメール送信
                    send_message(service, 'me', message)
                    print(f'{len(sc_list)}件の物件情報を{p["お客様名"]}様にMAILで送付しました')
                # -------------------------------------------------------------------------------------------
                # MAILで送付ここまで---------------------------------------------------------------------------
                # -------------------------------------------------------------------------------------------
                else:
                    print(f'{p["お客様名"]}様のMAILアドレスが設定されていません。')

            else:
                print(f'{p["お客様名"]}様の配信方法が設定されていません。')
        else:
            print(f'{p["お客様名"]}様の希望に合致する物件がありませんでした。')
else:
    print("配信希望ユーザーがいませんでした。物件情報自動通知処理を終了します。")
