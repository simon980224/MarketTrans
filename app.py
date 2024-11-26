from io import BytesIO

import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file

from service import TransRequestsService,TransResponseService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='首頁')

@app.route('/TransRequests', methods=['GET', 'POST'])
def TransRequests():
    user_data = TransRequestsService.getUserData()
    return render_template('TransRequests.html', title='用戶管理', user_data=user_data)

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

if __name__ == '__main__':
    app.run(debug=True)
