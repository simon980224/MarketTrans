import sqlite3
import pandas as pd

def getData(userId=None, startDate=None, endDate=None):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('/Users/chenyaoxuan/Desktop/MarketRecord.db')
        cursor = conn.cursor()

        # 初始 SQL 查詢語句
        sql = 'SELECT * FROM TransRecord WHERE 1=1'
        parameters = []

        # 增加條件過濾
        if userId:
            sql += ' AND User_Id LIKE ?'
            parameters.append(f'%{userId}%')
        if startDate and endDate:
            sql += ' AND Trans_Date BETWEEN ? AND ?'
            parameters.append(startDate)
            parameters.append(endDate)

        sql += ' ORDER BY Trans_Date DESC'

        # 執行查詢
        cursor.execute(sql, parameters)
        results = cursor.fetchall()

        # 獲取列名稱
        column_names = [description[0] for description in cursor.description]

        return pd.DataFrame(results, columns=column_names)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # 確保游標和連接被正確關閉
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getTotalAmount(userId=None):
    total_amount = 0
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect('/Users/chenyaoxuan/Desktop/MarketRecord.db')
        cursor = conn.cursor()

        # 初始 SQL 查詢語句
        sql = 'SELECT SUM(Trans_Amount) AS Total_Amount FROM TransRecord WHERE 1=1'
        parameters = []

        if userId:
            sql += ' AND User_Id LIKE ?'
            parameters.append(f'%{userId}%')

        cursor.execute(sql, parameters)
        result = cursor.fetchone()

        total_amount = result[0] if result[0] is not None else 0

        return total_amount
    
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        # 確保游標和連接被正確關閉
        if cursor:
            cursor.close()
        if conn:
            conn.close()
