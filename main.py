import telebot
import os
import calendar
import json

from datetime import datetime
from telebot import types
from dotenv import load_dotenv
from entities.lesson import Lesson
from constants import *


load_dotenv()
bot_token = os.getenv(API_TOKEN)
bot = telebot.TeleBot(bot_token)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Оберіть одну із команд:", reply_markup=spawn_start_menu())

@bot.callback_query_handler(func=lambda call: True)
def handle_user_button(call):     
    which_but = call.data                                             
    if which_but == GET_SCHEDULE:
        refresh_inline_menu(call, change_menu(TODAY_SCHEDULE),get_today_schedule())
    elif which_but == GET_CONTACTS:
        info = read_text_file(CONTACT_INFO_PATH)
        refresh_inline_menu(call, change_menu(BACK_BUTTON),info ,parse_mode="html")
    elif which_but == GET_BOT_INFO:
        info = read_text_file(BOT_INFO_PATH)
        refresh_inline_menu(call, change_menu(BACK_BUTTON),info ,parse_mode="html")
    elif which_but == BACK_TO_MAIN:
        refresh_inline_menu(call, change_menu(MAIN_MENU),"Оберіть одну із команд:" )
    elif which_but == CALENDAR:
        refresh_inline_menu(call, change_menu(CALENDAR),"📆 Оберіть дату:")
    elif which_but.startswith("day_"):
        date = which_but.replace('day_','')
        refresh_inline_menu(call, change_menu(TODAY_SCHEDULE),get_today_schedule(date))
    

def get_today_schedule(date=None):
    lessons = load_lessons()
    if len(lessons)==0:
        return NO_LESSONS
    if date == None:
        date = datetime.today().date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")
    lessons_today = [lesson for lesson in lessons if lesson.date == date.strftime('%Y-%m-%d')]
    if len(lessons_today)==0:
        return NO_LESSONS
    result = f"📆 Ваш розклад на {date.strftime('%Y-%m-%d')}:\n\n"
    for lesson in lessons_today:
        result+=str(lesson)+'\n\n'
    return result

def load_lessons():
    try:
        results = read_text_file(LESSONS_PATH)
        lessons_data = json.loads(results)
        return [Lesson(**result) for result in lessons_data]
    except FileNotFoundError as e:
        print(f"Ошибка: Файл с уроками не найден. {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка: Невозможно декодировать JSON. {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    return []

def read_text_file(env_path):
    try:
        base_dir = os.path.dirname(__file__)
        text_file_path = os.getenv(env_path)
        if not text_file_path:
            return ERROR
        file_path = os.path.join(os.path.join(base_dir, "db"), text_file_path)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден по пути {file_path}. {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при чтении файла: {e}")
    return ERROR

def refresh_inline_menu(call, markup, text='', parse_mode=None):
     bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup= markup,
            parse_mode= parse_mode,
            disable_web_page_preview=True
        )
    
start_buttons = {
    "📆 Розклад на сьогодні":GET_SCHEDULE,
    "☎🔗 Контакти та посилання":GET_CONTACTS,
    "ℹ Про бота":GET_BOT_INFO
}
def spawn_start_menu():
    markup = types.InlineKeyboardMarkup()
    counter=0
    for key, value in start_buttons.items():
        counter+=1
        markup.add(types.InlineKeyboardButton(key,callback_data=value))
    return markup
 
def spawn_back_button(return_type=False):
    markup = types.InlineKeyboardMarkup()
    type = types.InlineKeyboardButton("🔙 У головне меню",callback_data=BACK_TO_MAIN)
    if return_type == True:
        return type
    markup.add(type)
    return markup

def spawn_today_schedule_menu():
    markup = types.InlineKeyboardMarkup()
    row=[]
    row.append(spawn_back_button(True))
    row.append(types.InlineKeyboardButton("📆 На місяць", callback_data=CALENDAR))
    markup.row(*row)
    return markup

def spawn_calendar_menu(year=None, month=None):
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    markup = types.InlineKeyboardMarkup()
    month_calendar = calendar.monthcalendar(year, month)
    
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton("❌", callback_data=IGNORE))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"day_{year}-{month}-{day}"))
        markup.row(*row)
    row = []
    row.append(spawn_back_button(True))
    # Next month button
    # row.append(types.InlineKeyboardButton("⏭ Наступний місяць", callback_data=IGNORE))
    markup.row(*row)
    return markup
    
def change_menu(menu_name):
    if menu_name == MAIN_MENU:
        return spawn_start_menu()
    elif menu_name == BACK_BUTTON:
        return spawn_back_button()
    elif menu_name == CALENDAR:
        return spawn_calendar_menu()
    elif menu_name == TODAY_SCHEDULE:
        return spawn_today_schedule_menu()

if __name__ == '__main__':
    bot.infinity_polling()