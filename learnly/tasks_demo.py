from learnly.tasks import generate_ml_task
from learnly.memory import LearnlyMemory
from pprint import pprint

# Инициализация памяти
memory = LearnlyMemory(storage_type="local")

try:
    task = generate_ml_task("SVM")  # Генерация задания
    pprint(task)

    if task:
        memory.update_context("last_task", task)  # Сохраняем последнее задание
except Exception as e:
    print(f"Ошибка при генерации задания: {e}")
