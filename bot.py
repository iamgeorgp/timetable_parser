import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

import pars_func

def read_token(filename):
    with open(filename, 'r') as file:
        return file.read().strip()

TOKEN = read_token('token.txt')
# Словарь для хранения групп пользователей
user_groups = {}



def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Read the iOS manual", url='https://teletype.in/@geocode/Zj6q780IQAk')],
        [InlineKeyboardButton("Menu", callback_data='show_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"🎓 PRUE Study Buddy can help you add a schedule to your calendar app. \nIf you have Android installed, just click on the .ics file to import the schedule. For iOS users, follow the instructions to set up the import. \nReady to get started?",
        reply_markup=reply_markup
    )

def menu(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [
        [KeyboardButton("Current week"), KeyboardButton("Next week")],
        [KeyboardButton("Change group")],
        [KeyboardButton("iOS manual")],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text("Select:", reply_markup=reply_markup)

def send_instruction_link(update: Update, context: CallbackContext) -> None:
    instruction_link = "https://teletype.in/@geocode/Zj6q780IQAk"
    update.message.reply_text("Here are the instructions for iOS", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open the manual", url=instruction_link)]]))


def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'show_menu':
        menu(query, context)

def set_group(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Enter the group number.\nFor example: 15.06д-мен03а/21б")
    # Настройте следующий обработчик для ожидания номера группы
    context.user_data['waiting_for_group'] = True

def handle_group_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if 'waiting_for_group' in context.user_data and pars_func.check_group(update, update.message.text):
        group_number = update.message.text
        user_groups[user_id] = group_number
        del context.user_data['waiting_for_group']
        update.message.reply_text(f"✅ The group has been successfully selected\n{group_number}")
    else:
        update.message.reply_text(f"❌ Incorrect group entered\nClick the 'Change group' button again")
        # Введите команду 'Change group', чтобы установить новую группу.

def send_current_schedule(update: Update, context: CallbackContext) -> None:

    user_id = update.message.from_user.id
    if user_id in user_groups:
        group_number = user_groups[user_id]
        pars_func.send_schedule(update, user_groups, user_id)
    else:
        update.message.reply_text("First, set your group number with the 'Change group' command.")

def send_next_schedule(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("The feature is in development...")
    # user_id = update.message.from_user.id
    # if user_id in user_groups:
    #     group_number = user_groups[user_id]
    #     pars_func.send_n_schedule(update, user_groups, user_id)
    # else:
    #     update.message.reply_text("First, set your group number with the 'Change group' command.")

def main():

    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчик команды /start
    dispatcher.add_handler(CommandHandler('start', start))

    # Обработчик кнопки
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    # Обработчик команды /menu
    dispatcher.add_handler(CommandHandler('menu', menu))

    # Обработчик для кнопки "Инструкция"
    dispatcher.add_handler(MessageHandler(Filters.text("iOS manual"), send_instruction_link))

    # Обработчик для команды "Изменить группу"
    dispatcher.add_handler(MessageHandler(Filters.text("Change group"), set_group))

    # Обработчик для кнопки "Текущая"
    dispatcher.add_handler(MessageHandler(Filters.text("Next week"), send_next_schedule))
    
    # Обработчик для кнопки "Текущая"
    dispatcher.add_handler(MessageHandler(Filters.text("Current week"), send_current_schedule))

    

    # Обработчик для ввода номера группы
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_group_number))

    


    updater.start_polling()  # Здесь используется await
    updater.idle()

if __name__ == '__main__':
    main()