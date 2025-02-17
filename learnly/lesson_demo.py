import os
from pprint import pprint

import openai
from dotenv import load_dotenv

from learnly.lesson import create_new_lesson, generate_lesson_part


# Загружаем переменные окружения из файла .env
load_dotenv()

# Устанавливаем API ключ для OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')


lesson = create_new_lesson()


new_lesson_part = generate_lesson_part(lesson)
print("Следующий кусок урока:")
pprint(new_lesson_part)

lesson["parts"].append(new_lesson_part)
print("Обновленный урок:")
pprint(lesson)


new_lesson_part = generate_lesson_part(lesson)
print("Следующий кусок урока:")
pprint(new_lesson_part)

lesson["parts"].append(new_lesson_part)
print("Обновленный урок:")
pprint(lesson)
