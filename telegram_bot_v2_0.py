import sqlite3
import telebot
from telebot import types
from statistic_provider import test_bot_token, Statistics, secret_qiwi_key
import vk_api
import datetime
from datetime import date, timedelta
import plot
from pyqiwip2p import QiwiP2P
import random
import db
import markups


bot = telebot.TeleBot(test_bot_token)
p2p = QiwiP2P(auth_key=secret_qiwi_key)
user_info = {}


def get_statistics(info, message):
    token = get_token_db(message.from_user.id)
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    account_name = info['account']
    statistics = Statistics(vk=vk,
                            account_id=ad_accounts[account_name],
                            ids_type='campaign',
                            period=info['per'],
                            date_from=info['date_from'],
                            date_to=info['date_to'])
    period_for_message = info['период']
    clicks, clicks_links, clicks_groups = statistics.get_clicks()
    bot.send_message(message.chat.id, f'Статистика рекламного кабинета VK {account_name} {period_for_message}.\n\nПотрачено: {statistics.get_spent()} ₽\nОхват: {statistics.get_impressions()}\nКлики: {clicks}\nКлики по ссылкам: {clicks_links}\nКлики по группам: {clicks_groups}\nДоля кликов по ссылкам: {statistics.get_link_click_rate(clicks, clicks_links)} %\nCPC: {statistics.get_cpc(clicks)} ₽\nCPM: {statistics.get_cpm()} ₽\nCTR: {statistics.get_ctr(clicks)} %')
    main_menu(message)


def start_again(message):
    if message.text == 'Нет':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'До скорой встречи!', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for key in ad_accounts:
            markup.add(key)
        choice = bot.send_message(message.chat.id, 'Выберите аккаунт, с которым хотите работать.', reply_markup=markup)
        bot.register_next_step_handler(choice, choice_period)


