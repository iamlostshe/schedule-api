"""Самостоятельный парсер школьного расписания.

Содержит функцию получения и парсинга расписания из XLSX файла.
"""

from collections import defaultdict
from pathlib import Path

import openpyxl
import requests
from loguru import logger

# Ссылка на Google Таблицу (формат XLSX)
SCHEDULE_URL = "https://docs.google.com/spreadsheets/d/1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU/export?format=xlsx"
RAW_SC_PATH = Path("sp_data/sc.xlsx")


def download_schedule_file() -> bool:
    """Скачивает файл расписания по ссылке и сохраняет локально."""
    try:
        RAW_SC_PATH.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(SCHEDULE_URL, timeout=10)
        response.raise_for_status()
        RAW_SC_PATH.write_bytes(response.content)
        logger.info("Файл расписания успешно загружен.")
        return True
    except Exception as e:
        logger.error("Ошибка при загрузке файла: {}", e)
        return False


def _clear_day_lessons(day_lessons: list[str]) -> list[str]:
    """Удаляет все пустые уроки с конца списка."""
    while day_lessons:
        lesson = day_lessons[-1].split(":")[0]
        if lesson and lesson not in ("---", "None"):
            return day_lessons
        day_lessons.pop()
    return []


def parse_lessons() -> dict[str, list[list[str]]]:
    """Парсит XLSX-файл в словарь расписания.

    Формат:
    {
        "класс": [
            ["урок:кабинет", ...],  # Понедельник
            ["урок:кабинет", ...],  # Вторник
            ...
        ]
    }
    """
    logger.info("Начинаем парсинг расписания...")

    lessons: dict[str, list] = defaultdict(lambda: [[] for _ in range(6)])
    day = -1
    last_row = 8

    sheet = openpyxl.load_workbook(str(RAW_SC_PATH)).active
    if sheet is None:
        raise ValueError("Не удалось получить активный лист в файле расписания")

    row_iter = sheet.iter_rows()

    # Получаем заголовки с названиями классов
    next(row_iter)  # Пропускаем первую строку
    cl_header: list[tuple[str, int]] = []
    for i, cl in enumerate(next(row_iter)):
        if isinstance(cl.value, str) and cl.value.strip():
            cl_header.append((cl.value.lower(), i))

    # Построчное чтение расписания
    for row in row_iter:
        if isinstance(row[1].value, (int, float)):
            if row[1].value < last_row:
                day += 1
            last_row = int(row[1].value)

            for cl, i in cl_header:
                # Проверка на пустую ячейку или зачёркнутое значение
                if row[i].value is None or row[i].font.strike:
                    lesson = None
                else:
                    lesson = str(row[i].value).strip(" .-").lower() or None

                # Кабинет может быть числом или строкой
                if row[i + 1].value is None:
                    cabinet = "None"
                elif isinstance(row[i + 1].value, float):
                    cabinet = str(int(row[i + 1].value))
                elif isinstance(row[i + 1].value, str):
                    cabinet = str(row[i + 1].value).strip().lower() or "0"
                else:
                    raise ValueError(f"Неверный формат кабинета: {row[i + 1]}")

                lessons[cl][day].append(f"{lesson}:{cabinet}")

        elif day == 5:  # После субботы — стоп
            break

    logger.info("Парсинг завершён успешно.")
    return {k: [_clear_day_lessons(x) for x in v] for k, v in lessons.items()}
