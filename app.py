from flask import Flask, render_template, request, jsonify
from service import TransRecordService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/TransRecord', methods=['GET', 'POST'])
def TransRecord():
    return render_template('TransRecord.html')

@app.route('/queryTransRecord', methods=['POST'])
def queryTransRecord():
    data = request.json
    userId = data.get('userId', '').strip() or None
    startDate = data.get('startDate', '').strip() or None
    endDate = data.get('endDate', '').strip() or None

    # 確保 getData 函數被正確調用
    TransRecord = TransRecordService.getData(userId, startDate, endDate)

    # 將 DataFrame 轉換為字典列表
    records = TransRecord.to_dict(orient='records') if TransRecord is not None else []

    return jsonify(records=records)

if __name__ == '__main__':
    app.run(debug=True)
