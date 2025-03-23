import os
import json
import time
import datetime
import openai  # добавлено ChatGPT
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown, HTML
import ipywidgets as widgets

__all__ = ['LearnlyEngine', 'LessonPart', 'TextPart', 'CodePart', 'AssignmentPart']

from .lesson import create_new_lesson
from .display import LearnlyDisplay

LESSON_FILE = "lesson.json"  # добавлено ChatGPT

class LearnlyEngine:
    """Основной класс для управления процессом обучения"""
    
    def __init__(self):
        print("[DEBUG] Инициализация LearnlyEngine")
        self.lesson_data = self.read_lesson_file()
        if not self.lesson_data:
            print("[DEBUG] Файл lesson.json не найден. Создаём новый...")
            self.lesson_data = self.initialize_lesson_file()  # добавлено ChatGPT
        self.current_step = self.get_current_step()
        print(f"[DEBUG] Текущий шаг: {self.current_step}")

    def read_lesson_file(self) -> Optional[Dict[str, Any]]:  # добавлено ChatGPT
        """Считывает lesson.json"""
        print("[DEBUG] Чтение файла lesson.json")
        if os.path.exists(LESSON_FILE):
            with open(LESSON_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return None

    def save_lesson_file(self):  # добавлено ChatGPT
        """Сохраняет изменения в lesson.json"""
        print("[DEBUG] Сохранение файла lesson.json")
        with open(LESSON_FILE, "w", encoding="utf-8") as f:
            json.dump(self.lesson_data, f, ensure_ascii=False, indent=2)

    def initialize_lesson_file(self) -> Dict[str, Any]:  # добавлено ChatGPT
        """Создаёт lesson.json с начальными данными"""
        print("[DEBUG] Инициализация lesson.json")
        lesson_data = {
            "student_name": "Пример студента",
            "total_hours": 100,
            "difficulty_level": "начинающий",
            "start_date": datetime.datetime.now().isoformat(),
            "average_score": 0.0,
            "course_outline": self.generate_course_outline("начинающий", 100)  # добавлено ChatGPT
        }
        self.save_lesson_file()
        return lesson_data

    def generate_course_outline(self, difficulty_level: str, total_hours: int) -> List[Dict[str, Any]]:  # добавлено ChatGPT
        """Запрашивает у OpenAI программу курса AI/ML"""
        prompt = f"""
        Создай учебную программу по курсу AI/ML для студента с уровнем {difficulty_level}.
        Учитывай, что студент знает основы Python. Курс рассчитан на {total_hours} часов.
        
        Программа должна содержать список шагов, последовательное изучение тем.
        Пример формата:
        [
            {"step": 1, "title": "Введение в машинное обучение", "description": "Основные концепции AI и ML."},
            {"step": 2, "title": "Основы Python для AI/ML", "description": "Переменные, циклы, функции."}
        ]
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты - AI-преподаватель по машинному обучению."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        try:
            return json.loads(response["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"Ошибка при генерации курса: {e}")
            return []

    def get_current_step(self) -> Optional[Dict[str, Any]]:  # исправлено ChatGPT
        """Возвращает текущий шаг обучения (следующий после завершенного)"""
        print("[DEBUG] Определение текущего шага")
        for step in self.lesson_data["course_outline"]:
            if step["score"] is None:
                return step
        return None

    def start_next_step(self):  # исправлено ChatGPT
        """Начинает следующий шаг курса"""
        print("[DEBUG] Запуск следующего шага")
        if not self.current_step:
            print("Курс завершён!")
            return
        self.current_step["status"] = "in_progress"
        self.current_step["start_time"] = datetime.datetime.now().isoformat()
        self.save_lesson_file()
        print(f"[DEBUG] Начат шаг: {self.current_step['title']}")
        print(f"## {self.current_step['title']}\n{self.current_step['description']}")

    def complete_current_step(self, score: float):  # исправлено ChatGPT
        """Завершает текущий шаг курса и обновляет lesson.json"""
        print(f"[DEBUG] Завершение шага: {self.current_step}")
        if not self.current_step:
            print("Нет активного шага обучения.")
            return
        self.current_step["status"] = "completed"
        self.current_step["end_time"] = datetime.datetime.now().isoformat()
        self.current_step["score"] = score
        self.lesson_data["average_score"] = sum(
            s["score"] for s in self.lesson_data["course_outline"] if s["score"] is not None) / len(
            [s for s in self.lesson_data["course_outline"] if s["score"] is not None])
        self.save_lesson_file()
        print(f"[DEBUG] Шаг '{self.current_step['title']}' завершён с оценкой {score}.")
        self.current_step = self.get_current_step()
        print(f"[DEBUG] Новый текущий шаг: {self.current_step}")
        self.start_next_step()

# --- Использование ---
engine = LearnlyEngine()
engine.start_next_step()
