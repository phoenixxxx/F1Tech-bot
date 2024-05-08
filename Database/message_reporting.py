from typing import Final

import sqlite3
import datetime

DATABASE: Final[str] = 'f1techbot.db'
MessageReportTable_name: Final[str] = 'MessageReports'
MessageAckTable_name: Final[str] = 'MessageAcknowledgements'

def store_response(jump_url: str, ack_msg_id: int) -> None:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT * FROM {MessageAckTable_name}")
    except sqlite3.OperationalError:
        print("Creating {MessageAckTable_name} table")
        cursor.execute(f'''
                       CREATE TABLE {MessageAckTable_name}(
                       trigger_msg_jump_url TEXT,
                       ack_msg_id INTEGER
                       )
                       ''')
    cursor.execute(f"INSERT INTO {MessageAckTable_name} VALUES ('{jump_url}', '{ack_msg_id}')")
    connection.commit()
    connection.close()

def get_response(jump_url: str) -> str:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    ack_msg_id = None
    try:
        cursor.execute(f"SELECT * FROM {MessageAckTable_name} WHERE trigger_msg_jump_url=='{jump_url}'")
        result = cursor.fetchone()
        ack_msg_id = result[1]
    except sqlite3.OperationalError:
        pass
    
    connection.close()
    return ack_msg_id

def store(msg_id: int, chl_id: int, jump_url: str, user_name: str, user_id: int, report : str) -> None:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # if Table doesn't exist, we create it
    try:
        cursor.execute(f"SELECT * FROM {MessageReportTable_name}")
    except sqlite3.OperationalError:
        print("Creating {MessageReportTable_name} table")
        cursor.execute(f'''
                       CREATE TABLE {MessageReportTable_name}(
                       msg_id INTEGER,
                       chl_id INTEGER,
                       jump_url TEXT,
                       reporter TEXT,
                       reporter_id INTEGER,
                       report TEXT,
                       report_date TIMESTAMP
                       )
                       ''')

    # Store report
    currentDateTime = datetime.datetime.now()
    cursor.execute(f"INSERT INTO {MessageReportTable_name} VALUES ('{msg_id}', '{chl_id}', '{jump_url}', '{user_name}', '{user_id}', '{report}', '{currentDateTime}')")
    connection.commit()
    connection.close()

def get_reports(jump_url: str) -> list[object]:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    results = list()
    try:
        cursor.execute(f"SELECT * FROM {MessageReportTable_name} WHERE jump_url=='{jump_url}' ORDER BY report_date")
        results = cursor.fetchall()
    except sqlite3.OperationalError as e:
        print(f"get_stats failed with {e}")
        pass
    connection.close()
    return results

def get_report_count() -> int:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    count:int = 0
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {MessageReportTable_name}")
        count = cursor.fetchone()[0]
    except sqlite3.OperationalError as e:
        print(f"get_stats failed with {e}")
        pass
    connection.close()
    return count