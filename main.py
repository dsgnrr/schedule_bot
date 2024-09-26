import telebot
import os
import db.init_db as init_db

from db.dao import *
from telebot import types
from telebot.apihelper import ApiTelegramException
from dotenv import load_dotenv
from utils import utils
from utils.command import Command
from models.homework import *


from constants import crud
from constants.buttons import *
from constants.hints import *
from constants.messages import *
from constants.bot import *

edit_state={}
entity_buttons_data = {}
from spawner import *

# TODO: распределить обработчики по файлам
# TODO: добавить логгер и обработчики исключений

init_db.initialize_db()
load_dotenv()

 
bot = telebot.TeleBot(os.getenv(API_TOKEN))

@bot.message_handler(commands=['start'])
def send_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(*spawn_dict_menu([main_menu_buttons]),row_width=1)
    bot.send_message(message.chat.id, SELECT_COMMAND_PROMPT, reply_markup=markup)

@bot.message_handler(commands=['admin_menu'])
def send_admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(*spawn_dict_menu([admin_menu_buttons]),row_width=1)
    bot.send_message(message.chat.id, SELECT_COMMAND_PROMPT, reply_markup=markup)

# Обработчик АБСОЛЮТНО ВСЕХ инлайн кнопок которые есть в боте, он должен быть только один 
# TODO: разбить это, нечитабельно
@bot.callback_query_handler(func=lambda call: True)
def handle_user_button(call):
    if call.message.chat.id in edit_state:
        del edit_state[call.message.chat.id]    
    which_but = call.data                                             
    if which_but == GET_SCHEDULE_COMMAND:
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_today_schedule_menu(), message_text=UNKNOWN_FUNCTION_MESSAGE)
    elif which_but == GET_CONTACTS_COMMAND:
        info = utils.read_text_file(CONTACT_INFO_PATH)
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_back_button(), message_text=info ,parse_mode=HTML)
    elif which_but == GET_BOT_INFO_COMMAND:
        info = utils.read_text_file(BOT_INFO_PATH)
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_back_button(), message_text=info ,parse_mode=HTML)
    elif which_but == GET_CALENDAR_COMMAND:
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_calendar_menu(),message_text="📆 Оберіть дату:")
    elif which_but == BACK_TO_ADMIN_COMMAND:
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_dict_menu([admin_menu_buttons]), one_row=True ,message_text=SELECT_COMMAND_PROMPT )
    elif which_but == BACK_TO_MAIN_COMMAND:
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_dict_menu([main_menu_buttons]), one_row=True ,message_text=SELECT_COMMAND_PROMPT )
    elif which_but == CRUD_TEACHER_COMMAND:
        menu = spawn_dict_menu([crud_menu_buttons], crud_entity=TEACHER_ENTITY) 
        menu.append(spawn_back_button(True ,command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(tg_message=call.message, markup_list=menu, one_row=True, message_text="👨‍🏫 Викладачі: ")
    elif which_but == CRUD_SUBJECT_COMMAND:
        menu = spawn_dict_menu([crud_menu_buttons], crud_entity=SUBJECT_ENTITY) 
        menu.append(spawn_back_button(True ,command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(tg_message=call.message, markup_list=menu, one_row=True, message_text="📚 Предмети: ")
        
    elif which_but.startswith(tuple([ADD, EDIT, DELETE])):
        crud_distributor(which_but, tg_message=call.message)
    elif which_but.startswith("day_"):
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_today_schedule_menu(), message_text=UNKNOWN_FUNCTION_MESSAGE)
    elif which_but.startswith(ENTITY_COMMAND):
        entity_button_handler(tg_message=call.message, command_id=which_but)
    elif which_but == IGNORE_COMMAND:
        pass
    else:
        refresh_inline_menu(tg_message=call.message, markup_list=spawn_back_button(), message_text=UNKNOWN_FUNCTION_MESSAGE)

 
# Распеределитель операций CRUD исходя из команды вызывает необходимый хендлер      
def crud_distributor(command:str, tg_message, message_edit:str=True):
    command_obj = Command(command)
    if len(command_obj.entity)==0:
        refresh_inline_menu(tg_message=tg_message, 
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND), 
                            message_text=WRONG_COMMAND_MESSAGE)
    # ADD
    if command_obj.crud_command == ADD:
        if command_obj.entity==TEACHER_ENTITY:
            type_handler(command=command,
                        prompt=TEACHER_ADD_PROPMT, 
                        tg_message=tg_message)
        if command_obj.entity==SUBJECT_ENTITY:
            type_handler(command=command,
                        prompt=SUBJECT_ADD_PROPMT,
                        tg_message=tg_message)
    # EDIT
    if command_obj.crud_command == EDIT:
        if command_obj.entity==TEACHER_ENTITY:
            edit_teacher_handler(tg_message=tg_message, 
                                 full_command=command)
        if command_obj.entity == SUBJECT_ENTITY:
            edit_subject_handler(tg_message=tg_message, full_command=command)
    # DELETE
    if command_obj.crud_command == DELETE:
        if command_obj.entity == TEACHER_ENTITY:
            delete_teacher_handler(tg_message=tg_message, 
                                   entity_id=command_obj.target_entity_id if len(command_obj.target_entity_id) > 0 else None)
        if command_obj.entity == SUBJECT_ENTITY:
            delete_subject_handler(tg_message=tg_message, full_command=command)
            
                
                
            
# Этот хенделр обрабатывает ввод,например вы создаете нового преподавателя, в словарь заноситься ваш
# ТГ-айди и действие которое вы делаете, вы ввели что-то и например в действии прописано создать преподавателя
# выполняется сохранение в базу данных преподователя имя которого вы ввели
@bot.message_handler(func=lambda message:message.chat.id in edit_state)    
def crud_handler(message):
    chat_id = message.chat.id
    try:
        command = edit_state[chat_id]['action']
        del edit_state[chat_id]
        command_obj = Command(command)    
        if command_obj.entity == TEACHER_ENTITY:
            if command_obj.crud_command == ADD:
                r = TeacherDao().create_new_teacher(message.text)
                send_new_message(message_text=r.message,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                                tg_message=message, parse_mode=HTML)
            if command_obj.crud_command == EDIT:
                if len(command_obj.target_entity_id) != 0:
                    r = TeacherDao().edit_teacher(teacher_id=command_obj.target_entity_id, new_name=message.text)
                    send_new_message(message_text=r.message,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                                tg_message=message, parse_mode=HTML)
                    
        if command_obj.entity == SUBJECT_ENTITY:
            if command_obj.crud_command == ADD:
                r = SubjectDao().create_new_subject(subject_name=message.text)
                send_new_message(message_text=r.message,
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND) 
                            if r.is_success==False else None,
                            tg_message=message, parse_mode=HTML)
                
                if(r.is_success == False): return
                new_command = Command()
                new_command.crud_command = EDIT
                new_command.entity = SUBJECT_ENTITY
                new_command.target_entity_id = str(r.data.id)
                new_command.field_name = TEACHERID
                crud_distributor(command=str(new_command), tg_message=message, message_edit=False)
                
            if command_obj.crud_command == EDIT:
                r = SubjectDao().change_subject_name(subject_id=command_obj.target_entity_id,
                                                     subject_name=message.text)
                send_new_message(message_text=r.message,
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                            tg_message=message, parse_mode=HTML)

                                   
    except KeyError as e:
        del edit_state[chat_id]    
        send_new_message(WRONG_COMMAND_MESSAGE, 
                            spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                            tg_message=message)

def spawn_subject_fields_for_edit(subject_id:str):
    buttons=[]
    buttons.append(types.InlineKeyboardButton(text=SUBJECT_NAME_HINT, 
                                              callback_data=f"{EDIT}_{SUBJECT_ENTITY}_{subject_id}_{SUBJECT_NAME}"))
    buttons.append(types.InlineKeyboardButton(text=TEACHERID_HINT, 
                                              callback_data=f"{EDIT}_{SUBJECT_ENTITY}_{subject_id}_{TEACHERID}"))
    return buttons
    
#эта функция обрабатывает кнопки-сущности, динамические кнопки которые создаються когда вы достаёте записи из таблицы бд
def entity_button_handler(tg_message, command_id:str):
    chat_id=tg_message.chat.id
    callback_data = entity_buttons_data.get(chat_id)
    if callback_data == None:
        refresh_inline_menu(tg_message=tg_message,
                            message_text=WRONG_COMMAND_MESSAGE, 
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND))
        return
    command = callback_data.get(command_id)
    if command == None:
        refresh_inline_menu(tg_message=tg_message,
                            message_text=WRONG_COMMAND_MESSAGE, 
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND))
        return
    del entity_buttons_data[chat_id]
    print("COMMAND: ", command)
    crud_distributor(command=command, tg_message=tg_message)
    
    

