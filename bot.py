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
        [InlineKeyboardButton("Перейти к инструкции для iOS", url='https://teletype.in/@geocode/Zj6q780IQAk')],
        [InlineKeyboardButton("Меню", callback_data='show_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f"👋 Привет!\nБот сделан маёвцем для РЭУ.\n    Бот присылает расписание файлом формата .ics, который удобно импортировать в любой календарь (Google, Яндекс, Samsung, Apple, Outlook).\n    Для владельцев Android все работает сразу: файл календаря открывается через любое приложение.\n    Владельцам iOS необходимо сделать настройку, которая не займет больше 2 минут\n    Прочитать инструкцию или открыть меню ты можешь ниже по кнопкам:",
        reply_markup=reply_markup
    )

def menu(update: Update, context: CallbackContext) -> None:
    custom_keyboard = [
        [KeyboardButton("Текущая неделя"), KeyboardButton("Следующая неделя")],
        [KeyboardButton("Изменить группу")],
        [KeyboardButton("Инструкция")],
    ]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

def send_instruction_link(update: Update, context: CallbackContext) -> None:
    instruction_link = "https://teletype.in/@geocode/Zj6q780IQAk"
    update.message.reply_text("Вот инструкция для iOS", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Открыть инструкцию", url=instruction_link)]]))


def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if query.data == 'show_menu':
        menu(query, context)

def set_group(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Введите номер группы\nНапример: 15.06д-мен03а/21б")
    # Настройте следующий обработчик для ожидания номера группы
    context.user_data['waiting_for_group'] = True

def handle_group_number(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if 'waiting_for_group' in context.user_data and pars_func.check_group(update.message.text):
        group_number = update.message.text
        user_groups[user_id] = group_number
        del context.user_data['waiting_for_group']
        update.message.reply_text(f"✅Группа успешно установлена✅\n{group_number}")
    else:
        update.message.reply_text(f"❌Неправильно введена группа❌\nНажмите еще раз на кнопку 'Изменить группу'")
        # Введите команду 'Изменить группу', чтобы установить новую группу.

def send_current_schedule(update: Update, context: CallbackContext) -> None:
    pars_func.hihi()

    user_id = update.message.from_user.id
    if user_id in user_groups:
        group_number = user_groups[user_id]
        pars_func.send_schedule(update, user_groups, user_id)
    else:
        update.message.reply_text("Для начала установите номер своей группы командой 'Изменить группу'.")

def send_next_schedule(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Функция находится в разработке.")


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
    dispatcher.add_handler(MessageHandler(Filters.text("Инструкция"), send_instruction_link))

    # Обработчик для команды "Изменить группу"
    dispatcher.add_handler(MessageHandler(Filters.text("Изменить группу"), set_group))

    # Обработчик для кнопки "Текущая"
    dispatcher.add_handler(MessageHandler(Filters.text("Следующая неделя"), send_next_schedule))
    
    # Обработчик для кнопки "Текущая"
    dispatcher.add_handler(MessageHandler(Filters.text("Текущая неделя"), send_current_schedule))

    

    # Обработчик для ввода номера группы
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_group_number))

    


    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()