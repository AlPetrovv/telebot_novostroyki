"""This is a bot for filling out the client's application"""
import time
from telebot import TeleBot, types
import re
from string import Template
import os

user_dict = {}  # импровизированная база данных, где мы храним данные посетителя в данный момент (замена на sql)

bot = TeleBot(os.getenv("TOKEN"))
CHAT_ID = os.getenv("CHAT_ID")
user = ''
chat_id = ''


class User:  # можно заменить базой данных
    """Class for data processing"""

    def __init__(self, Id):
        self.Id = str(Id)


@bot.message_handler(commands=['start'])
def main(message: types.Message):
    """ function gets a message and gives the user the choice to go the next choice.

    :param message: data of chat, user, ...
    :type message: dict"""
    global user
    global chat_id
    chat_id = str(message.chat.id)
    user = User(message.from_user.id)
    user_dict[user.Id] = {}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    b_inv = types.KeyboardButton('/Инвестиции')
    b_sale = types.KeyboardButton('/Продажа')
    b_pay = types.KeyboardButton('/Покупка')
    markup.add(b_inv, b_sale, b_pay)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}, я бот и ты можешь выбрать следующие действия!',
                     reply_markup=markup)


@bot.message_handler(commands=['Инвестиции'])
def inv(message, *args, **kwargs):
    user_dict.update({user.Id: {inv.__name__: message.text}})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cash = types.KeyboardButton('Наличные')
    mortgage = types.KeyboardButton('Ипотека')
    back = types.KeyboardButton('Назад')
    markup.add(cash, mortgage, back)
    msg = bot.send_message(chat_id,
                           'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, inv_to_cash)
    bot.register_next_step_handler(msg, inv_to_mortgage)
    bot.register_next_step_handler(msg, return_back)


def inv_to_cash(message: types.Message):
    if message.text == 'Наличные':
        user_dict[user.Id].update({inv_to_cash.__name__: message.text})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        back = types.KeyboardButton('Назад')
        markup.add(back)
        msg = bot.send_message(chat_id,
                               'Введите сумму и ваш контактный номер, чтобы мы могли связаться с вами в формате:'
                               '123456789;81234567890', reply_markup=markup)  # РАЗДЕЛИТЬ НА 2 ФУНКЦИИ
        bot.register_next_step_handler(msg, cheсk_inv_to_cash)


def cheсk_inv_to_cash(message: types.Message):
    """function gets a message,  checks it and sends data to the telegram channel"""
    user_dict[user.Id].update({cheсk_inv_to_cash.__name__: message.text})
    try:
        if len(re.findall(r'\d+;\d{11,12}', message.text)) != 1:
            if message.text == 'Назад':
                return_back(message)
            else:
                bot.send_message(chat_id,
                                 'Неправильный ввод данных, попробуйте снова')
                message.text = "Наличные"
                transition_to_cash(message)

        else:
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_inv_to_cash(user_dict, 'Заявка от бота', bot.get_me().username,
                                                        message.from_user.first_name),
                             parse_mode='Markdown')

    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_inv_to_cash(data, title, bot_name, username):
    """function of decorating the output of strings in the telegram channel"""
    temp = Template(
        '$title *$bot_name* \n Пользователь: *$username* \n Выбор пункта 1: *$investment* \n '
        'Выбор пункта 2: *inv_to_cash* \n Данные : *$check_inv_to_cash*')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'investment': data[user.Id][inv.__name__],
        'inv_to_cash': data[user.Id][inv_to_cash.__name__],
        'check_inv_to_cash': data[user.Id][cheсk_inv_to_cash.__name__]
    })


def inv_to_mortgage(message):
    if message.text == 'Ипотека':
        user_dict[user.Id].update({inv_to_mortgage.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли связаться с вами: (Пример: 40000000;1000000;15000;79...), '
                               'если хотите вернуться, напишите back', reply_markup=markup)
        bot.register_next_step_handler(msg, check_inv_to_mortgage)


def check_inv_to_mortgage(message):
    try:
        if len(re.findall(r'\d+;\d+;\d+;\d{11,12}', message.text)) != 1:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            print(message.text)
            message.text = "Ипотека"
            transition_to_mortgage(message)
        else:
            user_dict[user.Id].update({check_inv_to_mortgage.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID, get_data_user_inv_mortgage(user_dict, 'Заявка от бота', bot.get_me().username,
                                                                 message.from_user.first_name, ))

    except Exception:
        message.text = 'Назад'
        return_back(message)


def get_data_user_inv_mortgage(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\nПользователь: *$username*\nВыбор пункта 1: *$inv*\nВыбор пункта 2: *$inv_to_mortgage*\n'
        'Данные: *$check_inv_to_mortgage*')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'inv': data[user.Id][inv.__name__],
        'inv_to_mortgage': data[user.Id][inv_to_mortgage.__name__],
        'check_inv_to_mortgage': data[user.Id][check_inv_to_mortgage.__name__]
    })


