from datetime import datetime
import sqlite3

# 統一管理資料庫位置
DATABASE_PATH = 'Transaction.db'


def getData(userId=None):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            SELECT 
                User_Id, 
                User_Name, 
                Line_Id, 
                Bank_Id
            FROM 
                "User"
            WHERE 
                1=1
        '''
        parameters = []

        if userId:
            sql += ' AND User_Id LIKE ?'
            parameters.append(f"%{userId}%")

        sql += '''
            ORDER BY User_Id
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


def addUser(userId, userName, lineId, bankId):
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        sql = '''
            INSERT INTO User (User_Id, User_Name, Line_Id, Bank_Id)
            VALUES (?, ?, ?, ?)
        '''
        cursor.execute(sql, (userId, userName, lineId, bankId))

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


# def getNewTransId():
#     try:
#         # 連接到 SQLite 資料庫
#         conn = sqlite3.connect(DATABASE_PATH)
#         cursor = conn.cursor()

#         today = datetime.now()
#         year = today.year % 100  # 取得年份的後兩位
#         month = today.month
#         day = today.day

#         # 格式化日期部分
#         date_part = f"{year:02}{month:02}{day:02}"

#         # 查詢當日最大交易編號
#         cursor.execute("""
#             SELECT Trans_Id FROM TransRequests 
#             WHERE Trans_Id LIKE ? 
#             ORDER BY Trans_Id DESC 
#             LIMIT 1
#         """, (f"{date_part}%",))
#         result = cursor.fetchone()

#         if result:
#             # 解析出編號部分，並遞增
#             last_id = result[0]
#             last_number = int(last_id.split('_')[1])
#             next_number = last_number + 1
#         else:
#             # 如果沒有當天的交易，從1開始
#             next_number = 1

#         # 返回新的交易編號，並在前面加上 "req"
#         return f"req_{date_part}_{next_number:03}"

#     except sqlite3.Error as e:
#         print(f"An error occurred: {e}")

#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

def getNewUserId():
    try:
        # 連接到 SQLite 資料庫
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # 查詢最大用戶編號
        cursor.execute("""
            SELECT User_Id FROM User
            ORDER BY User_Id DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        # User_Id 格式為Axxx
        if result:
            # 解析出編號部分，並遞增
            last_id = result[0]
            print('last_id',last_id)
            last_number = int(last_id.split('U')[1])
            print('last_number',last_number)
            next_number = last_number + 1
        else:
            # 如果沒有用戶，從1開始
            next_number = 1

        # 返回新的用戶編號
        return f"U{next_number:03}"

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
