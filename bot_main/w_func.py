'''
Main Functions for tg bot
'''

from aiogram import  types
import os 
import re

# F: read tg bot token 
def read_token(filename):
    full_file_name = 'config\\' + filename
    with open(full_file_name, 'r') as file:
        return file.read().strip()

# F: find .ics by name    
def find_file_by_name(file_name):
    # get path to directory
    file_name = re.sub(r'[/:]', '-', file_name)
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # full path to database
    return os.path.join(script_directory, '..', 'group_schedule_ics', 'current_week', file_name + '.ics' )    

# F: hello message markup     
def hello_message_markup():
    markup = types.InlineKeyboardMarkup()
    article_button = types.InlineKeyboardButton("Read the iOS manual", url='https://teletype.in/@geocode/Zj6q780IQAk')
    menu_button = types.InlineKeyboardButton("Menu", callback_data='menu')
    markup.add(article_button)
    markup.add(menu_button)
    return markup

# F: iOS manual markup 
def ios_manual_markup():
    instruction_link = "https://teletype.in/@geocode/Zj6q780IQAk"
    markup = types.InlineKeyboardMarkup()
    manual_button = types.InlineKeyboardButton("Open the manual", url=instruction_link)
    markup.add(manual_button)
    return markup

# F: main menu markup
def main_menu_buttons_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    current_week_button = types.KeyboardButton("Current week\nschedule")
    next_week_button = types.KeyboardButton("Next week\nschedule")
    change_group_button = types.KeyboardButton("Change group")
    ios_manual_button = types.KeyboardButton("iOS manual")
    map_button = types.KeyboardButton("Campus map")
    reviews_teachers_button = types.KeyboardButton("Reviews of teachers")
    markup.row(current_week_button, next_week_button)
    markup.row(change_group_button)
    markup.row(ios_manual_button)
    markup.row(map_button)
    markup.row(reviews_teachers_button)
    return markup