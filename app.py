from flask import Flask, render_template, request, jsonify
from service import TransRecordService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',title='首頁')

@app.route('/TransRecord', methods=['GET', 'POST'])
def TransRecord():
    return render_template('TransRecord.html',title='回款明細')

@app.route('/TransRecord/query', methods=['POST'])
def query():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    TransRecord = TransRecordService.getData(userId, startDate, endDate)
    totalAmount = TransRecordService.getTotalAmount(userId, startDate, endDate) if TransRecord is not None else 0

    records = TransRecord.to_dict(orient='records') if TransRecord is not None else []

    return jsonify(records=records, totalAmount=totalAmount)

if __name__ == '__main__':
    app.run(debug=True)
