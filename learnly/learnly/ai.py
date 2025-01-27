# TODO:
# Обращаемся к AI и просим его написать задание (на основе контекста урока). Вот пример:
# {
#     'problem': 'Создайте переменную x и присвойте ей значение 42',
#     'hint': 'Используйте оператор присваивания =, например: переменная = значение',
#     'check': lambda ns: 'x' in ns and ns['x'] == 42,
#     'error': 'Нужно создать переменную x со значением 42',
#     'success': 'Отлично! Задание выполнено правильно!'
# },


import openai
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Устанавливаем API ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_ml_task(context: str = None) -> dict:
    """
    Генерирует задание по машинному обучению с помощью OpenAI API.
    
    :param context: Контекст урока (например, предыдущие задания или тема).
    :return: Словарь с заданием, подсказкой, функцией проверки и сообщениями.
    """
    # Формируем промпт для генерации задания
    prompt = (
        "Ты — AI-учитель по машинному обучению. Сгенерируй задание для ученика. "
        "Задание должно быть связано с машинным обучением и Python. "
        "Вот пример задания:\n"
        "{\n"
        "    'problem': 'Создайте модель линейной регрессии с помощью библиотеки scikit-learn.',\n"
        "    'hint': 'Используйте класс LinearRegression из sklearn.linear_model.',\n"
        "    'check': lambda ns: 'LinearRegression' in ns and callable(ns['LinearRegression']),\n"
        "    'error': 'Нужно создать модель линейной регрессии.',\n"
        "    'success': 'Отлично! Модель линейной регрессии создана!'\n"
        "}\n"
        "Сгенерируй новое задание. Оно должно быть сложнее предыдущего."
    )

    if context:
        prompt += f"\nКонтекст: {context}"

    # Вызываем OpenAI API для генерации задания
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Можно использовать gpt-4, если доступен
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
        task = eval(generated_text)  # Преобразуем строку в словарь
        return task
    except Exception as e:
        print(f"Ошибка при парсинге задания: {e}")
        return None

# Пример использования
if __name__ == "__main__":
    # Генерация задания
    task = generate_ml_task()
    if task:
        print("Сгенерированное задание:")
        print(task)
    else:
        print("Не удалось сгенерировать задание.")