def period(choice):
    if choice.text == '1':
        date_from = date.today()
        date_to = date.today()
        dat = datetime.datetime.now()
        dat = dat.strftime('%d.%m.%Y')
        per = 'day'
        user_info['date_from'] = date_from
        user_info['date_to'] = date_to
        user_info['per'] = per
        user_info['период'] = f'за {dat}'
        try:
            get_statistics(user_info, choice)
        except Exception as e:
            print('exception occured: ' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(choice.chat.id, 'Контроль флуда. Обратитесь за статистикой чуть-чуть позднее.', reply_markup=markup)
    elif choice.text == '2':
        date_from = date.today() - timedelta(days=1)
        date_to = date.today() - timedelta(days=1)
        dat = datetime.datetime.now() - timedelta(days=1)
        dat = dat.strftime('%d.%m.%Y')
        per = 'day'
        user_info['date_from'] = date_from
        user_info['date_to'] = date_to
        user_info['per'] = per
        user_info['период'] = f'за {dat}'
        try:
            get_statistics(user_info, choice)
        except Exception as e:
            print('exception occured: ' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(choice.chat.id, 'Контроль флуда. Обратитесь за статистикой позднее.', reply_markup=markup)
    elif choice.text == '3':
        date_from = date.today() - timedelta(days=7)
        date_to = date.today() - timedelta(days=7)
        per = 'week'
        user_info['date_from'] = date_from
        user_info['date_to'] = date_to
        user_info['per'] = per
        user_info['период'] = 'за прошлую неделю'
        try:
            get_statistics(user_info, choice)
        except Exception as e:
            print('exception occured: ' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(choice.chat.id, 'Контроль флуда. Обратитесь за статистикой позднее.', reply_markup=markup)
    elif choice.text == '4':
        dat = datetime.datetime.now() - timedelta(days=31)
        date_from = dat.strftime('%Y-%m')
        date_to = dat.strftime('%Y-%m')
        per = 'month'
        user_info['date_from'] = date_from
        user_info['date_to'] = date_to
        user_info['per'] = per
        user_info['период'] = 'за прошлый месяц'
        try:
            get_statistics(user_info, choice)
        except Exception as e:
            print('exception occured: ' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(choice.chat.id, 'Контроль флуда. Обратитесь за статистикой чуть-чуть позднее.', reply_markup=markup)
    elif choice.text == '5':
        date_from = 0
        date_to = 0
        per = 'overall'
        user_info['date_from'] = date_from
        user_info['date_to'] = date_to
        user_info['per'] = per
        user_info['период'] = 'за все время'
        try:
            get_statistics(user_info, choice)
        except Exception as e:
            print('exception occured: ' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(choice.chat.id, 'Контроль флуда. Обратитесь за статистикой чуть-чуть позднее.', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(choice.chat.id, 'Некорректный ввод, перезапустите бот командой /start', reply_markup=markup)


def choice_period(message):
    # if message.text in ad_accounts:
    # user_info['account'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    numbers = ['1', '2', '3', '4', '5']
    for num in numbers:
        markup.add(num)
    bot.send_message(message.chat.id, 'Выберите период, за который необходимо отразить статистику.')
    choice = bot.send_message(message.chat.id, '1 - За сегодня\n2 - За вчера\n3 - За прошлую неделю\n4 - За прошлый месяц\n5 - За все время', reply_markup=markup)
    bot.register_next_step_handler(choice, period)
    # else:
    #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    #     start_button = types.KeyboardButton('/start')
    #     markup.add(start_button)
    #     bot.send_message(message.chat.id, 'Некорректный ввод, перезапустите бот командой /start', reply_markup=markup)


def get_ad_accounts(token):
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        accounts = vk.ads.getAccounts()
        accounts_ids = {}
        for account in accounts:
            accounts_ids[account['account_name']] = account['account_id']
        return accounts_ids
    except Exception as e:
        print('Exception occurred' + repr(e))
        print(Exception)
    # accounts_ids = {}
    # for account in accounts:
    #     accounts_ids[account['account_name']] = account['account_id']
    # return accounts_ids


def get_token_db(userid):
    with sqlite3.connect('users_base.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT token FROM users WHERE userid=?', (userid,))
        result = cur.fetchone()
        return result


def get_token_from_link(message):
    try:
        msg = str(message)
        msg = msg.split('access_token=')
        msg0 = msg[1]
        msg = msg0.split('&expires')
        token = msg[0]
        userid = message.from_user.id
        username = message.from_user.username
        db_table_val(userid=userid, username=username, token=token)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'Регистрация завершена. Приятного пользования!', reply_markup=markup)
    except Exception as e:
        print('not link: ' + repr(e))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reg_button = types.KeyboardButton('/registration')
        markup.add(reg_button)
        bot.send_message(message.from_user.id, 'Ссылка не найдена. Пожалуйста, ознакомьтесь с инструкцией и завершите регистрацию корректно.', reply_markup=markup)


def db_table_val(userid: int, username: str, token: str):
    conn = sqlite3.connect('users_base.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO users (userid, username, token) VALUES (?, ?, ?)', (userid, username, token))
    conn.commit()


def get_access(userid):
    with sqlite3.connect('users_base.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT userid FROM users WHERE userid=?', (userid, ))
        result = cur.fetchone()
        return result


def answer_exam(message):
    if message.text in ad_accounts:
        user_info['account'] = message.text
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'Некорректный ввод, перезапустите бот командой /start', reply_markup=markup)


def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    get_stat = types.KeyboardButton('🔎 Запросить статистику')
    get_plot = types.KeyboardButton('📊 Построить график')
    get_budget = types.KeyboardButton('💰 Запросить остаток бюджета')
    budget_report = types.KeyboardButton('📑 Настроить отчеты по бюджету')
    donate = types.InlineKeyboardButton('🍩 Поддержать разработчика')
    end_button = types.KeyboardButton('💤 Закончить работу')
    markup.add(get_stat, get_plot, get_budget, budget_report, donate, end_button)
    choice = bot.send_message(message.chat.id, 'Что необходимо сделать?', reply_markup=markup)
    bot.register_next_step_handler(choice, menu_next_step)


def menu_next_step(message):
    if message.text == '🔎 Запросить статистику':
        choice_period(message)
    elif message.text == '📊 Построить график':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        but1 = types.KeyboardButton('Охват')
        but2 = types.KeyboardButton('Клики')
        but3 = types.KeyboardButton('Потрачено')
        markup.add(but1, but2, but3)
        choice = bot.send_message(message.chat.id, 'Выберите метрику для отображения.', reply_markup=markup)
        bot.register_next_step_handler(choice, plot_next_step)
    elif message.text == '💰 Запросить остаток бюджета':
        token = get_token_db(message.from_user.id)
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        account_name = user_info['account']
        try:
            budget = vk.ads.getBudget(account_id=ad_accounts[account_name])
            dat = datetime.datetime.now()
            dat = dat.strftime('%d.%m.%Y')
            name = user_info['account']
            bot.send_message(message.chat.id, f'Остаток на счете аккаунта {name} на {dat}:\n\n{budget} ₽')
            main_menu(message)
        except Exception as e:
            print('exception occurred: ' + repr(e))
            bot.send_message(message.chat.id, 'Не удалось выполнить запрос. Возможно, у вас нет доступа.')
            main_menu(message)
    elif message.text == '📑 Настроить отчеты по бюджету':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        on_button = telebot.types.KeyboardButton('Включить')
        off_button = telebot.types.KeyboardButton('Выключить')
        back_button = telebot.types.KeyboardButton('Вернуться в меню')
        markup.add(on_button, off_button, back_button)
        text = user_info['account']
        choice = bot.send_message(message.chat.id, f'Включить/Выключить уведомления по бюджету для аккаунта {text}?', reply_markup=markup)
        bot.register_next_step_handler(choice, budget_report_next_step)
    elif message.text == '🍩 Поддержать разработчика':
        choice = bot.send_message(message.from_user.id, 'Спасибо за проявленную инициативу! Пожалуйста, отправьте сумму доната.')
        bot.register_next_step_handler(choice, donate_next_step)
    elif message.text == '💤 Закончить работу':
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = telebot.types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'До скорой встречи!', reply_markup=markup)
    else:
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # start_button = types.KeyboardButton('/start')
        # markup.add(start_button)
        # bot.send_message(message.chat.id, 'Некорректный ввод, перезапустите бот командой /start', reply_markup=markup)
        main_menu(message)


def donate_next_step(message):
    if message.text.isnumeric() is True:
        try:
            amount = message.text
            comment = str(message.from_user.id) + '_donate' + str(random.randint(1000, 9999))
            bill = p2p.bill(amount=amount, lifetime=15, comment=comment)
            markup = types.InlineKeyboardMarkup(row_width=1)
            link_button = types.InlineKeyboardButton(text='Совершить перевод', url=bill.pay_url)
            markup.add(link_button)
            bot.send_message(message.from_user.id, f'Спасибо большое за вашу поддержку!\n\nСсылка на совершение перевода: {bill.pay_url}', reply_markup=markup)
            main_menu(message)
        except Exception as e:
            print('Something wrong: ' + repr(e))
            bot.send_message(message.from_user.id, 'Что-то пошло не так :( Пожалуйста, попробуйте снова!')
            main_menu(message)
    else:
        bot.send_message(message.from_user.id, 'Похоже, что вы ввели не число :( Пожалуйста, попробуйте еще раз!')
        main_menu(message)


def budget_report_next_step(message):
    if message.text == 'Вернуться в меню':
        main_menu(message)
    if message.text == 'Включить':
        userid = message.from_user.id
        account_name = user_info['account']
        account = str(ad_accounts[account_name])
        print(account)
        with sqlite3.connect('users_base.db') as conn:
            cur = conn.cursor()
            info = cur.execute('SELECT * FROM budget_report WHERE userid=?', (userid,))
            if info.fetchone() is None:
                cur.execute('INSERT INTO budget_report (userid, accounts) VALUES (?, ?)', (userid, account))
                conn.commit()
                bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} теперь включены.')
                main_menu(message)
            else:
                info = cur.execute('SELECT accounts FROM budget_report WHERE userid=?', (userid,))
                accounts = info.fetchone()
                accounts = str(accounts[0])
                accounts_list = accounts.split(';')
                if account in accounts_list:
                    bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} уже включены.')
                    main_menu(message)
                    print('Report already on')
                else:
                    if accounts != '':
                        accounts += ';' + account
                    else:
                        accounts = account
                    cur.execute(f'UPDATE budget_report SET accounts = ? WHERE userid = ?', (accounts, userid))
                    conn.commit()
                    bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} теперь включены.')
                    main_menu(message)
                    print('Report is on')
    if message.text == 'Выключить':
        userid = message.from_user.id
        account_name = user_info['account']
        account = str(ad_accounts[account_name])
        with sqlite3.connect('users_base.db') as conn:
            cur = conn.cursor()
            info = cur.execute('SELECT * FROM budget_report WHERE userid=?', (userid,))
            if info.fetchone() is None:
                bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} не включены.')
                main_menu(message)
            else:
                info = cur.execute('SELECT accounts FROM budget_report WHERE userid=?', (userid,))
                accounts = info.fetchone()
                accounts = str(accounts[0])
                accounts_list = accounts.split(';')
                if account in accounts_list:
                    if account == accounts_list[0]:
                        if len(accounts_list) > 1:
                            accounts = accounts.replace(f'{account};', '')
                        else:
                            accounts = accounts.replace(f'{account}', '')
                    else:
                        accounts = accounts.replace(f';{account}', '')
                    cur.execute(f'UPDATE budget_report SET accounts = ? WHERE userid = ?', (accounts, userid))
                    conn.commit()
                    bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} отключены.')
                    main_menu(message)
                else:
                    bot.send_message(message.chat.id, f'Уведомления по бюджету для аккаунта {account_name} не включены.')
                    main_menu(message)


