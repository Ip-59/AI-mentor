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
import openai


# lesson_part - это словарь, который содержит информацию о кусочке урока.
# - lesson_part["type"] - тип кусочка урока.
# - lesson_part["content"] - содержимое кусочка урока.

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
    # TODO: openai 0.28.* -> openai 1.*
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты - AI-учитель по машинному обучению."},
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