# Функция отправляет сообщение пользователю вместе с любым маркапом(обычно это кнопка возврата в меню)
# Аргументы и факты: сообщение(ошибка, информация, статус выполнения операции), идентификатор чата(кому отправлять)
def send_new_message(tg_message, message_text:str, markup_list:list=None, parse_mode:str=None ):
    chat_id = tg_message.chat.id
    markup = types.InlineKeyboardMarkup()
    if markup_list != None:
        markup.add(*markup_list, row_width=1)
    bot.send_message(chat_id=chat_id, reply_markup=markup, text=message_text, parse_mode=parse_mode)

# Функция обновляет (освежает:D) сообщение бота, обычно используется
# для того чтобы обновить меню с кнопками, чтобы каждый раз не отправлять обновленное меню новым сообщением
def refresh_inline_menu(tg_message, message_text:str="NOT EMPTY", markup_list:list=None, one_row:bool=False, parse_mode:str=None):
#{
    markup = None
    if markup_list != None:
        markup = types.InlineKeyboardMarkup()
        is_double_list = False
        for mp in markup_list:
            if isinstance(mp, list):
                markup.row(*mp)
                is_double_list = True
        if not is_double_list:
            markup.add(*markup_list, row_width=1 if one_row else None) 
    try: 
        bot.edit_message_text(
            chat_id=tg_message.chat.id,
            message_id=tg_message.message_id,
            text=message_text,
            reply_markup= markup,
            parse_mode= parse_mode,
            disable_web_page_preview=True)
        return True
    except ApiTelegramException as e:
        return False
        
