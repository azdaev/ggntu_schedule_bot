import json

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
    bot.reply_to(message, "Чтобы установить свою группу, напишите ее название")
    bot.register_next_step_handler(message, process_group_name_step)


def process_group_name_step(message: Message):
    group_id = message.text.strip("\n").strip().upper()
    resp = requests.get(
        f"https://backend-isu.gstou.ru/api/timetable/public/entrie/?format=json&group={group_id}")
    if resp.status_code != 200:
        bot.reply_to(message, "Группа не найдена. Попробуйте еще раз")
        bot.register_next_step_handler(message, process_group_name_step)
        return

    cache.set_users_group(message.from_user.id, group_id)
    bot.send_message(message.chat.id, f"Группа установлена. Можешь посмотреть расписание на сегодня - /today")


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

    introduction_word = "Это"
    if weekday == timetable.get_today_weekday():
        introduction_word = "Сегодня"

    bot.send_message(message.chat.id,
                     f"Неделя №{timetable.get_current_week_index()}\n" +
                     f"{introduction_word} {timetable.DAYS_OF_WEEK[weekday].lower()}. Расписание:\n\n" +
                     f"{day_lessons}",
                     )


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


@bot.message_handler(commands=['stats'], func=lambda message: int(message.from_user.id) == int(config.telegram_admin_id))
def get_stats(message: Message):
    bot.reply_to(message, f"Number of users - {cache.get_users_count()}\n"
                          f"Number of groups - {cache.get_groups_count()}\n")


print("starting bot")
bot.infinity_polling()
