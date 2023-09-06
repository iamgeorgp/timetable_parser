'''
Main Functions for tg bot
'''

from aiogram import  types
import dateparser

# F: read tg bot token 
def read_token(filename):
    full_file_name = 'config\\' + filename
    with open(full_file_name, 'r') as file:
        return file.read().strip()

# F: get lesson star&end 
def date_converter(pair_number, day, month, year):
    # создают дату со временем в соответсвии с датой и номера пары
    # возвращает начало и конец пары
    time_of_pair = {1: [[8, 30], [10, 00]],
                    2: [[10, 10], [11, 40]],
                    3: [[11, 50], [13, 20]],
                    4: [[14, 0], [15, 30]],
                    5: [[15, 40], [17, 10]],
                    6: [[17, 20], [18, 50]]
                    }
    timing_of_pair = time_of_pair[int(pair_number)]
    hour_begin = timing_of_pair[0][0]
    minute_begin = timing_of_pair[0][1]
    hour_end = timing_of_pair[1][0]
    minute_end = timing_of_pair[1][1]
    date_time_str_begin = f"{int(day)} {str(month)} {int(year)} {hour_begin:02d}:{minute_begin:02d}"
    date_time_str_end = f"{int(day)} {str(month)} {int(year)} {hour_end:02d}:{minute_end:02d}"
    return dateparser.parse(date_time_str_begin), dateparser.parse(date_time_str_end)

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