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

def get_stats(jump_url: str) -> tuple[int, int, str]:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    report_count = 0
    reporter_count = 0
    latest_report = ""
    try:
        cursor.execute(f"SELECT * FROM {MessageReportTable_name} WHERE jump_url=='{jump_url}' ORDER BY report_date")
        results = cursor.fetchall()
        unique_reporters = list()
        for result in results:
            report_count += 1
            reporter_id = result[2]
            if reporter_id not in unique_reporters:
                unique_reporters.append(reporter_id)
                reporter_count += 1
            latest_report = result[5]
    except sqlite3.OperationalError as e:
        print(f"get_stats failed with {e}")
        pass
    
    connection.close()

    return report_count, reporter_count, latest_report
    