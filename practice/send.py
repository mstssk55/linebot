from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.models.send_messages import ImageSendMessage

# リモートリポジトリに"ご自身のチャネルのアクセストークン"をpushするのは、避けてください。
# 理由は、そのアクセストークンがあれば、あなたになりすまして、プッシュ通知を送れてしまうからです。
LINE_CHANNEL_ACCESS_TOKEN = ""

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)


user_id = ""
profile = line_bot_api.get_profile(user_id)
user_name = profile.display_name
# messages = TextSendMessage(text=f"こんにちは😁\n\n"
#                                 f"最近はいかがお過ごしでしょうか?"+user_name)
messages = ImageSendMessage(
    original_content_url='',
    preview_image_url=''
)
line_bot_api.push_message(user_id, messages=messages)
