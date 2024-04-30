from discord import Embed, Colour
from discord import Message, Interaction
import sqlite3
import datetime

def report_message(interaction: Interaction, message: Message, report : str) -> bool:
    connection = sqlite3.connect('f1techbot.db')
    cursor = connection.cursor()
    results = list()
    try:
        cursor.execute(f"SELECT * FROM MessageReports WHERE msg_url=='{message.jump_url}'")
        results = cursor.fetchall()
    except sqlite3.OperationalError:
        print("Creating MessageReports table")
        cursor.execute('''
                       CREATE TABLE MessageReports(
                       msg_url TEXT,
                       reporter TEXT,
                       reporter_id INTEGER,
                       report TEXT,
                       report_date TIMESTAMP
                       )
                       ''')

    reporter_count = 1
    report_count = len(results) + 1
    for result in results:
        reporter_id = result[2]
        if reporter_id != interaction.user.id:
            reporter_count += 1

    # Store report
    currentDateTime = datetime.datetime.now()
    cursor.execute(f"INSERT INTO MessageReports VALUES ('{message.jump_url}', '{interaction.user.name}', '{interaction.user.id}', '{report}', '{currentDateTime}')")

    connection.commit()
    connection.close()
    return report_count, reporter_count

