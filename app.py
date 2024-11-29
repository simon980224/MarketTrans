from io import BytesIO
import os
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file, abort

from service import TransactionService

# LINE Bot SDK 的相關匯入
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    # 根據需要添加其他模型
)


# 從環境變量中讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv(
    'LINE_CHANNEL_ACCESS_TOKEN', 'EKbygnyOwphN6TlaiWgnPn2pmM6HAIt1J4aGPg6wAhVGSbka391Im6byisw8F3zkjahjzk9TVWyxEp4O4OD3rw8dBgCqbKB8noTA3ELj7Z/Of67cmbphPp3CvcS9G0Urp/qVg02wKSZDe7j8JYNROAdB04t89/1O/w1cDnyilFU=')
LINE_CHANNEL_SECRET = os.getenv(
    'LINE_CHANNEL_SECRET', '84941f1ceb280db34dd751d4def5a146')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', title='首頁')


@app.route('/UserMgr', methods=['GET', 'POST'])
def UserMgr():
    return render_template('UserMgr.html', title='用戶管理')


@app.route('/Transaction', methods=['GET', 'POST'])
def Transaction():
    user_data = TransactionService.getUserData()
    return render_template('Transaction.html', title='交易明細', user_data=user_data)


@app.route('/Transaction/Transaction_query', methods=['POST'])
def Transaction_query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None
    transType = data.get('transType', '') or None

    transDatas = TransactionService.getData(
        userId, startDate, endDate, transType)
    return jsonify(transDatas=transDatas)


@app.route('/Transaction/Transaction_append', methods=['POST'])
def Transaction_append():
    data = request.json
    userId = data.get('newUserId', '').strip() or None
    amount = data.get('newAmount', '').strip() or None
    date = data.get('newDate', '').strip() or None
    transType = data.get('newTransType', '').strip() or None
    remark = data.get('newRemark', '').strip() or ''

    if not TransactionService.checkUserExists(userId):
        return jsonify(success=False, message='用戶不存在'), 400
    try:
        TransactionService.addRecord(userId, amount, date, transType, remark)
        return jsonify(success=True, message='新增成功'), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400


@app.route('/Transaction/Transaction_export', methods=['POST'])
def Transaction_export():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_requests_data = TransactionService.getData(
        userId, startDate, endDate)

    df = pd.DataFrame(trans_requests_data)

    if 'Total_Amount' in df.columns:
        df.drop(columns=['Total_Amount'], inplace=True)

    columns = {
        'Trans_Id': '交易編號',
        'User_Id': '用戶名稱',
        'Trans_Amount': '交易金額',
        'Trans_Date': '入帳日期',
        'Trans_Type': '交易類型',
        'Remark': '備註'
    }

    df.rename(columns=columns, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Transaction')

    output.seek(0)

    return send_file(output,
                     as_attachment=True,
                     download_name='Transaction.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


@app.route("/Api", methods=['POST'])
def Api():
    # 取得 LINE 發送的 X-Line-Signature 標頭
    signature = request.headers.get('X-Line-Signature')

    # 取得請求的主體
    body = request.get_data(as_text=True)

    # 驗證簽名並解析事件
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    user_id = event.source.user_id
    # app.logger.info(f"Received message from user {user_id}: {user_message}")

    if user_message == '/測試':
        response_text = f"你好"

    if user_message == '/查詢狀態':
        response_text = f"{event}"

    if user_message == '/查詢明細':
        trans_data = TransactionService.getData()[:9]
        if len(trans_data) > 0:
            response_text = "以下是您近10筆交易明細：\n\n"
            for item in trans_data:
                response_text += (
                    f"交易金額：{item['Trans_Amount']}\n"
                    f"交易日期：{item['Trans_Date']}\n"
                    f"交易類型：{item['Trans_Type']}\n"
                )
                if item.get('Remark'):
                    response_text += f"備註：{item['Remark']}\n"
                response_text += "-" * 25 + "\n"
        else:
            response_text = "沒有找到任何交易明細。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