#}

def type_handler(command:str, prompt:str, tg_message):
    chat_id = tg_message.chat.id
    edit_state[chat_id] = {'action':command}
    refresh_inline_menu(tg_message, message_text=prompt, 
                                    markup_list=spawn_back_button(button_text=CANCEL_BUTTON_TEXT, 
                                                                  command_type=BACK_TO_ADMIN_COMMAND))
     
def edit_teacher_handler(tg_message, full_command):
    command = Command(full_command=full_command)
    if len(command.target_entity_id) == 0:
        query = TeacherDao().get_teachers()
        buttons = spawn_teacher_buttons(tg_message=tg_message, query=query, crud_command=EDIT, entity_name=TEACHER_ENTITY)
        button_text = TEACHERS_NOT_FOUND if len(buttons)<=1 else SELECT_TEACHER_EDIT_PROMPT
        refresh_inline_menu(tg_message=tg_message, one_row=True,markup_list=buttons, message_text=button_text, parse_mode=HTML)
    else:
        print("EDIT: ", full_command)
        chat_id = tg_message.chat.id
        edit_state[chat_id] = {'action':full_command}
        refresh_inline_menu(tg_message=tg_message, message_text=TEACHER_EDIT_PROMPT, 
                                    markup_list=spawn_back_button(button_text=CANCEL_BUTTON_TEXT, 
                                                                  command_type=BACK_TO_ADMIN_COMMAND))

def delete_teacher_handler(tg_message, entity_id:str=None):
    if entity_id == None:
        query = TeacherDao().get_teachers()
        buttons = spawn_teacher_buttons(tg_message=tg_message, query=query, crud_command=DELETE, entity_name=TEACHER_ENTITY)
        button_text = TEACHERS_NOT_FOUND if len(buttons)<=1 else SELECT_TEACHER_DEL_PROMPT
        refresh_inline_menu(tg_message=tg_message, one_row=True,markup_list=buttons, message_text=button_text, parse_mode=HTML)
    else:
        r = TeacherDao().delete_teacher(entity_id)
        refresh_inline_menu(tg_message=tg_message, 
                            markup_list=spawn_back_button(
                                command_type=BACK_TO_ADMIN_COMMAND),
                            message_text=r.message, parse_mode=HTML)

