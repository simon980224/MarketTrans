from flask import Flask, render_template, request, jsonify
from service import TransResponseService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='首頁')

@app.route('/TransResponse', methods=['GET', 'POST'])
def TransResponse():
    return render_template('TransResponse.html', title='回款明細')

@app.route('/TransResponse/query', methods=['POST'])
def query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    TransResponse = TransResponseService.getData(userId, startDate, endDate)

    records = TransResponse.to_dict(orient='records') if TransResponse is not None else []

    return jsonify(records=records)

@app.route('/TransResponse/append', methods=['POST'])
def append():
    data = request.json
    print('data:', data)
    
    # 假設這裡有一些處理邏輯，比如將數據插入到數據庫中
    try:
        # TODO: 實現數據插入或其他邏輯
        # 例如: TransResponseService.addRecord(data['newUserId'], data['newAmount'], data['newDate'])
        
        # 返回成功響應
        return jsonify({'status': 'success', 'message': 'Record added successfully'})
    except Exception as e:
        # 返回失敗響應
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
