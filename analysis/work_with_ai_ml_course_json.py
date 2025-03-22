"""Вот пример **структуры JSON-файла** и **Python-кода**, который:  

1. **Проверяет наличие JSON-файла** с данными о студенте и курсе.  
2. **Создает JSON-файл** с программой курса (если его нет).  
3. **Читает JSON-файл** и загружает данные.  
4. **Дополняет JSON-файл** записями о прохождении курса.  
5. **Генерирует программу курса через OpenAI API** *(нужно будет вставить свой API-ключ OpenAI)*.  

---

## **1️⃣ Пример структуры JSON-файла**
```json
{
  "student": {
    "name": "Иван Петров",
    "allocated_hours": 120,
    "difficulty_level": "beginner",
    "start_datetime": "2025-03-16 10:00:00",
    "average_score": 0.0
  },
  "course_steps": [
    {
      "step_number": 1,
      "title": "Введение в машинное обучение",
      "lesson_content": null,
      "start_time": null,
      "end_time": null,
      "score": null
    },
    {
      "step_number": 2,
      "title": "Основные типы машинного обучения",
      "lesson_content": null,
      "start_time": null,
      "end_time": null,
      "score": null
    }
  ]
}
```
🔹 В **"course_steps"** заранее загружаются **все шаги курса**, но **содержание лекций (lesson_content) не заполняется сразу** – оно будет запрашиваться у OpenAI по мере прохождения шагов.  

---

## **2️⃣ Код на Python для работы с JSON-файлом**
Этот код:
- **Проверяет наличие файла** `ai_ml_course.json`
- **Создает его** с программой курса, если файла нет (с запросом к OpenAI для генерации списка шагов)
- **Читает файл**
- **Дополняет файл данными о прохождении курса**

### **🔹 Установите необходимые библиотеки**
```bash
pip install openai json datetime
```

---

### **🔹 Основной код**
```python"""
import os
import json
import openai  # Не забудьте вставить ваш API-ключ
from datetime import datetime

# Укажите ваш OpenAI API-ключ
OPENAI_API_KEY = "your-api-key-here"

# Название JSON-файла
JSON_FILE = "ai_ml_course.json"


# 1️⃣ Функция для запроса к OpenAI на генерацию шагов курса
def generate_course_steps(allocated_hours, difficulty_level):
    prompt = f"""
    Создай подробную программу обучения по курсу AI/ML для студента {difficulty_level} уровня.
    Количество часов: {allocated_hours}.
    Программа должна включать логически завершенные шаги, занимая не более 1-2 экранов информации.
    Учитывай контрольные вопросы, мини-тесты и небольшие задания на написание кода.
    Перечисли все шаги в формате:
    1. Название шага
    2. Название шага
    ...
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    
    steps_text = response["choices"][0]["message"]["content"].strip().split("\n")
    
    course_steps = []
    for i, step in enumerate(steps_text, start=1):
        course_steps.append({
            "step_number": i,
            "title": step.strip(),
            "lesson_content": None,
            "start_time": None,
            "end_time": None,
            "score": None
        })
    
    return course_steps


# 2️⃣ Функция создания JSON-файла с программой курса (если файла нет)
def create_json_file():
    if os.path.exists(JSON_FILE):
        print("Файл уже существует.")
        return
    
    student_data = {
        "name": "Иван Петров",
        "allocated_hours": 120,
        "difficulty_level": "beginner",
        "start_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "average_score": 0.0
    }

    # Генерация шагов курса через OpenAI
    course_steps = generate_course_steps(student_data["allocated_hours"], student_data["difficulty_level"])

    course_data = {
        "student": student_data,
        "course_steps": course_steps
    }

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(course_data, f, indent=4, ensure_ascii=False)

    print("Файл создан: ai_ml_course.json")


# 3️⃣ Функция чтения JSON-файла
def read_json_file():
    if not os.path.exists(JSON_FILE):
        print("Файл не найден. Создаю новый.")
        create_json_file()
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data


# 4️⃣ Функция обновления JSON-файла после прохождения шага
def update_course_progress(step_number, score):
    data = read_json_file()
    
    for step in data["course_steps"]:
        if step["step_number"] == step_number:
            step["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            step["score"] = score
            step["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            break

    # Пересчитать средний балл студента
    scores = [s["score"] for s in data["course_steps"] if s["score"] is not None]
    if scores:
        data["student"]["average_score"] = sum(scores) / len(scores)

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Данные по шагу {step_number} обновлены.")


# 5️⃣ Функция генерации содержания лекции (по запросу к OpenAI)
def generate_lesson_content(step_number):
    data = read_json_file()
    
    step_title = next((s["title"] for s in data["course_steps"] if s["step_number"] == step_number), None)
    if not step_title:
        print("Шаг не найден.")
        return
    
    prompt = f"Создай учебный материал по теме '{step_title}' в курсе AI/ML. Объем: 1-2 экрана текста."
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )
    
    lesson_content = response["choices"][0]["message"]["content"].strip()
    
    for step in data["course_steps"]:
        if step["step_number"] == step_number:
            step["lesson_content"] = lesson_content
            break
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Содержание лекции для шага {step_number} добавлено.")


# Запуск скрипта: проверяем файл и создаем его при необходимости
if __name__ == "__main__":
    create_json_file()
    course_data = read_json_file()

    # Пример обновления данных (прохождение шага 1 с оценкой 85)
    update_course_progress(step_number=1, score=85)

    # Пример генерации содержания лекции для шага 1
    generate_lesson_content(step_number=1)


"""## **🔹 Как использовать код**
1️⃣ **Запустите код** – создастся файл `ai_ml_course.json` с программой курса.  
2️⃣ **После прохождения каждого шага** вызывайте `update_course_progress(step_number, score)`.  
3️⃣ **Чтобы получить лекцию по шагу** используйте `generate_lesson_content(step_number)`.  

🎯 **Этот код обеспечивает гибкую систему хранения данных о студенте и ходе обучения!** 🚀"""