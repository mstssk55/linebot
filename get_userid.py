from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from dotenv import load_dotenv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import sys
load_dotenv()

line_bot_api = LineBotApi(os.getenv('GET_USER_ID'))


scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

credentials = ServiceAccountCredentials.from_json_keyfile_name('js/fc-line-59d509520a59.json', scope)
gc = gspread.authorize(credentials)
ws_conditions_list = gc.open_by_key(os.getenv('SPREADSHEET_KEY')).worksheet("ユーザーID取得（テスト）") #スプレッドシート【LINE物件情報自動通知】の"希望条件"シートを開く
conditions_list = ws_conditions_list.get_all_values()
redisterd_user_ids = ws_conditions_list.col_values(1)
print(redisterd_user_ids)


try:
    profile = line_bot_api.get_followers_ids()
    dt_now = datetime.datetime.now()
    dt_now = dt_now.strftime('%Y/%m/%d')
    users = [[i,line_bot_api.get_profile(i).display_name,dt_now] for i in profile.user_ids if i not in redisterd_user_ids]
    for i in users:
        ws_conditions_list.append_row(i)
except LineBotApiError as e:
    print("エラー")