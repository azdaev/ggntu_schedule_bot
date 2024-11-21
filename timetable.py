import datetime
import requests
from typing import Dict, List, Tuple, Optional

# Константы лучше вынести в отдельный файл constants.py
from constants import LESSON_TIMES, DAYS_OF_WEEK, ACTIVITY_TYPES_TO_STRING

def get_today_weekday() -> int:
    """Получить номер текущего дня недели. Понедельник - 1, Воскресенье - 7."""
    return datetime.datetime.today().weekday() + 1

def get_tomorrow_weekday() -> int:
    """Получить номер завтрашнего дня недели. Понедельник - 1, Воскресенье - 7."""
    return (datetime.date.today() + datetime.timedelta(days=1)).weekday() + 1

def get_current_week_index() -> int:
    """Получить индекс текущей недели. Первая неделя - 1, вторая - 2, третья - 1, четвертая - 2 и т.д."""
    return 2 - ((datetime.datetime.today().isocalendar()[1] + 1) % 2)

def get_next_week_index() -> int:
    """Получить индекс следующей недели."""
    return 2 - (datetime.datetime.today().isocalendar()[1] % 2)

def request_timetable(group_id: str) -> List[Dict]:
    """Запросить недельное расписание для группы, отсортированное по дню недели и периоду."""
    url = f"https://backend-isu.gstou.ru/api/timetable/public/entrie/?format=json&group={group_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Вызовет исключение при ошибке HTTP
    timetable_unsorted = response.json()
    return sorted(timetable_unsorted, key=lambda x: (x['week_day'], x['period']))

def get_day_schedule(weekday_id: int, week_schedule: List[Dict], week_index: Optional[int] = None) -> List[Dict]:
    """Получить расписание на день из недельного расписания."""
    if week_index is None:
        week_index = get_current_week_index()
    
    day_lessons = []
    seen_periods = set()
    
    for lesson in week_schedule:
        if lesson['week_day'] == weekday_id:
            if lesson.get('week') is not None and lesson.get('week') != week_index:
                continue
            if lesson['period'] in seen_periods:
                continue
            seen_periods.add(lesson['period'])
            day_lessons.append(lesson)
    
    return day_lessons

def string_day_schedule(day_lessons: List[Dict]) -> str:
    """Вернуть строковое представление расписания на день."""
    result = []
    for lesson in day_lessons:
        try:
            lesson_period = lesson['period']
            lesson_name = lesson['discipline']['name']
            lesson_type = lesson['activity_type']
            lesson_teacher = lesson['discipline'][ACTIVITY_TYPES_TO_STRING[lesson_type][1]]['name']
            lesson_cabinet = lesson['auditorium']['name']

            lesson_str = (
                f"<u>№{lesson_period} ({LESSON_TIMES[lesson_period][0]} – {LESSON_TIMES[lesson_period][1]})</u>\n"
                f"<b>{lesson_name}</b> ({ACTIVITY_TYPES_TO_STRING[lesson_type][0]})\n"
                f"<i>{lesson_teacher}, {lesson_cabinet}</i>"
            )
            result.append(lesson_str)
        except KeyError as e:
            print(f"Ошибка при обработке урока: {e}")
            print(f"Данные урока: {lesson}")
    
    return "\n\n".join(result)

def string_week_schedule(week_schedule: List[Dict], week_index: Optional[int] = None) -> str:
    """Вернуть строковое представление расписания на неделю."""
    if week_index is None:
        week_index = get_current_week_index()
    
    days_lessons = [[] for _ in range(7)]
    for i in range(1, 8):
        days_lessons[i - 1] = get_day_schedule(i, week_schedule, week_index=week_index)
    
    result = []
    for day_lessons in days_lessons:
        if len(day_lessons) == 0:
            continue
        result.append(f"<b>{DAYS_OF_WEEK[day_lessons[0]['week_day']]}:</b>")
        result.append(string_day_schedule(day_lessons))
        result.append("~~~~~~")
    
    return "\n\n".join(result)