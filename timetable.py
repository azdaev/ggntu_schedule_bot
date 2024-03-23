import datetime
import requests

LESSON_TIMES = {
    1: ("09:00", "10:20"),
    2: ("10:30", "11:50"),
    3: ("13:00", "14:20"),
    4: ("14:30", "15:50"),
    5: ("16:00", "17:20"),
}

DAYS_OF_WEEK = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}

ACTIVITY_TYPES_TO_STRING = {
    1: ("Лек.", "lecture_teacher"),
    2: ("Лаб.", "lab_teacher"),
    3: ("Прак.", "practice_teacher"),
}


def get_today_weekday():
    """
    Get today's weekday number. Monday is 1, Sunday is 7
    """
    return datetime.datetime.today().weekday() + 1


def get_tomorrow_weekday():
    """
    Get tomorrow's weekday number. Monday is 1, Sunday is 7
    """
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return tomorrow.weekday() + 1


def get_current_week_index():
    """
    Get current week index. First week is 1. Second week is 2. Third - 1, fourth - 2 etc.
    """
    return 2 - (datetime.datetime.today().isocalendar()[1] % 2)

def get_next_week_index():
    """
    Get next week index. First week is 1. Second week is 2. Third - 1, fourth - 2 etc.
    """
    return 2 - ((datetime.datetime.today().isocalendar()[1] + 1) % 2)

def request_timetable(group_id):
    """
        Request weekly timetable for group sorted by weekday and period (index of lesson)
    """
    timetable_unsorted = requests.get(
        f"https://backend-isu.gstou.ru/api/timetable/public/entrie/?format=json&group={group_id}").json()
    # sort timetable_unsorted by object['week_day'] and then by object['period']
    timetable = sorted(timetable_unsorted, key=lambda x: (x['week_day'], x['period']))
    return timetable


def get_day_schedule(weekday_id, week_schedule, week_index=get_current_week_index()):
    """
        Get day's schedule from weekly schedule
    """
    day_lessons = []
    for lesson in week_schedule:
        if lesson['week_day'] == weekday_id:
            if lesson.get('week') is not None and lesson.get('week') != week_index:  # not this week
                continue

            if len(day_lessons) > 0 and lesson['period'] == day_lessons[-1]['period']:  # duplicate lesson
                continue

            day_lessons.append(lesson)

    return day_lessons


def string_day_schedule(day_lessons):
    """
        Return string representation of day's schedule
    """
    result = ""
    for lesson in day_lessons:
        try:
            lesson_period = lesson['period']
            lesson_name = lesson['discipline']['name']
            lesson_type = lesson['activity_type']  # 1 - лекция, 2 - лаб., 3 - практика
            lesson_teacher = lesson['discipline'][ACTIVITY_TYPES_TO_STRING[lesson_type][1]]['name']
            lesson_cabinet = lesson['auditorium']['name']

            result += (f"<u>№{lesson_period} ({LESSON_TIMES[lesson_period][0]} – "
                       f"{LESSON_TIMES[lesson_period][1]})</u>\n")
            result += f"<b>{lesson_name}</b> ({ACTIVITY_TYPES_TO_STRING[lesson_type][0]})\n"
            result += f"<i>{lesson_teacher}, {lesson_cabinet}</i>\n\n"
        except KeyError as e:
            print(e, lesson)

    return result.strip("\n")


def string_week_schedule(week_schedule, week_index=get_current_week_index()):
    days_lessons = [[] for i in range(7)]
    for i in range(1, 8):
        days_lessons[i - 1] = get_day_schedule(i, week_schedule, week_index=week_index)

    result = ""

    for day_lessons in days_lessons:
        if len(day_lessons) == 0:
            continue
        result += f"<b>{DAYS_OF_WEEK[day_lessons[0]['week_day']]}:</b>\n\n"
        result += string_day_schedule(day_lessons)
        result += "\n\n~~~~~~\n\n"

    return result.strip("\n").strip("~")

