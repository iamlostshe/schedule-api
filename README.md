# SCHEDULE-API

> Предположительно, наиболее вероятное развитие для школьного расписания.

> Создавалось, в основном, для удобного использования расписания из Siri на iPhone.
>
> Просто сказав: "Привет Siri, расписание на завтра" вы можете получить ваше расписание.
>
> Видео демонстрации работы:
>
> <img style="max-width: 400px;" src="res/video_command_ios.gif">
>
> Ссылка на команду: https://www.icloud.com/shortcuts/5b35da0f815a49699aefd67ca42bb78a
>

> Хостится на сервере, для личного использования:
>
> [http://37.252.22.124:8000/](http://37.252.22.124:8000/?table_id=1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU&week_days=this_day&my_class=10%D0%B0)

API для получения расписания из google таблицы.

## Инструкция по использованию

1. Получите ссылку на вашу таблицу с расписанием:

```
https://docs.google.com/spreadsheets/d/1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU/edit?gid=1414560720#gid=1414560720
```

> **Если в вашей школе еще не используется подобный подход к ведению расписания**, вы можете обратиться к администрации.
> 
> Они могут скопировать [таблицу](https://docs.google.com/spreadsheets/d/1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU) и заполнить ее своими данными.
>
> После чего воспользутесь этой инструкцией.


2. Уберите лишние параметры:

~~https://docs.google.com/spreadsheets/d/~~

1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU

~~/edit?gid=1414560720#gid=1414560720~~

3. Таким образом у нас остаётся лишь необходимый нам параметр `table_id`:

```
table_id=1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU
```

4. Укажите необходимый вам класс (`my_class`):

```
my_class=10а
```

Класс указвается в типичном формате, например:

`10а`, `7б`, `6д`.

5. Укажите день недели на который необходимо расписание (`week_day`):

День недели можно указать в 3-х форматах, на русском/английском (регистр не учитывается):

| Полное название | Сокращение | Полное название (ru) | Сокращение (ru) | Число |
| --------------- | ---------- | -------------------- | --------------- | ----- |
| Monday          | Mo         | понедельник          | пн              | 0     |
| Tuesday         | Tu         | вторник              | вт              | 1     |
| Wednesday       | We         | среда                | ср              | 2     |
| Thursday        | Th         | четверг              | чт              | 3     |
| Friday          | Fr         | пятница              | пт              | 4     |
| Saturday        | Sa         | суббота              | сб              | 5     |

> Использование воскресенья недопустимо!!!

и относительные варианты

Получить расписание на сегодня - `this_day`.
Получить расписание на завтра - `next_day`.

> Если необходима информация на несколько дней, можно указать дни через запятую.

6. Формируем запрос:

```
http://127.0.0.1:8000/?table_id=1pP_qEHh4PBk5Rsb7Wk9iVbJtTA11O9nTQbo1JFjnrGU&week_day=next_day&my_class=10а
```

и получаем ответ в формате:

```json
[
  {
    "entry_lesson": 1,
    "lessons": [
      "Физ(у)/инф(у)",
      "Физ(у)/инф(у)",
      "Инф(б)/физ(б)",
      "Геометрия",
      "Обзр",
      "Физкультура",
      "Общест.(б)"
    ],
    "cabinets": [
      "321/307",
      "321/307",
      "307/321",
      "204",
      "108",
      "330",
      "313"
    ]
  },
  {
    "entry_lesson": 4,
    "lessons": [
      "None",
      "None",
      "None",
      "Алгебра",
      "Английский язык",
      "География",
      "Английский язык",
      "Английский язык"
    ],
    "cabinets": [
      "0",
      "0",
      "0",
      "204",
      "305",
      "317",
      "305",
      "305"
    ]
  }
]
```
