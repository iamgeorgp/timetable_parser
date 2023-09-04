import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import pars_func2
import w_func


API_TOKEN = w_func.read_token('token.txt')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Словарь для хранения состояния пользователей
user_state = {}
user_group = {}


# Команда /start
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("🎓 PRUE Study Buddy can help you add a schedule to your calendar app."
                         "If you have Android installed, just click on the .ics file to import the schedule. For iOS users, follow the instructions to set up the import.\n"
                         "Use /help for help notion\nReady to get started?", 
                         reply_markup=w_func.hello_message_markup()
                         )

@dp.message_handler(commands=['help'])
async def help_note(message: types.Message):
    await message.answer("Help Notion\n"
                         "--Menu--\n"
                         "`Current week schedule` - send current week schedule in .ics format\n"
                         "`Next week schedule` - send next week schedule in .ics format\n"
                         "`Change group` - change your group (use before use .ics commands)\n"
                         "`iOS manual` -  send link of manual for iOS to connect calendar\n"
                         "`Campus map` - send image of campus\n"
                         )

# Обработчик для кнопки "Меню"
@dp.callback_query_handler(lambda c: c.data == 'menu')
async def show_menu(call: types.CallbackQuery):
    await call.message.answer("Select:", 
                              reply_markup=w_func.main_menu_buttons_markup())

@dp.message_handler(lambda message: message.text == "Campus map")
async def show_campus_map(message: types.Message):
    instruction_image_url = "https://www.rea.ru/ru/org/faculties/Fakultet-biznesa-i-dopolnitelnogo-obrazovanija/PublishingImages/%D0%9A%D0%BE%D1%80%D0%BF%D1%83%D1%81%D0%B0%20%D0%A0%D0%AD%D0%A3.JPEG"
    caption = "PRUE map"
    await message.reply_photo(photo=instruction_image_url, caption=caption)

@dp.message_handler(lambda message: message.text == "iOS manual")
async def show_ios_manual(message: types.Message):
    await message.answer("Here are the instructions for iOS", 
                         reply_markup=w_func.ios_manual_markup())
# Обработчик для кнопки "Текущая неделя"
@dp.message_handler(lambda message: message.text == "Current week")
async def show_current_week(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_group:
        group_number = user_group[user_id]
        await pars_func2.send_schedule(message, user_group, user_id)
    else:
        message.answer("First, set your group number with the 'Change group' command.")


# Обработчик для кнопки "Поменять группу"
@dp.message_handler(lambda message: message.text == "Change group")
@dp.message_handler(commands=['change_group'])
async def change_group(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = "awaiting_group"
    await message.answer("Enter the group number.\nFor example:    15.06д-мен03а/21б")


# Обработчик ввода группы
@dp.message_handler(lambda message: user_state.get(message.from_user.id) == "awaiting_group")
async def process_group(message: types.Message):
    user_id = message.from_user.id
    group = message.text
    # Проверяем группу с помощью вашей функции check_group
    valid_group = await pars_func2.check_group(group)
    if valid_group:
        user_state.pop(user_id)  # Удаляем состояние пользователя
        await message.answer(f"The group has been successfully selected:\n✅    {group}")
    else:
        await message.answer("❌ Incorrect group entered\nClick the 'Change group' button again")


if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
