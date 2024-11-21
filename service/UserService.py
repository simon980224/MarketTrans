from datetime import datetime
import sqlite3

# 統一管理資料庫位置
DATABASE_PATH = 'Transaction.db'

def getData(userId=None, startDate=None, endDate=None):
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
            ORDER BY Trans_Id DESC
        '''

        cursor.execute(sql, parameters)
        results = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]

        return [dict(zip(column_names, row)) for row in results]

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def checkUserExists(userId):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT User_Id FROM User WHERE User_Id = ?
        """, (userId,))
        result = cursor.fetchone()

        return result is not None

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        return False

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def addRecord(userId, amount, date):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            INSERT INTO TransResponse (Trans_Id, User_Id, Trans_Amount, Trans_Date)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(sql, (getNewTransId(), userId, amount, date))
        
        conn.commit()

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getNewTransId():
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        today = datetime.now()
        year = today.year % 100  # 取得年份的後兩位
        month = today.month
        day = today.day

        # 格式化日期部分
        date_part = f"{year:02}{month:02}{day:02}"

        # 查詢當日最大交易編號
        cursor.execute("""
            SELECT Trans_Id FROM TransResponse 
            WHERE Trans_Id LIKE ? 
            ORDER BY Trans_Id DESC 
            LIMIT 1
        """, (f"{date_part}%",))
        result = cursor.fetchone()

        if result:
            # 解析出編號部分，並遞增
            last_id = result[0]
            last_number = int(last_id.split('_')[1])
            next_number = last_number + 1
        else:
            # 如果沒有當天的交易，從1開始
            next_number = 1

        # 返回新的交易編號，並在前面加上 "req"
        return f"req_{date_part}_{next_number:03}"

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def getUserData():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    sql = '''
        SELECT 
            *
        FROM User
    '''

    cursor.execute(sql)
    results = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]

    return [dict(zip(column_names, row)) for row in results]

