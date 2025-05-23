"""Schedule API module."""

from fastapi import FastAPI
from loguru import logger

from consts import NORMALIZED_WEEKDAYS
from parser import ScheduleParser

parser = ScheduleParser()
app = FastAPI()


def _normalize_week_days(week_days: str) -> list:
    """Нормализует список из дней недели."""
    n_week_days = []
    try:
        for week_day in week_days.replace(" ", "").split(","):
            n_week_day = NORMALIZED_WEEKDAYS[week_day.lower()]
            if len(n_week_days) == 6:
                break
            if not isinstance(n_week_day, int):
                n_week_day = n_week_day()
            if n_week_day not in n_week_days:
                n_week_days.append(n_week_day)

    except KeyError:
        msg = (
            "Проблема с задаными данными дней недели. "
            "Пожалуйста проверьте корректность введённых данных."
        )
        raise KeyError(  # noqa: B904
            msg,
        )

    else:
        return n_week_days


def process_lessons(schedule: list[str]) -> tuple[list[str], list[str], int]:
    """Разделяет уроки и кабинеты, определяет первый действительный урок."""
    lessons = []
    cabinets = []
    entry_lesson = 0

    for i, lesson in enumerate(schedule, 1):
        subject, cabinet = lesson.split(":")

        lessons.append(subject)
        cabinets.append(cabinet)

        # Определяем первый не None урок
        if not entry_lesson and "None" not in subject:
            entry_lesson = i

    return {
        "entry_lesson": entry_lesson,
        "lessons": lessons,
        "cabinets": cabinets,
    }


@app.get("/")
async def get_schedule(
    week_days: str,
    table_id: str,
    my_class: str,
) -> list:
    """Обработка запроса расписания у API."""
    try:
        # Приводим дни недели к единому числовому формату
        week_days = _normalize_week_days(week_days)

        # Скачиваем файл с расписанием
        table_filename = await parser.download_schedule_file(table_id)
        if not table_filename:
            msg = (
                "Ошибка при скачивании файла с расписанием. "
                "Проверьте параметр table_id или настройки доступа к таблице."
            )
            raise ValueError(  # noqa: TRY301
                msg,
            )

        # Препарируем файл и получаем данные по нужному классу
        class_schedule = parser.parse_lessons(table_filename).get(my_class)

        if not class_schedule:
            msg = "Указаный класс не найден в раписании."
            raise ValueError(  # noqa: TRY301
                msg,
            )

        # Формируем итоговое расписание и возвращаем пользователю
        return [process_lessons(class_schedule[week_day]) for week_day in week_days]

    except Exception as e:  # noqa: BLE001
        # Выводим лог в консоль
        logger.error(e)

        # Возвращаем пользователю ошибку
        return [{
            "error": str(e),
        }]