def plot_next_step(message):
    if message.text == 'Охват':
        metrix = 'impressions'
        account_name = user_info['account']
        account_id = ad_accounts[account_name]
        token = get_token_db(message.from_user.id)
        plot.make_plot(account_id, token, metrix, message)
        main_menu(message)
    elif message.text == 'Клики':
        metrix = 'clicks'
        account_name = user_info['account']
        account_id = ad_accounts[account_name]
        token = get_token_db(message.from_user.id)
        plot.make_plot(account_id, token, metrix, message)
        main_menu(message)
    elif message.text == 'Потрачено':
        metrix = 'spent'
        account_name = user_info['account']
        account_id = ad_accounts[account_name]
        token = get_token_db(message.from_user.id)
        plot.make_plot(account_id, token, metrix, message)
        main_menu(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'Некорректный ввод, перезапустите бот командой /start', reply_markup=markup)


def check_payment(userid):
    with sqlite3.connect('users_base.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT payment FROM users WHERE userid=?', (userid, ))
        result = cur.fetchone()
        return result


def payment_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    pay_button = types.KeyboardButton('Оплатить подписку')
    trial_button = types.KeyboardButton('Бесплатный период')
    help_button = types.KeyboardButton('/help')
    markup.add(pay_button, trial_button, help_button)
    choice = bot.send_message(message.chat.id, '''Для получения доступа к услугам сервиса оформите подписку на месяц за 490 ₽ или начните бесплатный пробный период на 7 дней.

Чтобы узнать подробнее об услугах, предоставляемых сервисом, выполните команду /help.''', reply_markup=markup)
    bot.register_next_step_handler(choice, payment_next_step)