def return_back(message):
    if message.text == 'Назад':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        b_inv = types.KeyboardButton('/Инвестиции')
        b_sale = types.KeyboardButton('/Продажа')
        b_buy = types.KeyboardButton('/Покупка')
        markup.add(b_inv, b_sale, b_buy)
        bot.send_message(chat_id, 'Хорошо, давайте начнем заново'.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['Покупка'])
def buy(message):
    user_dict.update({user.Id: {buy.__name__: message.text}})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    secondary = types.KeyboardButton('Вторичка')
    new_building = types.KeyboardButton('Новостройка')
    back = types.KeyboardButton('Назад')
    markup.add(secondary, new_building, back)
    msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, buy_to_secondary)
    bot.register_next_step_handler(msg, buy_to_new)
    bot.register_next_step_handler(msg, return_back)


def buy_to_secondary(message):
    if message.text == 'Вторичка':
        user_dict[user.Id].update({buy_to_secondary.__name__: message.text})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mortgage = types.KeyboardButton('Ипотека')
        cash = types.KeyboardButton('Наличные')
        back = types.KeyboardButton('Назад')
        markup.add(mortgage, cash, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, buy_to_secondary_mortgage)
        bot.register_next_step_handler(msg, buy_to_secondary_cash)
        bot.register_next_step_handler(msg, return_back)


def buy_to_secondary_mortgage(message):
    if message.text == 'Ипотека':
        user_dict[user.Id].update({buy_to_secondary_mortgage.__name__: message.text})
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли связаться с вами:(Пример: 40000000;1000000;15000;79...)')
        bot.register_next_step_handler(msg, check_buy_to_secondary_mortgage)


