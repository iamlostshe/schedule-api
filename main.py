"""Schedule API module."""

import datetime

from fastapi import FastAPI
from loguru import logger

from consts import NORMALIZED_WEEKDAYS
from parser import ScheduleParser

parser = ScheduleParser()
app = FastAPI()


def get_this_weekday() -> int:
    return datetime.datetime.now().weekday()

def get_next_weekday() -> int:
    return (datetime.datetime.now() + datetime.timedelta(days=1)).weekday()

def process_lessons(lessons: list[str]) -> tuple[list[str], list[str], int]:
    """Разделяет уроки и кабинеты, определяет первый действительный урок."""
    subjects = []
    cabinets = []
    entry_lesson = 0

    for i, lesson in enumerate(lessons, 1):
        subject, cabinet = lesson.split(":")

        subjects.append(subject)
        cabinets.append(cabinet)

        # Определяем первый не None урок
        if not entry_lesson and "Окно" not in subject:
            entry_lesson = i

    return subjects, cabinets, entry_lesson

@app.get("/")
async def get_schedule(
    table_id: str,
    week_day: str,
    my_class: str,
) -> dict:
    # Download and parse schedule
    table_filename = await parser.download_schedule_file(table_id)
    if not table_filename:
        logger.error("Failed to download schedule file")
        return {"entry_lesson": 1, "schedule": [], "cabinets": []}

    schedule = parser.parse_lessons(table_filename)
    class_schedule = schedule.get(my_class)

    if not class_schedule:
        ValueError(f"Class {my_class} not found")

    # Process days
    try:
        if "," in week_day:
            days = [d.strip() for d in week_day.split(",")]
            if any(d.lower() in ("this_day", "next_day") for d in days):
                msg = "Relative days in multi-day request"
                raise ValueError(msg)

            normalized_days = []
            for day in days:
                normalized_day = NORMALIZED_WEEKDAYS.get(day.title()) or NORMALIZED_WEEKDAYS.get(day)
                if normalized_day is None or not 0 <= normalized_day <= 5:
                    msg = f"Invalid day: {day}"
                    raise ValueError(msg)
                normalized_days.append(normalized_day)

            combined_lessons = []
            for nd in normalized_days:
                if nd >= len(class_schedule):
                    msg = f"Day index {nd} out of range"
                    raise IndexError(msg)
                combined_lessons.extend(class_schedule[nd])

            subjects, cabinets, entry_lesson = process_lessons(combined_lessons)
            return {
                "entry_lesson": entry_lesson,
                "schedule": subjects,
                "cabinets": cabinets,
            }

        if week_day.lower() == "this_day":
            wd = get_this_weekday()
        elif week_day.lower() == "next_day":
            wd = get_next_weekday()
        else:
            wd = NORMALIZED_WEEKDAYS.get(week_day.lower())
            if wd is None:
                msg = f"Invalid day format: {week_day}"
                raise ValueError(msg)

        if not 0 <= wd <= 5:
            msg = "Sunday cannot be used"
            raise ValueError(msg)

        if wd >= len(class_schedule):
            msg = f"Day index {wd} out of range"
            raise IndexError(msg)

        subjects, cabinets, entry_lesson = process_lessons(class_schedule[wd])

    except Exception as e:  # noqa: BLE001
        return {
            "error": str(e),
            "entry_lesson": 1,
            "schedule": [],
            "cabinets": [],
        }

    else:
        return {
            "entry_lesson": entry_lesson,
            "schedule": subjects,
            "cabinets": cabinets,
        }
