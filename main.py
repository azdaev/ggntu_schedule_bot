import telebot
from telebot import types
from telebot.types import Message
import config
import cache
import requests
import timetable


config = config.Config()
bot = telebot.TeleBot(config.telegram_api_token, parse_mode="HTML")
cache = cache.Cache(config.redis_host, config.redis_port)

bot.set_my_commands([types.BotCommand('me', 'Указать группу'),
                     types.BotCommand('today', 'Сегодня'),
                     types.BotCommand('tomorrow', 'Завтра'),
                     types.BotCommand('week', 'На неделе')])


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(message, "Ассаляму алейкум! Напиши название твоей группы и я смогу показывать тебе расписание")
    bot.register_next_step_handler(message, process_group_name_step)


@bot.message_handler(commands=['me'])
def set_group(message: Message):
    bot.reply_to(message, "Чтобы установить свою группу, напишите ее название. Отменить ввод группы - /cancel")
    bot.register_next_step_handler(message, process_group_name_step)


def process_group_name_step(message: Message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "Отменено")
        return
    
    group_id = message.text.strip("\n").strip().upper()        
    resp = requests.get(
        f"https://backend-isu.gstou.ru/api/timetable/public/entrie/?format=json&group={group_id}")
    if resp.status_code != 200:
        bot.reply_to(message, "Группа не найдена. Попробуйте еще раз или отмените ввод группы - /cancel")
        bot.register_next_step_handler(message, process_group_name_step)
        return

    cache.set_users_group(message.from_user.id, group_id)
    bot.send_message(message.chat.id, f"Группа установлена. Можешь посмотреть расписание на сегодня - /today\nНа завтра - /tomorrow\nНа неделе - /week")


@bot.message_handler(commands=['today'])
def today_schedule(message: Message):
    day_schedule(message, timetable.get_today_weekday())


@bot.message_handler(commands=['tomorrow'])
def tomorrow_schedule(message: Message):
    day_schedule(message, timetable.get_tomorrow_weekday())


def day_schedule(message: Message, weekday):
    group_id = cache.get_users_group_id(message.from_user.id)
    if group_id is None:
        bot.send_message(message.chat.id, "Сначала введите вашу группу")
        bot.register_next_step_handler(message, process_group_name_step)
        return

    schedule = cache.get_group_schedule(group_id)
    if schedule is None:
        schedule = timetable.request_timetable(group_id)
        cache.set_group_schedule(group_id, schedule)

    raw_day_lessons = timetable.get_day_schedule(weekday, schedule)
    day_lessons = timetable.string_day_schedule(raw_day_lessons)

    reply_text = f"Неделя №{timetable.get_current_week_index()}. {timetable.DAYS_OF_WEEK[weekday]}\n"
    if day_lessons == "":
        reply_text += "Пар нет"
    else:
        reply_text += "Расписание:\n"
        reply_text += day_lessons

    bot.send_message(message.chat.id, reply_text)


@bot.message_handler(commands=['week'])
def week_schedule(message: Message):
    group_id = cache.get_users_group_id(message.from_user.id)
    if group_id is None:
        bot.send_message(message.chat.id, "Сначала введите вашу группу")
        bot.register_next_step_handler(message, process_group_name_step)
        return
 
    schedule = cache.get_group_schedule(group_id)
    if schedule is None:
        schedule = timetable.request_timetable(group_id)
        cache.set_group_schedule(group_id, schedule)

    week_lessons = timetable.string_week_schedule(schedule)

    bot.send_message(message.chat.id,
                     f"Неделя №{timetable.get_current_week_index()}\n\n" +
                     week_lessons
                     )
    
@bot.message_handler(commands=['next_week'])
def next_week_schedule(message: Message):
    group_id = cache.get_users_group_id(message.from_user.id)
    if group_id is None:
        bot.send_message(message.chat.id, "Сначала введите вашу группу")
        bot.register_next_step_handler(message, process_group_name_step)
        return
 
    schedule = cache.get_group_schedule(group_id)
    if schedule is None:
        schedule = timetable.request_timetable(group_id)
        cache.set_group_schedule(group_id, schedule)

    next_week_index = 3 - timetable.get_current_week_index()

    week_lessons = timetable.string_week_schedule(schedule, week_index=next_week_index)

    bot.send_message(message.chat.id,
                     f"Следующая неделя - №{next_week_index}\n\n" +
                     week_lessons
                     )


@bot.message_handler(commands=['stats'], func=lambda message: int(message.from_user.id) == int(config.telegram_admin_id))
def get_stats(message: Message):
    bot.reply_to(message, f"Number of users - {cache.get_users_count()}\n"
                          f"Number of groups - {cache.get_groups_count()}\n")


print("starting bot")
bot.infinity_polling()