def edit_subject_handler(tg_message, full_command):
    command_obj = Command(full_command=full_command)
    if command_obj.field_name == TEACHERID:
        if len(command_obj.selected_id)!=0:
            r = SubjectDao().change_teacher(command_obj.target_entity_id, command_obj.selected_id)
            refresh_inline_menu(tg_message=tg_message, 
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND), 
                                message_text=r.message)
        else:    
            query = TeacherDao().get_teachers()
            buttons = spawn_teacher_buttons(tg_message=tg_message, 
                                            query=query, 
                                            crud_command=EDIT, 
                                            entity_name=SUBJECT_ENTITY, 
                                            field_name=TEACHERID,
                                            target_id=command_obj.target_entity_id)
            button_text = TEACHERS_NOT_FOUND if len(buttons)<=1 else SELECT_TEACHER_TO_SUBJECT_PROMPT
            send_result = refresh_inline_menu(tg_message=tg_message, 
                                    markup_list=buttons, 
                                    one_row=True, 
                                    message_text=button_text, 
                                    parse_mode=HTML)
            if send_result == False:
                send_new_message(tg_message=tg_message, message_text=button_text, markup_list=buttons, parse_mode=HTML)
                
    if command_obj.field_name == SUBJECT_NAME:
        type_handler(command=str(command_obj),prompt=SUBJECT_ADD_PROPMT, tg_message=tg_message)
        
    if command_obj.field_name == ALL_FIELDS:
        query = SubjectDao().get_subject_by_id(command_obj.target_entity_id)
        if query.is_success == False:
            refresh_inline_menu(tg_message=tg_message, 
                                one_row=True,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND), 
                                message_text=query.message, 
                                parse_mode=HTML)
        buttons = spawn_subject_fields_for_edit(subject_id=command_obj.target_entity_id)
        buttons.append(spawn_back_button(return_type=True, 
                                         button_text=CANCEL_BUTTON_TEXT, 
                                         command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(tg_message=tg_message,
                            one_row=True, 
                            message_text=f"{str(query.data)}{FIELD_EDIT_PROMPT}", 
                            markup_list=buttons)
    if len(command_obj.field_name) == 0: 
        query = SubjectDao().get_subjects()
        buttons = spawn_subject_buttons(tg_message=tg_message,
                                            query=query,
                                            crud_command=EDIT, 
                                            entity_name=SUBJECT_ENTITY, 
                                            field_name=ALL_FIELDS)
        button_text = SUBJECTS_NOT_FOUND if len(buttons)<=1 else SELECT_SUBJECT_EDIT_PROMPT
        refresh_inline_menu(tg_message=tg_message, 
                                one_row=True,
                                markup_list=buttons, 
                                message_text=button_text, 
                                parse_mode=HTML)

def delete_subject_handler(tg_message, full_command):
    command_obj = Command(full_command=full_command)
    if len(command_obj.target_entity_id) == 0:
        query = SubjectDao().get_subjects()
        buttons = spawn_subject_buttons(tg_message=tg_message,
                                        query=query,
                                        crud_command=command_obj.crud_command,
                                        entity_name= command_obj.entity)
        button_text = SUBJECTS_NOT_FOUND if len(buttons)<=1 else SELECT_SUBJECT_DEL_PROMPT
        refresh_inline_menu(tg_message=tg_message, 
                            one_row=True,
                            markup_list=buttons, 
                            message_text=button_text, 
                            parse_mode=HTML)    
    else:
        r = SubjectDao().delete_subject(command_obj.target_entity_id)
        refresh_inline_menu(tg_message=tg_message, 
                            markup_list=spawn_back_button(
                                command_type=BACK_TO_ADMIN_COMMAND),
                            message_text=r.message, parse_mode=HTML)


# TODO: создать функцию main где сделать !ВАЖНЫЕ вызовы чтобы бот база данных инициализировались и запустить полинг
if __name__ == '__main__':
    bot.infinity_polling()