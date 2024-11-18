import sqlite3
import pandas as pd

# 統一管理資料庫位置
DATABASE_PATH = '/Users/chenyaoxuan/Desktop/MarketRecord.db'

def getData(userId=None, startDate=None, endDate=None):
    conn = None
    cursor = None
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            SELECT 
                Trans_Id, 
                User_Id, 
                Trans_Amount, 
                Trans_Date, 
                Total_Amount
            FROM (
                SELECT 
                    *,
                    SUM(Trans_Amount) OVER() AS Total_Amount
                FROM 
                    TransResponse
                WHERE 
                    1=1
        '''
        parameters = []

        if userId:
            sql += ' AND User_Id LIKE ?'
            parameters.append(f"%{userId}%")
        if startDate and endDate:
            sql += ' AND Trans_Date BETWEEN ? AND ?'
            parameters.append(startDate)
            parameters.append(endDate)

        sql += '''
            )
            ORDER BY Trans_Date DESC
        '''

        cursor.execute(sql, parameters)
        results = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        return pd.DataFrame(results, columns=column_names)

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# print(getData(None, None, None))