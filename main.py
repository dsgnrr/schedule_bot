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
print([f"{teacher.name}_{teacher.id}" for teacher in TeacherDao().get_teachers()])
 
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
        refresh_inline_menu(call, change_menu(TODAY_SCHEDULE_MENU, message=call.message),text=UNKNOWN_FUNCTION_ERROR)
    elif which_but == GET_CONTACTS_COMMAND:
        info = read_text_file(CONTACT_INFO_PATH)
        refresh_inline_menu(call, change_menu(BACK_MENU, message=call.message),info ,parse_mode="html")
    elif which_but == GET_BOT_INFO_COMMAND:
        info = read_text_file(BOT_INFO_PATH)
        refresh_inline_menu(call, change_menu(BACK_MENU, message=call.message),info ,parse_mode="html")
    elif which_but == GET_CALENDAR_COMMAND:
        refresh_inline_menu(call, change_menu(CALENDAR_MENU, message=call.message),"📆 Оберіть дату:")
    elif which_but == BACK_TO_ADMIN_COMMAND:
        refresh_inline_menu(call, change_menu(ADMIN_MENU, message=call.message), one_row=True ,text="Оберіть одну із команд:" )
    elif which_but == BACK_TO_MAIN_COMMAND:
        refresh_inline_menu(call, change_menu(MAIN_MENU, message=call.message), one_row=True ,text="Оберіть одну із команд:" )
    elif which_but == CRUD_TEACHER_COMMAND:
        menu = change_menu(CRUD_TEACHER_MENU)
        menu.append(spawn_back_button(True ,command_type=BACK_TO_ADMIN_COMMAND))
        refresh_inline_menu(call, list_markup=menu, one_row=True, text="👨‍🏫 Викладачі: ")
        
    elif which_but.startswith(tuple([ADD, EDIT, DELETE])):
        crud_distributor(which_but, call)
    elif which_but.startswith("day_"):
        refresh_inline_menu(call, change_menu(TODAY_SCHEDULE_MENU, message=call.message), UNKNOWN_FUNCTION_ERROR)
    elif which_but == IGNORE_COMMAND:
        pass
    else:
        refresh_inline_menu(call, change_menu(BACK_MENU), UNKNOWN_FUNCTION_ERROR)

 
# Распеределитель операций CRUD исходя из команды вызывает необходимый хендлер      
def crud_distributor(command:str, call):
    chat_id = call.message.chat.id
    crud_command = utils.truncate_string(command)
    entity=utils.truncate_string(command, part=1)
    entity_id = utils.truncate_string(command, part=2)
    if len(entity)==0:
        refresh_inline_menu(call, 
                            spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND), 
                            text=WRONG_COMMAND_ERROR)
    if entity == TEACHER:
        if crud_command == ADD:
            send_new_message("✍ Введіть ім'я викладача: ", chat_id=chat_id)
            edit_state[chat_id] = {'action':command}
        # TODO: разбить на функции, в дистрибьютере только вызов функций
        if crud_command == DELETE:
            if len(entity_id) == 0:
                query = TeacherDao().get_teachers()
                buttons=[]
                button_text = ''
                if len(query) != 0:
                    button_text = '❌ Видалити викладача:'
                    buttons=[spawn_inline_button(button_text=teacher.name,
                                               callback_data=f"{DELETE}_{TEACHER}_{teacher.id}") for teacher in query]
                else:
                    button_text='🙈 Викладачів не знайдено'
                buttons.append(spawn_back_button(return_type=True, command_type=BACK_TO_ADMIN_COMMAND))
                refresh_inline_menu(call, one_row=True,list_markup=buttons, text=button_text)
            else:
                del_result = TeacherDao().delete_teacher(entity_id)
                refresh_inline_menu(call, list_markup=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),text=del_result.message)


# Этот хенделр обрабатывает ввод,например вы создаете нового преподавателя, в словарь заноситься ваш
# ТГ-айди и действие которое вы делаете, вы ввели что-то и например в действии прописано создать преподавателя
# выполняется сохранение в базу данных преподователя имя которого вы ввели
@bot.message_handler(func=lambda message:message.chat.id in edit_state)    
def crud_handler(message):
    chat_id = message.chat.id
    try:
        command = edit_state[chat_id]['action']
        if command == f"{ADD}_{TEACHER}":
            r = TeacherDao().create_new_teacher(message.text)
            send_new_message(message=r.message,
                                markup_list=spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                                chat_id=chat_id)
            
    except KeyError as e:
        send_new_message(WRONG_COMMAND_ERROR, 
                            spawn_back_button(command_type=BACK_TO_ADMIN_COMMAND),
                            chat_id=chat_id)
    del edit_state[chat_id]    

# Функция отправляет сообщение пользователю вместе с любым маркапом(обычно это кнопка возврата в меню)
# Аргументы и факты: сообщение(ошибка, информация, статус выполнения операции), идентификатор чата(кому отправлять)
def send_new_message(message:str, chat_id:int, markup_list:list=None ):
    markup = types.InlineKeyboardMarkup()
    if markup_list != None:
        markup.add(*markup_list, row_width=1)
    bot.send_message(chat_id=chat_id, reply_markup=markup, text=message)

# Функция обновляет (освежает:D) сообщение бота, обычно используется
# для того чтобы обновить меню с кнопками, чтобы каждый раз не отправлять обновленное меню новым сообщением
def refresh_inline_menu(call, list_markup:list, text='', one_row=False, parse_mode=None):
#{
    markup = types.InlineKeyboardMarkup()
    is_double_list = False
    for mp in list_markup:
        if isinstance(mp, list):
            markup.row(*mp)
            is_double_list = True
    if not is_double_list:
        markup.add(*list_markup, row_width=1 if one_row else None) 
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup= markup,
        parse_mode= parse_mode,
        disable_web_page_preview=True
        )
#}

# по названию меню возвращает список элементов с кнопками нужного меню

def change_menu(menu_name, message=None):
    if menu_name == MAIN_MENU:
        return spawn_dict_menu([main_menu_buttons])
    if menu_name == ADMIN_MENU:
        return spawn_dict_menu([admin_menu_buttons])
    elif menu_name == BACK_MENU:
        return spawn_back_button()
    elif menu_name == CALENDAR_MENU:
        return spawn_calendar_menu()
    elif menu_name == TODAY_SCHEDULE_MENU:
        return spawn_today_schedule_menu()   
    elif menu_name == CRUD_TEACHER_MENU:
        return spawn_dict_menu([crud_menu_buttons], crud_entity=TEACHER) 

# это утилита(значит надо вынести её нахуй в другой файл не так ли)
def read_text_file(env_path):
    try:
        base_dir = os.path.dirname(__file__)
        text_file_path = os.getenv(env_path)
        if not text_file_path:
            return UNKNOWN_FUNCTION_ERROR
        file_path = os.path.join(os.path.join(base_dir, "wwwroot"), text_file_path)
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден по пути {file_path}. {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка при чтении файла: {e}")
    return UNKNOWN_FUNCTION_ERROR

# TODO: создать функцию main где сделать !ВАЖНЫЕ вызовы чтобы бот база данных инициализировались и запустить полинг
if __name__ == '__main__':
    bot.infinity_polling()