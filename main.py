"""telebot: Модуль для работы с телеграмм; string: Модуль для работы со строками(шаблоны) """
import telebot
from telebot import types
from string import Template
import os

user_dict = {}  # импровизированная база данных, где мы храним данные посетителя в данный момент (замена на sql)

bot = telebot.TeleBot(os.getenv("TOKEN"))
CHAT_ID = os.getenv("CHAT_ID")


def main():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    starts = types.KeyboardButton('/start')
    markup.add(starts)


class User:  # можно заменить базой данных
    """Class for data processing"""

    def __init__(self, data):
        self.data = data
        # Доделать
        # keys = ['invest', 'invest_cash', 'invest_cash_reg', 'mortgage_reg', 'mortgage', 'buy', 'buy_secondary',
        #         'buy_secondary_mortgage', 'buy_secondary_mortgage_reg', 'buy_secondary_cash', 'buy_secondary_cash_reg'
        #         , 'buy_newBuilding', 'buy_newBuilding_mortgage',  'buy_newBuilding_cash',
        #         'buy_newBuilding_cash_reg', 'buy_newBuilding_mortgage_reg', 'sale', 'sale_exchange',
        #         'sale_exchange_secondary', 'sale_exchange_newBuilding', 'sale_exchange_secondary_reg',
        #         'sale_exchange_newBuilding_reg', 'sale_valuation', 'sale_valuation_reg']
        # for key in keys:
        #     self.key = None


