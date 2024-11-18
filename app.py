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
    userId = data.get('newUserId', '').strip() or None
    amount = data.get('newAmount', '').strip() or None
    date = data.get('newDate', '').strip() or None

    try:
        TransResponseService.addRecord(userId, amount, date)
        return '',200
    
    except Exception:
        return '',500

if __name__ == '__main__':
    app.run(debug=True)
