import logging
from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.middlewares.logging import LoggingMiddleware

import w_func
import sql_func

API_TOKEN = w_func.read_token(filename='token.txt')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
# dp.middleware.setup(LoggingMiddleware())

# Dictionary for storing user status
user_state = {}
user_group = {}

# Handler for the '/start' command
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer("🎓 <b>PRUE Study Buddy</b>\ncan help you add a schedule to your calendar app.\n"
                         "If you have Android installed, just click on the .ics file to import the schedule. For iOS users, follow the instructions to set up the import.\n"
                         "Use /help to get assisatnce.\nReady to get started?", 
                         reply_markup=w_func.hello_message_markup(),
                         parse_mode=types.ParseMode.HTML
                         )
    
# Handler for the '/help' command
@dp.message_handler(commands=['help'])
async def help_note(message: types.Message):
    await message.answer("❓ <b>Help Menu</b>\n"
                         "<u>Current week schedule</u> - send current week schedule in .ics format\n"
                         "<u>Next week schedule</u> - send next week schedule in .ics format\n"
                         "<u>Change group</u> - change your group (use before use .ics commands)\n"
                         "<u>iOS manual</u> -  send link of manual for iOS to connect calendar\n"
                         "<u>Campus map</u> - send image of campus\n"
                         "<u>Reviews of teachers</u> - feature in development",
                         parse_mode=types.ParseMode.HTML
                         )

# Handler for the "Menu" button
@dp.callback_query_handler(lambda c: c.data == 'menu')
async def show_menu(call: types.CallbackQuery):
    await call.message.answer("Select button:", 
                              reply_markup=w_func.main_menu_buttons_markup())

# Handler for the "Campus map" button
@dp.message_handler(lambda message: message.text == "Campus map")
async def show_campus_map(message: types.Message):
    instruction_image_url = "https://www.rea.ru/ru/org/faculties/Fakultet-biznesa-i-dopolnitelnogo-obrazovanija/PublishingImages/%D0%9A%D0%BE%D1%80%D0%BF%D1%83%D1%81%D0%B0%20%D0%A0%D0%AD%D0%A3.JPEG"
    caption = "PRUE map"
    await message.reply_photo(photo=instruction_image_url, caption=caption)

# Handler for the "iOS manual" button
@dp.message_handler(lambda message: message.text == "iOS manual")
async def show_ios_manual(message: types.Message):
    await message.answer("Here are the instructions for iOS", 
                         reply_markup=w_func.ios_manual_markup())

# Handler for the "Current week schedule" button
@dp.message_handler(lambda message: message.text == "Current week\nschedule")
async def show_current_week(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_group:
        group_number = user_group[user_id]
        file_path = w_func.find_file_by_name(group_number, 'current_week')     #   .send_schedule(message, user_group, user_id)
        await message.answer_document(open(file_path, 'rb'), caption='🗓 Your schedule for current week')
    else:
        await message.answer("First, set your group number with the 'Change group' command.")

# Handler for the "Next week schedule" button
@dp.message_handler(lambda message: message.text == "Next week\nschedule")
async def show_current_week(message: types.Message):
    user_id = message.from_user.id
    if user_id in user_group:
        group_number = user_group[user_id]
        file_path = w_func.find_file_by_name(group_number, 'next_week')     #   .send_schedule(message, user_group, user_id)
        await message.answer_document(open(file_path, 'rb'), caption='🗓 Your schedule for next week')
    else:
        await message.answer("First, set your group number with the 'Change group' command.")

# Handler for the "Reviews of teachers" button
@dp.message_handler(lambda message: message.text == "Reviews of teachers")
async def reviews_teachers(message: types.Message):
    await message.answer("🔧 Feature in development")

# Handler for the "Change group" button
@dp.message_handler(lambda message: message.text == "Change group")
@dp.message_handler(commands=['change_group'])
async def change_group(message: types.Message):
    user_id = message.from_user.id
    user_state[user_id] = "awaiting_group"
    await message.answer("Enter the group number.\nFor example:    15.06д-мен03а/21б")

# Group input handler
@dp.message_handler(lambda message: user_state.get(message.from_user.id) == "awaiting_group")
async def process_group(message: types.Message):
    user_id = message.from_user.id
    group = message.text.lower()
    valid_group = sql_func.find_schedule(group)
    if valid_group != False:
        user_state.pop(user_id)  # Delete user state
        user_group[user_id] = group
        await message.answer(f"The group has been successfully selected:\n✅    {group}")
    else:
        await message.answer("❌ Incorrect group entered\nClick the 'Change group' button again")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)