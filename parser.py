"""Самостоятельный парсер школьного расписания.

Содержит функцию получения и парсинга расписания из XLSX файла.
"""

from collections import defaultdict
from pathlib import Path
from time import time

import aiofiles
import openpyxl
from aiohttp import ClientSession
from loguru import logger

from consts import FOLDER_NAME, MAX_UPDATE_TIME, MINIFY_LESSON_TITLE, PARAMS

Path(FOLDER_NAME).mkdir(parents=True, exist_ok=True)

class IncorrectCabinetFormatError(ValueError):
    """Исключение, выбрасываемое при некорректном формате кабинета."""

    def __init__(self, cabinet: str) -> None:
        """Just init error."""
        super().__init__(f'Некорректный формат кабинета: "{cabinet}"')


def _get_previous_file(table_id: str) -> str | None:
    """Возвращает предыдущее сохранение таблицы, если оно есть."""
    for f in Path(FOLDER_NAME).iterdir():
        if (
            f.is_file()
            and table_id in f.name
            and int(
                f.name.replace(".xlsx", "").split("_")[-1],
            )
            + MAX_UPDATE_TIME
            > time()
        ):
            return f"{FOLDER_NAME}/{f.name}"
    return None


def _normalize_lesson(lesson: str) -> str:
    """Нормализует название урока."""
    if isinstance(lesson, str):
        return MINIFY_LESSON_TITLE.get(
            lesson.strip().strip(".").lower().split("(")[0],
            lesson,
        ).capitalize()
    return lesson


def _clear_day_lessons(day_lessons: list[str]) -> list[str]:
    """Удаляет все пустые уроки с конца списка."""
    while day_lessons:
        lesson = day_lessons[-1].split(":")[0]
        if lesson and lesson not in ["None", "---"]:
            return day_lessons
        day_lessons.pop()
    return []


class ScheduleParser:
    """Класс для взаимодействия с таблицами и извлечения из них данных."""

    def __init__(self) -> None:
        """Просто инициализация пустой сессии чтобы всё корректно работало."""
        self.session = None

    async def download_schedule_file(self, table_id: str) -> bool:
        """Скачивает файл расписания по ссылке и сохраняет локально."""
        try:
            # TODO: Проверить наличие такого файла в локальной памяти
            # в таком случае не запрашивать таблицу с сервера,
            # разумеется, если не истёк строк актуальности (константа)

            # Проверяем наличае сессии и если её нет - создаём
            if not self.session:
                self.session = ClientSession(
                    base_url="https://docs.google.com/spreadsheets/d/",
                    raise_for_status=True,
                )
                logger.debug("Сессия aiohttp создана.")

            # Запрашиваем таблицу
            table_filename = _get_previous_file(table_id)

            if table_filename:
                return table_filename

            async with self.session.get(f"{table_id}/export", params=PARAMS) as r:
                filename = f"{FOLDER_NAME}/{table_id}_{int(time())}.xlsx"

                async with aiofiles.open(
                    filename,
                    mode="wb",
                ) as export_file:
                    await export_file.write(await r.read())
                    logger.info("Файл расписания {} успешно загружен.", table_id)
                    return filename

        except Exception as e:  # noqa: BLE001
            logger.error("Ошибка при загрузке файла: {}", e)
            return False

    def parse_lessons(self, table_filename: str) -> dict[str, list[list[str]]]:  # noqa: C901, PLR0912
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

        sheet = openpyxl.load_workbook(table_filename).active

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
                        cabinet = "---"
                    elif isinstance(row[i + 1].value, float):
                        cabinet = str(int(row[i + 1].value))
                    elif isinstance(row[i + 1].value, str):
                        cabinet = str(row[i + 1].value).strip().lower() or "0"
                    else:
                        raise IncorrectCabinetFormatError(row[i + 1])

                    lessons[cl][day].append(
                        f"{_normalize_lesson(lesson)}:{cabinet}",
                    )

            elif day == 5:  # После субботы — стоп
                break

        logger.info("Парсинг завершён успешно.")
        return {k: [_clear_day_lessons(x) for x in v] for k, v in lessons.items()}
