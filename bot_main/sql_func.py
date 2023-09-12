'''
SQL Queries for working with database
'''

import sqlite3
import os

# get path to directory
script_directory = os.path.dirname(os.path.abspath(__file__))
# full path to database
database_path = os.path.join(script_directory, '..', 'databases', 'hsci.db')

# F: Search for a schedule by group number
def find_schedule(group_number):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("SELECT schedule_url FROM schedules WHERE group_number = ?", (group_number,))
    result = cursor.fetchone()
    print(result)
    conn.close()
    if result:
        return result[0]
    else:
        return False