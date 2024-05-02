from typing import Final

import sqlite3
import datetime

DATABASE: Final[str] = 'f1techbot.db'
FeedbackTable_name: Final[str] = 'Feedbacks'

def store(reporter: str, feedback_title: str, feedback : str) -> None:
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # if Table doesn't exist, we create it
    try:
        cursor.execute(f"SELECT * FROM {FeedbackTable_name}")
    except sqlite3.OperationalError:
        print("Creating {FeedbackTable_name} table")
        cursor.execute(f'''
                       CREATE TABLE {FeedbackTable_name}(
                       feedback_title TEXT,
                       feedback TEXT,
                       reporter TEXT,
                       report_date TIMESTAMP
                       )
                       ''')

    # Store report
    currentDateTime = datetime.datetime.now()
    cursor.execute(f"INSERT INTO {FeedbackTable_name} VALUES ('{feedback_title}', '{feedback}', '{reporter}', '{currentDateTime}')")
    connection.commit()
    connection.close()