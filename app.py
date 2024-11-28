from io import BytesIO
import os
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file, abort

from service import TransRequestsService, TransResponseService

# LINE Bot SDK 的相關匯入
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    # 根據需要添加其他模型
)

app = Flask(__name__)

# 從環境變量中讀取憑證
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'EKbygnyOwphN6TlaiWgnPn2pmM6HAIt1J4aGPg6wAhVGSbka391Im6byisw8F3zkjahjzk9TVWyxEp4O4OD3rw8dBgCqbKB8noTA3ELj7Z/Of67cmbphPp3CvcS9G0Urp/qVg02wKSZDe7j8JYNROAdB04t89/1O/w1cDnyilFU=')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '84941f1ceb280db34dd751d4def5a146')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route('/')
def index():
    return render_template('index.html', title='首頁')

@app.route('/UserMgr', methods=['GET', 'POST'])
def UserMgr():
    # user_data = TransRequestsService.getUserData()
    return render_template('UserMgr.html', title='用戶管理')

@app.route('/TransRequests', methods=['GET', 'POST'])
def TransRequests():
    user_data = TransRequestsService.getUserData()
    return render_template('TransRequests.html', title='入帳明細', user_data=user_data)

@app.route('/TransRequests/TransRequests_query', methods=['POST'])
def TransRequests_query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_requests_data = TransRequestsService.getData(userId, startDate, endDate)
    return jsonify(trans_requests_data=trans_requests_data)

@app.route('/TransRequests/TransRequests_append', methods=['POST'])
def TransRequests_append():
    data = request.json
    userId = data.get('newUserId', '').strip() or None
    amount = data.get('newAmount', '').strip() or None
    date = data.get('newDate', '').strip() or None
    remark = data.get('newRemark', '').strip() or ''
    if not TransRequestsService.checkUserExists(userId):
        return jsonify(success=False, message='用戶不存在'), 400
    try:
        TransRequestsService.addRecord(userId, amount, date, remark)
        return jsonify(success=True, message='新增成功'), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/TransRequests/TransRequests_export', methods=['POST'])
def TransRequests_export():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_requests_data = TransRequestsService.getData(userId, startDate, endDate)
    
    df = pd.DataFrame(trans_requests_data)

    if 'Total_Amount' in df.columns:
        df.drop(columns=['Total_Amount'], inplace=True)
    
    columns = {
        'Trans_Id': '交易編號',
        'User_Id': '用戶名稱',
        'Trans_Amount': '回款金額',
        'Trans_Date': '回款日期',
    }

    df.rename(columns=columns, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='TransRequests')

    output.seek(0)
    
    return send_file(output, 
                     as_attachment=True, 
                     download_name='TransRequests.xlsx', 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/TransResponse', methods=['GET', 'POST'])
def TransResponse():
    user_data = TransResponseService.getUserData()
    return render_template('TransResponse.html', title='回款明細', user_data=user_data)

@app.route('/TransResponse/TransResponse_query', methods=['POST'])
def TransResponse_query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_response_data = TransResponseService.getData(userId, startDate, endDate)
    return jsonify(trans_response_data=trans_response_data)

@app.route('/TransResponse/TransResponse_append', methods=['POST'])
def TransResponse_append():
    data = request.json
    userId = data.get('newUserId', '').strip() or None
    amount = data.get('newAmount', '').strip() or None
    date = data.get('newDate', '').strip() or None
    remark = data.get('newRemark', '').strip() or ''

    if not TransResponseService.checkUserExists(userId):
        return jsonify(success=False, message='用戶不存在'), 400

    try:
        TransResponseService.addRecord(userId, amount, date, remark)
        return jsonify(success=True, message='新增成功'), 200
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/TransResponse/TransResponse_export', methods=['POST'])
def TransResponse_export():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_response_data = TransResponseService.getData(userId, startDate, endDate)
    
    df = pd.DataFrame(trans_response_data)

    if 'Total_Amount' in df.columns:
        df.drop(columns=['Total_Amount'], inplace=True)
    
    columns = {
        'Trans_Id': '交易編號',
        'User_Id': '用戶名稱',
        'Trans_Amount': '回款金額',
        'Trans_Date': '回款日期',
    }

    df.rename(columns=columns, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='TransResponse')

    output.seek(0)
    
    return send_file(output, 
                     as_attachment=True, 
                     download_name='TransResponse.xlsx', 
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
    app.logger.info(f"Received message from user {user_id}: {user_message}")

    if user_message == '/測試':
    # 回傳event結構
        response_text = f"您的 event 是 {event}"

    if user_message == '/查詢回款':
        trans_data = TransResponseService.getData()
        if not trans_data:
            response_text = "沒有找到任何回款紀錄。"
        else:
            # 建立回應訊息
            response_text = "以下是您的回款明細：\n\n"
            for item in trans_data:
                response_text += (
                    f"回款金額：{item['Trans_Amount']}\n"
                    f"回款日期：{item['Trans_Date']}\n"
                )
                if item.get('Remark'):
                    response_text += f"備註：{item['Remark']}\n"
                response_text += "-" * 27 + "\n"
    
    # else:
    #     response_text = "抱歉，我無法理解您的指令。請使用 '/查詢回款' 來查詢回款明細。"

    # 使用 LINE Messaging API 發送回應
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response_text)
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