def payment_next_step(message):
    userid = message.from_user.id
    if message.text == 'Бесплатный период':
        with sqlite3.connect('users_base.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT trial FROM users WHERE userid=?', (userid,))
            result = cur.fetchone()
            if result[0] is None:
                trial = 'expired'
                cur.execute(f'UPDATE users SET trial = ? WHERE userid = ?', (trial, userid))
                payment = date.today() + timedelta(days=7)
                cur.execute(f'UPDATE users SET payment = ? WHERE userid = ?', (payment, userid))
                conn.commit()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                start_button = types.KeyboardButton('/start')
                markup.add(start_button)
                bot.send_message(message.chat.id, 'Ваш пробный период на 7 дней начат!\n\nДля начала работы выполните команду /start', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, 'Ваш пробный период истек.')
                payment_message(message)
    elif message.text == 'Оплатить подписку':
        database = db.Database('users_base.db')
        comment = str(message.from_user.id) + '_' + str(random.randint(1000, 9999))
        bill = p2p.bill(amount=490, lifetime=15, comment=comment)
        database.add_pay_check(message.from_user.id, bill.bill_id)
        bot.send_message(message.from_user.id, f'Оплата производится через QIWI.\n\nСсылка на оплату: {bill.pay_url}\n\nПосле оплаты нажмите кнопку <Проверить оплату> для подтверждения.', reply_markup=markups.buy_menu(url=bill.pay_url, bill=bill.bill_id))
    elif message.text == '/help':
        help_command(message)
    else:
        choice = bot.send_message(message.chat.id, 'Некорректный ввод. Пожалуйста, воспользуйтесь кнопками ниже.')
        bot.register_next_step_handler(choice, payment_next_step)