@bot.message_handler(commands=['start'])
def start(message):
    """ function gets a message and gives the user the choice to go the next choice.

    :param message: data of chat, user, ...
    :type message: dict"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    inv = types.KeyboardButton('/Инвестиции')
    sale = types.KeyboardButton('/Продажа')
    pay = types.KeyboardButton('/Покупка')
    markup.add(inv, sale, pay)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}, я бот и ты можешь выбрать следующие действия !',
                     reply_markup=markup)


@bot.message_handler(commands=['Инвестиции'])
def choice_inv(message):
    chat_id = message.chat.id  # id чата(не пользователя)
    user_dict[chat_id] = User(message.text)
    user = user_dict[chat_id]
    user.invest = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    cash = types.KeyboardButton('Наличные')
    mortgage = types.KeyboardButton('Ипотека')
    back = types.KeyboardButton('Назад')
    markup.add(cash, mortgage, back)
    msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, transition_to_cash)
    bot.register_next_step_handler(msg, transition_to_mortgage)
    bot.register_next_step_handler(msg, return_back)


def transition_to_cash(message):
    if message.text == 'Наличные':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.invest_cash = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму и ваш контактный номер, чтобы мы могли связаться с вами:'
                               '(Пример: 40000000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, cheking_transition_to_cash)


def cheking_transition_to_cash(message):  # добавить регулярное выражение
    """function gets a message,  checks it and sends data to the telegram channel"""
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.invest_cash_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID,
                         get_data_user_inv_cash(user, 'Заявка от бота', bot.get_me().username,
                                                message.from_user.first_name),
                         parse_mode='Markdown')
    # except Exception as e:
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def get_data_user_inv_cash(user, title, bot_name, username):
    """function of decorating the output of strings in the telegram channel"""
    t = Template(
        '$title *$bot_name* \n Имя: *$username* \n Выбор пункта 1: *$invest* \n Выбор пункта 2: *$invest_cash* '
        '\n Данные : *$invest_cash_reg*')
    return t.substitute({
        'title': title,
        'bot_name': bot_name,
        'username': username,
        'invest': user.invest,
        'invest_cash': user.invest_cash,
        'invest_cash_reg': user.invest_cash_reg
    })


def transition_to_mortgage(message):
    if message.text == 'Ипотека':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.mortgage = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли взязаться с вами :(Пример: 40000000;1000000;15000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_mortgage)


def checking_transition_to_mortgage(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.mortgage_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_inv_mortgage(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def get_data_user_inv_mortgage(user, title, bot_name):
    s = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$invest* \n Выбор пункта 2: *$mortgage* \n Данные : *$mortgage_reg*')
    return s.substitute({
        'title': title,
        'bot_name': bot_name,
        'invest': user.invest,
        'mortgage': user.mortgage,
        'mortgage_reg': user.mortgage_reg
    })


def return_back(message):
    if message.text == 'Назад':
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        inv = types.KeyboardButton('/Инвестиции')
        sale = types.KeyboardButton('/Продажа')
        buy = types.KeyboardButton('/Покупка')
        markup.add(inv, sale, buy)
        bot.send_message(chat_id, 'Хорошо, давайте начнем заново'.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['Покупка'])
def choice_buy(message):
    chat_id = message.chat.id
    user_dict[chat_id] = User(message.text)
    user = user_dict[chat_id]
    user.buy = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    secondary = types.KeyboardButton('Вторичка')
    new_building = types.KeyboardButton('Новостройка')
    back = types.KeyboardButton('Назад')
    markup.add(secondary, new_building, back)
    msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, transition_to_secondary)
    bot.register_next_step_handler(msg, transition_to_new)
    bot.register_next_step_handler(msg, back2)  # заменить на return_back


def transition_to_secondary(message):
    if message.text == 'Вторичка':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_secondary = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mortgage = types.KeyboardButton('Ипотека')
        cash = types.KeyboardButton('Наличные')
        back = types.KeyboardButton('Назад')
        markup.add(mortgage, cash, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, transition_to_secondary_mortgage)
        bot.register_next_step_handler(msg, transition_to_secondary_cash)
        bot.register_next_step_handler(msg, back2)


def transition_to_secondary_mortgage(message):
    if message.text == 'Ипотека':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_secondary_mortgage = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли взязаться с вами:(Пример: 40000000;1000000;15000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_secondary_mortgage)


def checking_transition_to_secondary_mortgage(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_secondary_cash_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID,
                         get_data_user_secondary_mortgage(user, 'Заявка от бота', bot.get_me().username,
                                                          message.from_user.username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def get_data_user_secondary_mortgage(user, title, name, username):
    f = Template(
        '$title *$name* \n Никнейм пользователя: *$username*  \n Выбор пункта 1: *$buy* \n Выбор пункта 2: '
        '*$buy_secondary* \n Выбор пункта 3: *$buy_secondary_cash* \n Данные: *$buy_secondary_cash_reg* ')
    return f.substitute({
        'title': title,
        'name': name,
        'username': username,
        'buy': user.buy,
        'buy_secondary': user.buy_secondary,
        'buy_secondary_cash': user.buy_secondary_cash,
        'buy_secondary_cash_reg': user.buy_secondary_cash_reg
    })


def transition_to_secondary_cash(message):
    if message.text == 'Наличные':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_secondary_cash = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, комфортный платеж и ваш контактный номер, чтобы мы могли связаться '
                               'с вами:(Пример: 40000000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_secondary_cash)


def checking_transition_to_secondary_cash(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_secondary_mortgage_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_secondary_cash(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def get_data_user_secondary_cash(user, title, bot_name):
    s = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$buy* \n Выбор пункта 2: *$buy_secondary* \n Выбор пункта 3: '
        '*$buy_secondary_mortgage* \n Данные: *$buy_secondary_mortgage_reg* ')
    return s.substitute({
        'title': title,
        'bot_name': bot_name,
        'buy': user.buy,
        'buy_secondary': user.buy_secondary,
        'buy_secondary_mortgage': user.buy_secondary_mortgage,
        'buy_secondary_mortgage_reg': user.buy_secondary_mortgage_reg
    })


def transition_to_new_mortgage(message):
    if message.text == 'Ипотека':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_newBuilding_mortgage = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите сумму, первоначальный взнос, комфортный платеж и ваш контактный номер, '
                               'чтобы мы могли взязаться с вами:(Пример: 40000000;1000000;15000;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_new_mortgage)


def transition_to_new(message):
    if message.text == 'Новостройка':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_newBuilding = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        mortgage = types.KeyboardButton('Ипотека')
        cash = types.KeyboardButton('Наличные')
        back = types.KeyboardButton('Назад')
        markup.add(mortgage, cash, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, transition_to_new_mortgage)
        bot.register_next_step_handler(msg, transition_to_new_cash)
        bot.register_next_step_handler(msg, back2)  # change to return_step


def transition_to_new_cash(message):
    if message.text == 'Наличные':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_newBuilding_cash = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg1 = bot.send_message(chat_id,
                                'Введите сумму и ваш контактный номер, чтобы мы могли взязаться с вами:'
                                '(Пример: 40000000;79...)',
                                reply_markup=markup)
        bot.register_next_step_handler(msg1, checking_transition_to_new_cash)


def checking_transition_to_new_mortgage(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_newBuilding_mortgage_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_new_mortgage(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def checking_transition_to_new_cash(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.buy_newBuilding_cash_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_new_cash(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def back2(message):
    if message.text == 'Назад':
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        one = types.KeyboardButton('/Инвестиции')
        two = types.KeyboardButton('/Продажа')
        three = types.KeyboardButton('/Покупка')

        markup.add(one, two, three)
        bot.send_message(chat_id, 'Хорошо, давайте начнем заново'.format(message.from_user), reply_markup=markup)


def get_data_user_new_mortgage(user, title, bot_name):
    f = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$buy* \n Выбор пункта 2: *$buy_newBuilding* \n '
        'Выбор пункта 3: *$buy_newBuilding_mortgage* \n Данные: *$buy_newBuilding_mortgage_reg* ')
    return f.substitute({
        'title': title,
        'bot_name': bot_name,
        'buy': user.buy,
        'buy_newBuilding': user.buy_newBuilding,
        'buy_newBuilding_mortgage': user.buy_newBuilding_mortgage,
        'buy_newBuilding_mortgage_reg': user.buy_newBuilding_mortgage_reg
    })


def get_data_user_new_cash(user, title, bot_name):
    f = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$buy* \n Выбор пункта 2: *$buy_newBuilding* \n '
        'Выбор пункта 3: *$buy_newBuilding_cash* \n Данные: *$buy_newBuilding_cash_reg* ')
    return f.substitute({
        'title': title,
        'bot_name': bot_name,
        'buy': user.buy,
        'buy_newBuilding': user.buy_newBuilding,
        'buy_newBuilding_cash': user.buy_newBuilding_cash,
        'buy_newBuilding_cash_reg': user.buy_newBuilding_cash_reg
    })


@bot.message_handler(commands=['Продажа'])
def choice_sale(message):
    chat_id = message.chat.id
    user_dict[chat_id] = User(message.text)
    user = user_dict[chat_id]
    user.sale = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    exchange = types.KeyboardButton('Обмен')
    valuation = types.KeyboardButton('Оценка')
    back = types.KeyboardButton('Назад')
    markup.add(exchange, valuation, back)
    msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
    bot.register_next_step_handler(msg, transition_to_exchange)
    bot.register_next_step_handler(msg, transition_to_valuation)
    bot.register_next_step_handler(msg, back3)


def transition_to_exchange(message):
    if message.text == 'Обмен':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_exchange = message.text
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        secondary = types.KeyboardButton('Вторичка')
        new_building = types.KeyboardButton('Новостройка')
        back = types.KeyboardButton('Назад')
        markup.add(secondary, new_building, back)
        msg = bot.send_message(chat_id, 'Продолжим', reply_markup=markup)
        bot.register_next_step_handler(msg, transition_to_exchange_secondary)
        bot.register_next_step_handler(msg, transition_to_exchange_new)
        bot.register_next_step_handler(msg, back3)


def transition_to_exchange_secondary(message):
    if message.text == 'Вторичка':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_exchange_secondary = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли взязаться с вами:'
                               '(Пример: НСК, красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_exchange_secondary)


def transition_to_exchange_new(message):
    if message.text == 'Новостройка':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_exchange_newBuilding = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли взязаться с вами:'
                               '(Пример: НСК, красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_exchange_new)


def checking_transition_to_exchange_secondary(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_exchange_secondary_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_exchange_secondary(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def checking_transition_to_exchange_new(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_exchange_newBuilding_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_exchange_new(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def get_data_user_exchange_secondary(user, title, bot_name):
    u = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$sale* \n Выбор пункта 2: *$sale_exchange* \n '
        'Выбор пункта 3: *$sale_exchange_secondary* \n Данные: *$sale_exchange_secondary_reg* ')
    return u.substitute({
        'title': title,
        'bot_name': bot_name,
        'sale': user.sale,
        'sale_exchange': user.sale_exchange,
        'sale_exchange_secondary': user.sale_exchange_secondary,
        'sale_exchange_secondary_reg': user.sale_exchange_secondary_reg
    })


def get_data_user_exchange_new(user, title, bot_name):
    i = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$sale* \n Выбор пункта 2: *$sale_exchange* \n '
        'Выбор пункта 3: *$sale_exchange_newBuilding* \n Данные: *$sale_exchange_newBuilding_reg* ')
    return i.substitute({
        'title': title,
        'bot_name': bot_name,
        'sale': user.sale,
        'sale_exchange': user.sale_exchange,
        'sale_exchange_newBuilding': user.sale_exchange_newBuilding,
        'sale_exchange_newBuilding_reg': user.sale_exchange_newBuilding_reg
    })


def transition_to_valuation(message):
    if message.text == 'Оценка':
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_valuation = message.text
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id,
                               'Введите адрес, площадь в м2 и ваш контактный номер, чтобы мы могли сзязаться с вами:'
                               '(Пример: НСК, красный проспект 1; 100м2;79...)',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, checking_transition_to_valuation)


def checking_transition_to_valuation(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        user.sale_valuation_reg = message.text
        bot.send_message(chat_id, 'Ваша заявка принята! Наш специалист скоро свяжется с вами 😊', parse_mode='Markdown')
        bot.send_message(CHAT_ID, get_data_user_valuation(user, 'Заявка от бота', bot.get_me().username),
                         parse_mode='Markdown')
    except ValueError:
        bot.reply_to(message, 'Не правильный ввод данных')


def back3(message):
    if message.text == 'Назад':
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        one = types.KeyboardButton('/Инвестиции')
        two = types.KeyboardButton('/Продажа')
        three = types.KeyboardButton('/Покупка')

        markup.add(one, two, three)
        bot.send_message(chat_id, 'Хорошо, давайте начнем заново'.format(message.from_user), reply_markup=markup)


def get_data_user_valuation(user, title, bot_name):
    p = Template(
        '$title *$bot_name* \n Выбор пункта 1: *$sale*  \n Выбор пункта 2: *$sale_valuation* \n '
        'Данные: *$sale_valuation_reg* ')
    return p.substitute({
        'title': title,
        'bot_name': bot_name,
        'sale': user.sale,
        'sale_valuation': user.sale_valuation,
        'sale_valuation_reg': user.sale_valuation_reg
    })


bot.polling(none_stop=True)
if __name__ == '__main__':
    main()