def check_buy_to_secondary_mortgage(message):
    try:
        if len(re.findall(r'\d+;\d+;\d+;\d{11,12}', message.text)) != 1:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Ипотека"
            buy_to_secondary_mortgage(message)

        else:
            user_dict[user.Id].update({check_buy_to_secondary_mortgage.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_secondary_mortgage(user_dict, 'Заявка от бота', bot.get_me().username,
                                                               message.from_user.first_name), parse_mode='Markdown')
    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_secondary_mortgage(data, title, name, username):
    temp = Template(
        '$title *$name* \n Пользователь: *$username* \n Выбор пункта 1: *$buy* \n Выбор пункта 2: *$buy_to_secondary*'
        '\nВыбор пункта 3: *$buy_to_secondary_mortgage*\nДанные: *$check_buy_to_secondary_mortgage* ')
    return temp.substitute({
        'title': title,
        'name': name,
        'username': username,
        'buy': data[user.Id][buy.__name__],
        'buy_to_secondary': data[user.Id][buy_to_secondary.__name__],
        'buy_to_secondary_mortgage': data[user.Id][buy_to_secondary_mortgage.__name__],
        'check_buy_to_secondary_mortgage': data[user.Id][check_buy_to_secondary_mortgage.__name__]
    })


def buy_to_secondary_cash(message):
    if message.text == 'Наличные':
        user_dict[user.Id].update({buy_to_secondary_cash.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, комфортный платеж и ваш контактный номер, чтобы мы могли связаться '
                               'с вами:(Пример: 40000000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, check_buy_to_secondary_cash)


def check_buy_to_secondary_cash(message):
    try:
        if len(re.findall(r'\d+;\d{11,12}', message.text)) != 1:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Наличные"
            buy_to_secondary_cash(message)
        else:
            user_dict[user.Id].update({check_buy_to_secondary_cash.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_secondary_cash(user_dict, 'Заявка от бота', bot.get_me().username,
                                                           message.from_user.first_name), parse_mode='Markdown')

    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def send_data_user_secondary_cash(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\n Пользователь: *$username*\nВыбор пункта 1: *$buy*\n'
        'Выбор пункта 2: *$buy_to_secondary*\nВыбор пункта 3: '
        '*$buy_to_secondary_cash*\nДанные: *$check_buy_to_secondary_cash* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'buy': data[user.Id][buy.__name__],
        'buy_to_secondary': data[user.Id][buy_to_secondary.__name__],
        'buy_to_secondary_cash': data[user.Id][buy_to_secondary_cash.__name__],
        'check_buy_to_secondary_cash': data[user.Id][check_buy_to_secondary_cash.__name__]
    })


def buy_to_new(message):
    if message.text == 'Новостройка':
        user_dict[user.Id].update({buy_to_new.__name__: message.text})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mortgage = types.KeyboardButton('Ипотека')
        cash = types.KeyboardButton('Наличные')
        back = types.KeyboardButton('Назад')
        markup.add(mortgage, cash, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, buy_to_new_mortgage)
        bot.register_next_step_handler(msg, buy_to_new_cash)
        bot.register_next_step_handler(msg, return_back)


def buy_to_new_mortgage(message):
    if message.text == 'Ипотека':
        user_dict[user.Id].update({buy_to_new_mortgage.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли связаться с вами:(Пример: 40000000;1000000;15000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, check_buy_to_new_mortgage)


def check_buy_to_new_mortgage(message):
    try:
        if len(re.findall(r'\d+;\d+;\d+;\d{11,12}', message.text)) != 1:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Ипотека"
            buy_to_new_mortgage(message)

        else:
            user_dict[user.Id].update({check_buy_to_new_mortgage.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_new_mortgage(user_dict, 'Заявка от бота', bot.get_me().username,
                                                         message.from_user.first_name), parse_mode='Markdown')
    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_new_mortgage(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\nПользователь: *$username*\nВыбор пункта 1: *$buy*\nВыбор пункта 2: *$buy_to_new*\n'
        'Выбор пункта 3: *$buy_to_new_mortgage*\nДанные: *$check_buy_to_new_mortgage* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'buy': data[user.Id][buy.__name__],
        'buy_to_new': data[user.Id][buy_to_new.__name__],
        'buy_to_new_mortgage': data[user.Id][buy_to_new_mortgage.__name__],
        'check_buy_to_new_mortgage': data[user.Id][check_buy_to_new_mortgage.__name__]
    })


def buy_to_new_cash(message):
    if message.text == 'Наличные':
        user_dict[user.Id].update({buy_to_new_cash.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму и ваш контактный номер, чтобы мы могли взязаться с вами:'
                               '(Пример: 40000000;79...)', reply_markup=markup)
        bot.register_next_step_handler(msg, check_buy_to_new_cash)


def check_buy_to_new_cash(message):
    try:
        if len(re.findall(r'\d+;\d{11,12}', message.text)) != 1:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Наличные"
            buy_to_new_cash(message)

        else:
            user_dict[user.Id].update({check_buy_to_new_cash.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_new_cash(user_dict, 'Заявка от бота', bot.get_me().username,
                                                     message.from_user.first_name), parse_mode='Markdown')
    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_new_cash(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\nПользователь: *$username*\nВыбор пункта 1: *$buy*\nВыбор пункта 2: *$buy_to_new*\n'
        'Выбор пункта 3: *$buy_to_new_cash*\nДанные: *$check_buy_to_new_cash* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'buy': data[user.Id][buy.__name__],
        'buy_to_new': data[user.Id][buy_to_new.__name__],
        'buy_to_new_cash': data[user.Id][buy_to_new_cash.__name__],
        'check_buy_to_new_cash': data[user.Id][check_buy_to_new_cash.__name__]
    })


@bot.message_handler(commands=['Продажа'])
def sale(message):
    user_dict.update({user.Id: {sale.__name__: message.text}})
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exchange = types.KeyboardButton('Обмен')
    valuation = types.KeyboardButton('Оценка')
    back = types.KeyboardButton('Назад')
    markup.add(exchange, valuation, back)
    msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, sale_to_exchange)
    bot.register_next_step_handler(msg, sale_to_valuation)
    bot.register_next_step_handler(msg, return_back)


def sale_to_exchange(message):
    if message.text == 'Обмен':
        user_dict[user.Id].update({sale_to_exchange.__name__: message.text})
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        secondary = types.KeyboardButton('Вторичка')
        new_building = types.KeyboardButton('Новостройка')
        back = types.KeyboardButton('Назад')
        markup.add(secondary, new_building, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, sale_to_exchange_secondary)
        bot.register_next_step_handler(msg, sale_to_exchange_new)
        bot.register_next_step_handler(msg, return_back)


def sale_to_exchange_secondary(message):
    if message.text == 'Вторичка':
        user_dict[user.Id].update({sale_to_exchange_secondary.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли взязаться с вами:'
                               '(Пример: НСК; красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, check_sale_to_exchange_secondary)


def check_sale_to_exchange_secondary(message):
    try:
        if re.search(r'[А-ЯЁа-яё]+;[\dА-ЯЁа-яё\s]+;[\dА-ЯЁа-яё\s]+;\d{11,12}', message.text).group() is None:
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Вторичка"
            sale_to_exchange_secondary(message)

        else:
            user_dict[user.Id].update({check_sale_to_exchange_secondary.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_exchange_secondary(user_dict, 'Заявка от бота', bot.get_me().username,
                                                               message.from_user.first_name), parse_mode='Markdown')
    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_exchange_secondary(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\nПользователь: *$username*\nВыбор пункта 1: *$sale* \n Выбор пункта 2: '
        '*sale_to_exchange*\nВыбор пункта 3: *sale_to_exchange_secondary*\nДанные: *check_sale_to_exchange_secondary* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'sale': data[user.Id][sale.__name__],
        'sale_to_exchange': data[user.Id][sale_to_exchange.__name__],
        'sale_to_exchange_secondary': data[user.Id][sale_to_exchange_secondary.__name__],
        'check_sale_to_exchange_secondary': data[user.Id][check_sale_to_exchange_secondary.__name__]
    })


def sale_to_exchange_new(message):
    if message.text == 'Новостройка':
        user_dict[user.Id].update({sale_to_exchange_new.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли взязаться с вами:'
                               '(Пример: НСК; красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, check_sale_to_exchange_new)


def check_sale_to_exchange_new(message):
    try:
        if not re.search(r'[А-ЯЁа-яё]+;[\dА-ЯЁа-яё\s]+;[\dА-ЯЁа-яё\s]+;\d{11,12}', message.text).group():
            bot.send_message(chat_id, 'Неправильный ввод данных, попробуйте снова', parse_mode='Markdown')
            message.text = "Новостройка"
            sale_to_exchange_new(message)

        else:
            user_dict[user.Id].update({check_sale_to_exchange_new.__name__: message.text})
            bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊',
                             parse_mode='Markdown')
            bot.send_message(CHAT_ID,
                             send_data_user_exchange_new(user_dict, 'Заявка от бота', bot.get_me().username,
                                                         message.from_user.first_name), parse_mode='Markdown')
    except Exception:
        message.text = 'Назад'
        return_back(message)


def send_data_user_exchange_new(data, title, bot_name, username):
    temp = Template(
        '$title *$bot_name*\nПользователь: *$username*\nВыбор пункта 1: *$sale*\nВыбор пункта 2: *sale_to_exchange*\n'
        'Выбор пункта 3: *sale_to_exchange_new*\nДанные: *check_sale_to_exchange_new* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'sale': data[user.Id][sale.__name__],
        'sale_to_exchange': data[user.Id][sale_to_exchange.__name__],
        'sale_to_exchange_new': data[user.Id][sale_to_exchange_new.__name__],
        'check_sale_to_exchange_new': data[user.Id][check_sale_to_exchange_new.__name__]
    })


def sale_to_valuation(message):
    if message.text == 'Оценка':
        user_dict[user.Id].update({sale_to_valuation.__name__: message.text})
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли связаться с вами:'
                               '(Пример: НСК, красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, check_sale_to_valuation)


def check_sale_to_valuation(message):
    try:
        user_dict[user.Id].update({check_sale_to_valuation.__name__: message.text})
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, send_data_user_valuation(user_dict, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def send_data_user_valuation(data, title, bot_name):
    temp = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$sale*  \n Выбор пункта 2: *sale_to_valuation* \n '
        'Данные: *check_sale_to_valuation* ')
    return temp.substitute({
        'title': title,
        'bot_name': bot_name,
        'sale': data[user.Id][sale.__name__],
        'sale_to_valuation': data[user.Id][sale_to_valuation.__name__],
        'check_sale_to_valuation': data[user.Id][check_sale_to_valuation.__name__]
    })


bot.polling(none_stop=True)
if __name__ == '__main__':
    main()
