from flask import Flask, render_template, request
from service import TransRecordService

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/TransRecord', methods=['GET', 'POST'])
def TransRecord():
    return render_template('TransRecord.html')

@app.route('/queryTransRecord', methods=['GET', 'POST'])
def queryTransRecord():
    if request.method == 'POST':
        userId = request.form.get('userId', '').strip() or None
        startDate = request.form.get('startDate', '').strip() or None
        endDate = request.form.get('endDate', '').strip() or None

        # 確保 getData 函數被正確調用
        TransRecord = TransRecordService.getData(userId, startDate, endDate)

        # 將 DataFrame 轉換為字典列表
        records = TransRecord.to_dict(orient='records') if TransRecord is not None else []

        return render_template('TransRecord.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