@bot.callback_query_handler(func=lambda call: True)
def check(call):
    database = db.Database('users_base.db')
    bill = str(call.data[6:])
    print(bill)
    status = database.get_pay_check(bill)
    if status != False:
        if str(p2p.check(bill_id=bill).status) == 'PAID':
            database.set_payment(call.from_user.id)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton('/start')
            markup.add(start_button)
            bot.send_message(call.from_user.id, 'Подписка оплачена. Для начала работы выполните команду /start. Приятного пользования!', reply_markup=markup)
            database.del_pay_check(bill_id=bill)
        else:
            bot.send_message(call.from_user.id, 'Вы не оплатили счет.', reply_markup=markups.buy_menu(False, bill=bill))
    else:
        bot.send_message(call.from_user.id, 'Счет не найден')


@bot.message_handler(commands=['start'])
def beginning(message):
    database = db.Database('users_base.db')
    print(f'User {message.from_user.id} {message.from_user.username} online')
    access = database.user_exists(message.from_user.id)
    user_info.clear()
    if access is True:
        token = get_token_db(message.from_user.id)
        global ad_accounts
        try:
            pay = check_payment(message.from_user.id)
            if pay[0] is not None:
                ad_accounts = get_ad_accounts(token)
                if not ad_accounts:
                    bot.send_message(message.from_user.id, 'У вас нет доступа ни к одному рекламному кабинету VK :(')
                else:
                    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    for key in ad_accounts:
                        markup.add(key)
                    bot.send_message(message.chat.id, 'Доброго времени суток!', reply_markup=markup)
                    choice = bot.send_message(message.chat.id, 'Выберите аккаунт, с которым хотите работать.')
                    bot.register_next_step_handler(choice, answer_exam)
            else:
                payment_message(message)
        except Exception as e:
            print('Exception occurred' + repr(e))
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            token_button = types.KeyboardButton('/token')
            markup.add(token_button)
            bot.send_message(message.chat.id, 'Похоже, что ваш токен задан не верно. Для замены токена выполните команду /token', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reg_button = types.KeyboardButton('/registration')
        markup.add(reg_button)
        bot.send_message(message.chat.id, 'Доброго времени суток!\n\nВы не зарегистрированы в системе.\n\nДля регистрации выполните команду /registration', reply_markup=markup)


@bot.message_handler(commands=['registration'])
def registration(message):
    access = get_access(message.chat.id)
    if access is not None:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы')
    else:
        markup = types.InlineKeyboardMarkup()
        link_button = types.InlineKeyboardButton("Авторизация", url='https://oauth.vk.com/oauth/authorize?client_id=6121396&redirect_uri=https%3A%2F%2Foauth.vk.com%2Fblank.html&response_type=token&scope=496074752&v=&state=&revoke=1&display=page&display=page&success=1')
        markup.add(link_button)
        bot.send_message(message.chat.id, 'Для работы бота необходимо задать токен.\n\nДля получения токена, перейдите по ссылке и авторизуйтесь в VK.\n\nПолученную ссылку из строки браузера скопируйте и отправьте в этот чат.', reply_markup=markup)
        with open('instruction.pdf', 'rb') as doc:
            bot.send_document(message.chat.id, doc, caption='Не отправляйте в чат ничего, кроме ссылки, иначе бот не сможет отразить статистику.\n\nПодробная инструкция в документе.')
        markup = types.ReplyKeyboardRemove()
        token_link = bot.send_message(message.chat.id, 'Ожидание ссылки...', reply_markup=markup)
        bot.register_next_step_handler(token_link, get_token_from_link)


@bot.message_handler(commands=['help'])
def help_command(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton('/start')
    markup.add(start_button)
    bot.send_message(message.chat.id, '''❓Какие услуги предоставляет Clickeye сейчас:

🔎 Предоставление статистики рекламного кабинета:
      ✔️ За период на ваш выбор
      ✔️ Все важные метрики
📊 Постройка графиков по различным метрикам:
      ✔️ По охвату
      ✔️ По кликам
      ✔️ По тратам
💰 Предоставление остатка на счет рекламного кабинета по вашему запросу. 
📑 Ежедневная отправка отчетов об остатке на счете рекламного кабинета или нескольких по вашему запросу. 

/start - для начала работы
/registration - для регистрации в системе
/token - для проверки или смены вашего токена

Примите во внимание, что сервис находится в разработке, возможны ошибки в работе сервиса. При возникновении таковых, пишите @markgevorkyan''', reply_markup=markup)


@bot.message_handler(commands=['token'])
def token_info(message):
    access = get_access(message.chat.id)
    if access is not None:
        token = get_token_db(message.from_user.id)
        bot.send_message(message.chat.id, 'Ваш текущий токен:')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        y_button = types.KeyboardButton('Да')
        n_button = types.KeyboardButton('Нет')
        markup.add(y_button, n_button)
        bot.send_message(message.chat.id, token)
        choice = bot.send_message(message.chat.id, 'Желаете изменить ваш токен?', reply_markup=markup)
        bot.register_next_step_handler(choice, change_token)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        reg_button = types.KeyboardButton('/registration')
        markup.add(reg_button)
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в системе. Для регистрации выполните команду /registration', reply_markup=markup)


def change_token(message):
    if message.text == 'Да':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Вы пожелали изменить ваш токен.', reply_markup=markup)
        markup = types.InlineKeyboardMarkup()
        link_button = types.InlineKeyboardButton("Авторизация", url='https://oauth.vk.com/authorize?client_id=6121396&scope=1073737727&redirect_uri=https://oauth.vk.com/blank.html&display=page&response_type=token&revoke=1')
        markup.add(link_button)
        bot.send_message(message.chat.id, 'Для получения токена, перейдите по ссылке и авторизуйтесь через VK ADMIN или другое приложение, дающее доступ к рекламному кабинету вконтакте.\n\nПолученную ссылку из строки браузера скопируйте и отправьте в этот чат.', reply_markup=markup)
        token_link = bot.send_message(message.chat.id, 'Ожидание ссылки...')
        bot.register_next_step_handler(token_link, insert_new_token)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'Для начала работы выполните команду /start', reply_markup=markup)


def insert_new_token(message):
    try:
        msg = str(message)
        msg = msg.split('access_token=')
        msg0 = msg[1]
        msg = msg0.split('&expires')
        token = msg[0]
        userid = message.from_user.id
        conn = sqlite3.connect('users_base.db')
        cur = conn.cursor()
        cur.execute(f'UPDATE users SET token = ? WHERE userid = ?', (token, userid))
        conn.commit()
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton('/start')
        markup.add(start_button)
        bot.send_message(message.chat.id, 'Токен успешно изменен на: ')
        bot.send_message(message.chat.id, token)
        bot.send_message(message.chat.id, 'Для начала работы выполните команду /start', reply_markup=markup)
    except Exception as e:
        print('Exception occurred' + repr(e))


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print('exception occurred in main: ' + repr(e))
