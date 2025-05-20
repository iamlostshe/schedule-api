"""Schedule API module."""

import datetime

from fastapi import FastAPI

from parser import download_schedule_file, parse_lessons


app = FastAPI()

NORMALIZED_WEEKDAYS = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
    "Mo": 0,
    "Tu": 1,
    "We": 2,
    "Th": 3,
    "Fr": 4,
    "Sa": 5,
    "Su": 6,
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
}


def get_this_weekday():
    return datetime.datetime.now().weekday()


def get_next_weekday():
    return (datetime.datetime.now() + datetime.timedelta(days=1)).weekday()


@app.get("/")
async def read_item(
    table_id: str,
    week_day: str,
    my_class: str,
):
    # Проверяем возможно ли скачать указанный файл
    if not download_schedule_file():
        return {
            "error": "Problems with downloading the schedule file. The link may be corrupted.",
            "schedule": []
        }

    # Получаем данные
    schedule = parse_lessons()

    # Получаем расписание для указанного класса
    class_schedule = schedule.get(my_class)

    if not class_schedule:
        return {
            "error": "It is not possible to get information on the specified class.",
            "schedule": []
        }

    if week_day == "this_day":
        wd = get_this_weekday()
    elif week_day == "next_day":
        wd = get_next_weekday()
    else:

        # TODO: Добавить возможность получить расписание на несколько дней
        for i in week_day.split(","):
            wd = NORMALIZED_WEEKDAYS.get(week_day, "")
            break

    try:
        wd = int(wd)
        return {
            "schedule": class_schedule[wd]
        }
    except ValueError:
        return {
            "error": "Problem when retrieving information by day of the week.",
            "schedule": []
        }
    except IndexError:
        return {
            "error": "Problem. Attempting to get an inaccessible index, {wd}. The index should be between 0 and 5. Sunday cannot be used.",
            "schedule": []
        }