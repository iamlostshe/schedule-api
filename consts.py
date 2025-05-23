"""Некторые постоянные значения."""

import datetime


def get_this_weekday() -> int:
    """Получение текущего дня недели."""
    this_weekday = datetime.datetime.now().weekday()  # noqa: DTZ005
    return 0 if this_weekday == 6 else this_weekday


def get_next_weekday() -> int:
    """Получение следующего дня недели."""
    next_weekday = (datetime.datetime.now() + datetime.timedelta(days=1)).weekday()  # noqa: DTZ005
    return 0 if next_weekday == 6 else next_weekday


PARAMS = {"format": "xlsx"}
FOLDER_NAME = "sp_data"
MAX_UPDATE_TIME = 3600
NORMALIZED_WEEKDAYS = {
    "this_day": get_this_weekday,
    "next_day": get_next_weekday,
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "mo": 0,
    "tu": 1,
    "we": 2,
    "th": 3,
    "fr": 4,
    "sa": 5,
    "пн": 0,
    "вт": 1,
    "ср": 2,
    "чт": 3,
    "пт": 4,
    "сб": 5,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
}
MINIFY_LESSON_TITLE = {
    "кл.час": "классный час",
    "матем": "математика",
    "рус.яз": "русский язык",
    "физкул": "физкультура",
    "географ": "география",
    "литер": "литература",
    "геометр": "геометрия",
    "биолог": "биология",
    "общест": "обществознание",
    "англ.яз": "английский язык",
    "физ(у)/инф(у)": "физика (углублённая)/информатика (углублённая)",
    "инф(б)/физ(б)": "информатика (базовая)/физика (базовая)",
    "информ.(э)": "электив по информатике",
}
