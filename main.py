import telebot
import os
import db.init_db as init_db

from db.dao import *
from telebot import types
from dotenv import load_dotenv
from constants import *
from spawner import *
from utils import utils

# TODO: распределить обработчики по файлам
# TODO: добавить логгер и обработчики исключений

init_db.initialize_db()
load_dotenv()


edit_state={}
 
bot = telebot.TeleBot(os.getenv(API_TOKEN))

@bot.message_handler(commands=['start'])
def send_main_menu(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(*spawn_dict_menu([main_menu_buttons]),row_width=1)
    bot.send_message(message.chat.id, "Оберіть одну із команд:", reply_markup=markup)

@bot.message_handler(commands=['admin_menu'])
def send_admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(*spawn_dict_menu([admin_menu_buttons]),row_width=1)
    bot.send_message(message.chat.id, "Оберіть одну із команд:", reply_markup=markup)

# Обработчик АБСОЛЮТНО ВСЕХ инлайн кнопок которые есть в боте, он должен быть только один 
# TODO: разбить это, нечитабельно
@bot.callback_query_handler(func=lambda call: True)
def handle_user_button(call):
    if call.message.chat.id in edit_state:
        del edit_state[call.message.chat.id]
           
    which_but = call.data                                             
    if which_but == GET_SCHEDULE_COMMAND:
        refresh_inline_menu(call.message, spawn_today_schedule_menu(), text=UNKNOWN_FUNCTION_ERROR)
    elif which_but == GET_CONTACTS_COMMAND:
        info = utils.read_text_file(CONTACT_INFO_PATH)
        refresh_inline_menu(call.message, spawn_back_button(), info ,parse_mode=HTML)
    elif which_but == GET_BOT_INFO_COMMAND:
        info = utils.read_text_file(BOT_INFO_PATH)
        refresh_inline_menu(call.message, spawn_back_button(), info ,parse_mode=HTML)
    elif which_but == GET_CALENDAR_COMMAND:
        refresh_inline_menu(call.message, spawn_calendar_menu(),"📆 Оберіть дату:")
    elif which_but == BACK_TO_ADMIN_COMMAND:
        refresh_inline_menu(call.message, spawn_dict_menu([admin_menu_buttons]), one_row=True ,text="Оберіть одну із команд:" )
    elif which_but == BACK_TO_MAIN_COMMAND:
        refresh_inline_menu(call.message, spawn_dict_menu([main_menu_buttons]), one_row=True ,text="Оберіть одну із команд:" )
    elif which_but == CRUD_TEACHER_COMMAND:
        menu = spawn_dict_menu([crud_menu_buttons], crud_entity=TEACHER) 
        menu.append(spawn_back_button(True ,command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(call.message, list_markup=menu, one_row=True, text="👨‍🏫 Викладачі: ")
    elif which_but == CRUD_SUBJECT_COMMAND:
        menu = spawn_dict_menu([crud_menu_buttons], crud_entity=SUBJECT) 
        menu.append(spawn_back_button(True ,command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(call.message, list_markup=menu, one_row=True, text="📚 Предмети: ")
        
    elif which_but.startswith(tuple([ADD, EDIT, DELETE])):
        crud_distributor(which_but, call)
    elif which_but.startswith("day_"):
        refresh_inline_menu(call.message, spawn_today_schedule_menu(), UNKNOWN_FUNCTION_ERROR)
    elif which_but == IGNORE_COMMAND:
        pass
    else:
        refresh_inline_menu(call.message, spawn_back_button(), UNKNOWN_FUNCTION_ERROR)

 
# Распеределитель операций CRUD исходя из команды вызывает необходимый хендлер      
def crud_distributor(command:str, call):
    chat_id = call.message.chat.id
    crud_command = utils.truncate_string(command)
    entity=utils.truncate_string(command, part=1)
    entity_id = utils.truncate_string(command, part=2)
    
    edit_state[chat_id] = {'action':command}
    if len(entity)==0:
        refresh_inline_menu(call.message, 
                            spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND), 
                            text=WRONG_COMMAND_ERROR)
    if entity == TEACHER:
        # TODO: разбить на функции, в дистрибьютере только вызов функций
        if crud_command == ADD:
            refresh_inline_menu(call.message, text="✍ Введіть нове ім'я викладача: ", 
                                    list_markup=spawn_back_button(button_text="❌ Відмінити", 
                                                                  command_type=BACK_TO_ADMIN_COMMAND))
            
        if crud_command == EDIT:
            if len(entity_id) == 0:
                query = TeacherDao().get_teachers()
                buttons=[]
                button_text = None
                if len(query) != 0:
                    button_text = '✍ Оберіть викладача для редагування:'
                    buttons=[spawn_inline_button(button_text=teacher.name,
                                               callback_data=f"{EDIT}_{TEACHER}_{teacher.id}") for teacher in query]
                else:
                    button_text='🙈 Викладачів не знайдено'
                buttons.append(spawn_back_button(return_type=True, command_type=BACK_TO_ADMIN_COMMAND))
                refresh_inline_menu(call.message, one_row=True,list_markup=buttons, text=button_text, parse_mode=HTML)
            else:
                refresh_inline_menu(call.message, text="✍ Введіть нове ім'я викладача: ", 
                                    list_markup=spawn_back_button(button_text="❌ Відмінити", 
                                                                  command_type=BACK_TO_ADMIN_COMMAND))
        
        if crud_command == DELETE:
            if len(entity_id) == 0:
                query = TeacherDao().get_teachers()
                buttons=[]
                button_text = None
                if len(query) != 0:
                    button_text = '❌ Оберіть викладача для видалення:'
                    buttons=[spawn_inline_button(button_text=teacher.name,
                                               callback_data=f"{DELETE}_{TEACHER}_{teacher.id}") for teacher in query]
                else:
                    button_text='🙈 Викладачів не знайдено'
                buttons.append(spawn_back_button(return_type=True, command_type=BACK_TO_ADMIN_COMMAND))
                refresh_inline_menu(call.message, one_row=True,list_markup=buttons, text=button_text, parse_mode=HTML)
            else:
                r = TeacherDao().delete_teacher(entity_id)
                refresh_inline_menu(call.message, 
                                    list_markup=spawn_back_button(
                                        command_type=BACK_TO_ADMIN_COMMAND),
                                    text=r.message, parse_mode=HTML)
    # SUBJECT
    if entity == SUBJECT:
        if crud_command == ADD:
            send_new_message("✍ Введіть назву предмета: ", chat_id=chat_id)
        if crud_command == EDIT:
            query = SubjectDao().get_subjects()
            buttons=[]
            button_text = None
            if len(query) != 0:
                button_text = '✍ Оберіть предмет для редагування:'
                buttons=[spawn_inline_button(button_text=subject.name,
                                           callback_data=f"{EDIT}_{SUBJECT}_{subject.id}") for subject in query]
            else:
                button_text='🙈 Предметів не знайдено'
            buttons.append(spawn_back_button(return_type=True, command_type=BACK_TO_ADMIN_COMMAND))
            refresh_inline_menu(call.message, one_row=True,list_markup=buttons, text=button_text, parse_mode=HTML)

# Этот хенделр обрабатывает ввод,например вы создаете нового преподавателя, в словарь заноситься ваш
# ТГ-айди и действие которое вы делаете, вы ввели что-то и например в действии прописано создать преподавателя
# выполняется сохранение в базу данных преподователя имя которого вы ввели
@bot.message_handler(func=lambda message:message.chat.id in edit_state)    
def crud_handler(message):
    chat_id = message.chat.id
    try:
        command = edit_state[chat_id]['action']
        del edit_state[chat_id]    
        crud_command = utils.truncate_string(command)
        entity=utils.truncate_string(command, part=1)
        entity_id = utils.truncate_string(command, part=2)
        if entity == TEACHER:
            if crud_command == ADD:
                r = TeacherDao().create_new_teacher(message.text)
                send_new_message(message=r.message,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                                chat_id=chat_id, parse_mode=HTML)
            if crud_command == EDIT:
                if len(entity_id) != 0:
                    r = TeacherDao().edit_teacher(teacher_id=entity_id, new_name=message.text)
                    send_new_message(message=r.message,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                                chat_id=chat_id, parse_mode=HTML)
        if entity == SUBJECT:
            if crud_command == ADD:
                r = SubjectDao().create_new_subject(subject_name=message.text)
                send_new_message(message=r.message,
                            markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND) 
                            if r.is_success==True else None,
                            chat_id=chat_id, parse_mode=HTML)
                if(r.is_success == False): return
                query = TeacherDao().get_teachers()
                buttons=[]
                button_text = None
                if len(query) != 0:
                    button_text = '✍ Оберіть викладача для предмета:'
                    buttons=[spawn_inline_button(button_text=teacher.name,
                                               callback_data=f"{EDIT}_{SUBJECT}_{r.data.id}_teacherid_{teacher.id}") 
                             for teacher in query]
                else:
                    button_text='🙈 Викладачів не знайдено'
                buttons.append(spawn_back_button(return_type=True, command_type=BACK_TO_ADMIN_COMMAND))
                refresh_inline_menu(message, one_row=True,list_markup=buttons, text=button_text, parse_mode=HTML)

                                   
    except KeyError as e:
        del edit_state[chat_id]    
        send_new_message(WRONG_COMMAND_ERROR, 
                            spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                            chat_id=chat_id)
   

# Функция отправляет сообщение пользователю вместе с любым маркапом(обычно это кнопка возврата в меню)
# Аргументы и факты: сообщение(ошибка, информация, статус выполнения операции), идентификатор чата(кому отправлять)
def send_new_message(message:str, chat_id:int, markup_list:list=None, parse_mode:str=None ):
    markup = types.InlineKeyboardMarkup()
    if markup_list != None:
        markup.add(*markup_list, row_width=1)
    bot.send_message(chat_id=chat_id, reply_markup=markup, text=message, parse_mode=parse_mode)

# Функция обновляет (освежает:D) сообщение бота, обычно используется
# для того чтобы обновить меню с кнопками, чтобы каждый раз не отправлять обновленное меню новым сообщением
def refresh_inline_menu(message, list_markup:list=None, text='', one_row=False, parse_mode=None):
#{
    markup = None
    if list_markup != None:
        markup = types.InlineKeyboardMarkup()
        is_double_list = False
        for mp in list_markup:
            if isinstance(mp, list):
                markup.row(*mp)
                is_double_list = True
        if not is_double_list:
            markup.add(*list_markup, row_width=1 if one_row else None) 
    bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.message_id,
        text=text,
        reply_markup= markup,
        parse_mode= parse_mode,
        disable_web_page_preview=True
        )
#}

# TODO: создать функцию main где сделать !ВАЖНЫЕ вызовы чтобы бот база данных инициализировались и запустить полинг
if __name__ == '__main__':
    bot.infinity_polling()