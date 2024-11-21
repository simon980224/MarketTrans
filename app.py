from io import BytesIO

import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file

from service import TransResponseService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='首頁')

@app.route('/TransResponse', methods=['GET', 'POST'])
def TransResponse():
    user_data = TransResponseService.getUserData()
    return render_template('TransResponse.html', title='回款明細', user_data=user_data)

@app.route('/TransResponse/query', methods=['POST'])
def query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    trans_response_data = TransResponseService.getData(userId, startDate, endDate)
    return jsonify(trans_response_data=trans_response_data)

@app.route('/TransResponse/append', methods=['POST'])
def append():
    data = request.json
    userId = data.get('newUserId', '').strip() or None
    amount = data.get('newAmount', '').strip() or None
    date = data.get('newDate', '').strip() or None

    try:
        TransResponseService.addRecord(userId, amount, date)
        # raise Exception('測試用例: 新增失敗')
        return jsonify(success=True,message='明細新增成功'), 200
    
    except Exception as e:
        return jsonify(success=False, message=str(e)), 400

@app.route('/TransResponse/export', methods=['POST'])
def export():
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
