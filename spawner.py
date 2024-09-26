import calendar

from main import entity_buttons_data
from utils import utils
from constants.buttons import *
from constants.crud import *
from constants.hints import *
from datetime import datetime
from telebot import types

main_menu_buttons = {
    "📆 Розклад на сьогодні":GET_SCHEDULE_COMMAND,
    "☎🔗 Контакти та посилання":GET_CONTACTS_COMMAND,
    "🧾 Домашні завдання": GET_HOMEWORKS_COMMAND,
    "ℹ Про бота":GET_BOT_INFO_COMMAND
}

admin_menu_buttons={
    "📆 Розклад":CRUD_SCHEDULE_COMMAND,
    "📑 Домашні завдання":CRUD_HOMEWORK_COMMAND,
    "👨‍🏫 Викладачі":CRUD_TEACHER_COMMAND,
    "📚 Предмети": CRUD_SUBJECT_COMMAND
}

crud_menu_buttons={
    "➕ Створити":ADD,
    "✍️ Редагувати":EDIT,
    "❌ Видалити":DELETE
}

def spawn_dict_menu(menu_buttons:list, crud_entity:str=None)->list:
    markup=[]
    for mb in menu_buttons:
        if isinstance(mb,dict):
            for key, value in mb.items():
                markup.append(types.InlineKeyboardButton(key,callback_data=value 
                                                         if crud_entity is None else f"{value}_{crud_entity}"))
    return markup

def spawn_inline_button(button_text:str, callback_data:str):
    return types.InlineKeyboardButton(text=button_text, callback_data=callback_data)
 
def spawn_back_button(return_type=False, button_text:str=BACK_TO_MAIN_BUTTON_TEXT, command_type=BACK_TO_MAIN_COMMAND)->list:
    markup = []
    type = types.InlineKeyboardButton(button_text, callback_data=command_type)
    if return_type == True:
        return type
    markup.append(type)
    return markup

def spawn_today_schedule_menu()->list:
    row=[]
    row.append(spawn_back_button(True))
    row.append(types.InlineKeyboardButton("📆 На місяць", callback_data=GET_CALENDAR_COMMAND))
    return row

def spawn_calendar_menu(year=None, month=None)->list:
    now = datetime.now()
    if year is None:
        year = now.year
    if month is None:
        month = now.month
    
    month_calendar = calendar.monthcalendar(year, month)
    markup_rows=[]
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton("❌", callback_data=IGNORE_COMMAND))
            else:
                row.append(types.InlineKeyboardButton(str(day), callback_data=f"day_{year}-{month}-{day}"))
        markup_rows.append(row)
    row = []
    row.append(spawn_back_button(True))
    # Next month button
    # row.append(types.InlineKeyboardButton("⏭ Наступний місяць", callback_data=IGNORE))
    markup_rows.append(row)
    return markup_rows

def spawn_teacher_buttons(tg_message, query:list, crud_command:str, entity_name:str, target_id:str=None, field_name:str=None):
    buttons=[]
    back_button = None
    chat_id = tg_message.chat.id
    if len(query) != 0:
        entity_buttons_data[chat_id] ={}
        for teacher in query:
            if field_name:
                callback_data = f"{crud_command}_{entity_name}_{teacher.id}_{field_name}"
                if target_id:
                    callback_data = f"{crud_command}_{entity_name}_{target_id}_{field_name}_{teacher.id}"
            else:
                callback_data = f"{crud_command}_{entity_name}_{teacher.id}"
            print(teacher.id)
            button_id = f"{ENTITY_COMMAND}_{utils.get_uuid1()}"
            entity_buttons_data[chat_id][button_id] = callback_data
            buttons.append(spawn_inline_button(button_text=teacher.name, callback_data=button_id))
            back_button = spawn_back_button(return_type=True, button_text=CANCEL_BUTTON_TEXT, command_type=BACK_TO_ADMIN_COMMAND)
    else:
        back_button = spawn_back_button(return_type=True, button_text=BACK_TO_MAIN_BUTTON_TEXT, command_type=BACK_TO_ADMIN_COMMAND)
    buttons.append(back_button)
    return buttons

def spawn_subject_buttons(tg_message, query:list, crud_command:str, entity_name:str, target_id:str=None, field_name:str=None):
    buttons=[]
    back_button = None
    chat_id = tg_message.chat.id
    if len(query) != 0:
        entity_buttons_data[chat_id] ={}
        for subject in query:
            if field_name:
                callback_data = f"{crud_command}_{entity_name}_{subject.id}_{field_name}"
                if target_id:
                    callback_data = f"{crud_command}_{entity_name}_{target_id}_{field_name}_{subject.id}"
            else:
                callback_data = f"{crud_command}_{entity_name}_{subject.id}"
            button_id = f"{ENTITY_COMMAND}_{utils.get_uuid1()}"
            entity_buttons_data[chat_id][button_id] = callback_data
            buttons.append(spawn_inline_button(button_text=subject.name, callback_data=callback_data))
            back_button = spawn_back_button(return_type=True, button_text=CANCEL_BUTTON_TEXT, command_type=BACK_TO_ADMIN_COMMAND)
    else:
        back_button = spawn_back_button(return_type=True, button_text=BACK_TO_MAIN_BUTTON_TEXT, command_type=BACK_TO_ADMIN_COMMAND)
    buttons.append(back_button)
    return buttons

