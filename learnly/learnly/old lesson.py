# Обращаемся к AI и просим его написать задание (на основе контекста урока). Вот пример:
# {
#     'problem': 'Создайте переменную x и присвойте ей значение 42',
#     'hint': 'Используйте оператор присваивания =, например: переменная = значение',
#     'check': lambda ns: 'x' in ns and ns['x'] == 42,
#     'error': 'Нужно создать переменную x со значением 42',
#     'success': 'Отлично! Задание выполнено правильно!'
# },

# Еще примеры заданий:
# self.tasks = {
#     1: {
#         'problem': 'Создайте переменную x и присвойте ей значение 42',
#         'hint': 'Используйте оператор присваивания =, например: переменная = значение',
#         'check': lambda ns: 'x' in ns and ns['x'] == 42,
#         'error': 'Нужно создать переменную x со значением 42',
#         'success': 'Отлично! Задание выполнено правильно!'
#     },
#     2: {
#         'problem': 'Создайте список numbers, содержащий числа от 1 до 5',
#         'hint': '''Списки создаются с помощью квадратных скобок: [1, 2, ...]''',
#         'check': lambda ns: ('numbers' in ns and
#                            isinstance(ns['numbers'], list) and
#                            ns['numbers'] == [1, 2, 3, 4, 5]),
#         'error': 'Список numbers должен содержать числа от 1 до 5 в порядке возрастания',
#         'success': 'Превосходно! Вы справились со вторым заданием!'
#     },
#     3: {
#         'problem': 'Напишите функцию square(n), которая возвращает квадрат числа n',
#         'hint': '''                    Функция определяется так:
#             def square(n):
#                 return ...''',
#         'check': lambda ns: ('square' in ns and
#                            callable(ns['square']) and
#                            all(ns['square'](n) == n*n for n in [-2, 0, 4])),
#         'error': 'Функция square должна возвращать квадрат числа. Проверьте случаи: square(4)=16, square(0)=0, square(-2)=4',
#         'success': 'Отлично! Функция square работает правильно!'
#     }
#}

from typing import Any, Dict
import openai, os, json


# lesson_part - это словарь, который содержит информацию о кусочке урока.
# lesson_part["type"] - тип кусочка урока.
# lesson_part["content"] - содержание кусочка урока.

def create_new_lesson():
    return {
        "parts": [
            {
                "type": "text",
                "content": "Здравствуйте! Давайте начнем наш урок.",
            },
            {
                "type": "code",
                "content": "print('Hello, world!')",
            },
            {
                "type": "text",
                "content": "Этот код выводит на экран приветствие.",
            },
        ],
    }



def generate_lesson_part(lesson) -> dict:
    prompt = (
        "Сгенерируй следующий кусок урока."
        "Учитывай следующие правила:\n"
        "1. Кусок урока должен быть связан предыдущими кусочками урока. "
        "2. Новые кусочки урока должны опираться на знания из предыдущих. "
        "3. Не повторять уже разобранные кусочки урока. "
    )
    prompt += (
        f"\n\nУрок на данный момент:\n{lesson}\n\n"
    )
    prompt += (
        "Сгенерируй задание в формате JSON:\n"
        "{\n"
        "    'type': 'text',\n"
        "    'content': [текст создаваемого кусочка урока],\n"
        "}\n"
        "Выведи задание в формате JSON, **не используй Markdown**."
    )

    # Вызываем OpenAI API для генерации задания
    response = openai.ChatCompletion.create(   # TODO: openai 0.28.* -> openai 1.*
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты — AI-учитель по машинному обучению."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7
    )

    # Извлекаем сгенерированный текст
    generated_text = response['choices'][0]['message']['content'].strip()

    # Парсим сгенерированный текст в словарь
    try:
        new_lesson_part = eval(generated_text)
        return new_lesson_part
    except Exception as e:
        print(f"Ошибка при парсинге сгенерированного моделью текста: {e}")
        print(f"Сгенерированный текст:\n{generated_text}")
        return None
    
# от ChatGPT для Игоря: Функция проверки существования файла
def check_file_exists(filename):
    """Проверяет, существует ли файл на диске."""
    return os.path.isfile(filename)

# Функция чтения JSON
def load_json_data(filename):
    """Загружает JSON-данные из файла и возвращает как Python-объект (словарь или список)."""
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# Функция записи JSON
def save_json_data(filename, data):
    """Сохраняет Python-объект data в JSON-файл filename (перезапись)."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_or_load_lesson_json(lesson_filename):
    """
    Проверяет, существует ли lesson.json. Если нет, создаёт с двумя "жёстко зашитыми" частями.
    Возвращает структуру lesson.json (dict).
    """
    if not check_file_exists(lesson_filename):
        # Создаём
        lesson_data = {
            "parts": [
                {
                    "part_number": 1,
                    "topic": "Введение в машинное обучение",
                    "type": "text",
                    "content": "Это первая часть лекции по теме 'Введение в ML'."
                },
                {
                    "part_number": 2,
                    "topic": "Введение в машинное обучение",
                    "type": "multiple_choice",
                    "content": "Выберите правильный вариант, что называется 'обучением с учителем'?"
                }
            ]
        }
        save_json_data(lesson_filename, lesson_data)
        return lesson_data
    else:
        lesson_data = load_json_data(lesson_filename)
        return lesson_data

def create_new_lesson_part(lesson_data, new_topic=None):
    """
    Генерирует новую часть урока на базе последних двух частей (хранит их в памяти),
    чтобы избежать повторений. Для упрощения здесь просто добавим фиктивную часть.
    
    Аргумент new_topic используется, если нужно добавить часть к новой теме,
    иначе можно продолжать в той же теме.
    """
    parts = lesson_data["parts"]
    part_number = len(parts) + 1

    # Получим последние 2 части (если их меньше, берём все, что есть).
    last_parts = parts[-2:]  # Срез последних двух

    # Псевдо-генерация (на реальном проекте можно вызвать ChatGPT API).
    # Будем считать, что новая часть - это "open_question".
    new_part = {
        "part_number": part_number,
        "topic": new_topic if new_topic else (last_parts[-1]["topic"] if last_parts else "Новая тема"),
        "type": "open_question",
        "content": f"Автоматически сгенерированный вопрос {part_number} (продолжение предыдущих частей)."
    }

    parts.append(new_part)
    return new_part