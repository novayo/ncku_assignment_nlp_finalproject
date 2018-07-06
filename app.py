from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import NLP_final_project
from NLP_final_project import nlp

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('T63ifAtKFwrNl7AuT3oapkrp//ntWtAO4UsL4hbRyu2o9c7APbv1iFxx3ZpbxKirybGhvDZexSk0XhYg+2y+Nxm1tymqpaJ2g1nt5Tb7ivm7lM0E9EMeH9UfKDAuiyHJXqOWSxLFiI3MUCRwRRhRzwdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('67324affddd7348cdc9023a208b51c3a')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # try 只能寫一行
    t = ''
    try:
        t = nlp(event.message.text)
    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("斷詞系統連線錯誤!"))
    message = TextSendMessage(text=t)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
