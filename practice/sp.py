import gspread
import json
import key as key

#ServiceAccountCredentials：Googleの各サービスへアクセスできるservice変数を生成します。
from oauth2client.service_account import ServiceAccountCredentials 

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name('', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。

#共有設定したスプレッドシートのシート1を開く
worksheet = gc.open_by_key(key.SPREADSHEET_KEY).worksheet("希望条件")


all_v = worksheet.get_all_values()
del all_v[0]
print(all_v)
#A1セルの値を受け取る
import_value = str(worksheet.acell('A1').value)
print(import_value)

# #A1セルの値に100加算した値をB1セルに表示させる
# export_value = import_value+100
# worksheet.update_cell(1,2, export_value)