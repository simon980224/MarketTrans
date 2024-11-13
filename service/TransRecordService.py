import sqlite3
import pandas as pd

def getData(userId=None, transAmount=None, transDate=None):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('/Users/chenyaoxuan/Desktop/MarketRecord.db')
        cursor = conn.cursor()

        # 初始 SQL 查詢語句
        sql = 'SELECT * FROM TransRecord WHERE 1=1'
        parameters = []

        # 增加條件過濾
        if userId:
            sql += ' AND User_Id = ?'
            parameters.append(userId)
        if transAmount:
            sql += ' AND Trans_Amount = ?'
            parameters.append(transAmount)
        if transDate:
            sql += ' AND Trans_Date = ?'
            parameters.append(transDate)

        # 執行查詢
        cursor.execute(sql, parameters)
        results = cursor.fetchall()

        # 獲取列名稱
        column_names = [description[0] for description in cursor.description]

        # 將結果轉換為 DataFrame
        df = pd.DataFrame(results, columns=column_names)

        return df

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # 確保游標和連接被正確關閉
        if cursor:
            cursor.close()
        if conn:
            conn.close()