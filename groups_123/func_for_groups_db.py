'''
Functions for Database
'''

import os
import sqlite3
from data_group import group_url

# get path to directory
script_directory = os.path.dirname(os.path.abspath(__file__))
# full path to database
database_path = os.path.join(script_directory, '..', 'databases', 'hsci.db')

# F: Check db existense
def table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    return cursor.fetchone() is not None

# F: Create db and table
def create_database():
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    if not table_exists(cursor, 'schedules'):
        cursor.execute('''CREATE TABLE schedules
                          (group_number TEXT PRIMARY KEY, schedule_url TEXT)''')
    conn.commit()
    conn.close()

# F: Add new info in db
def add_schedule(group_number, schedule_url):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO schedules (group_number, schedule_url) VALUES (?, ?)",
                   (group_number, schedule_url))
    conn.commit()
    conn.close()

# F: Combining upper functions
def operate_db():
    create_database()
    all_groups = group_url()
    for group in all_groups:
        add_schedule(group, all_groups[group])