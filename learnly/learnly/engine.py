from asyncio import current_task
import os
import json
import time, datetime, openai
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown, HTML
import ipywidgets as widgets

__all__ = ['LearnlyEngine', 'LessonPart', 'TextPart', 'CodePart', 'AssignmentPart']

# Проверяем, находимся ли мы в IPython окружении
ipython = get_ipython()
if ipython is not None:
    from IPython.core.magic import register_line_magic, register_cell_magic

    def reload_learnly(line):
        """Перезагружает модуль LearnlyEngine"""
        import importlib
        import sys
        if 'learnly_engine' in sys.modules:
            importlib.reload(sys.modules['learnly_engine'])
        return "LearnlyEngine перезагружен"

    # Регистрируем магическую команду только если мы в IPython
    ipython.register_magic_function(reload_learnly, 'line')

from .lesson import create_new_lesson
from .display import LearnlyDisplay

LESSON_FILE = "lesson.json"  # добавлено ChatGPT


# TODO: способность задавать проверочные вопросы
# - создавать задания для ученика
# - давать возможность их выполнить и предъявить решение и ответ
# - проверить и написать отзыв для ученика - AI


# Базовый класс для частей урока
class LessonPart(ABC):
    def __init__(self, content: str, hint: str = "", example: str = ""):
        self.content = content
        self.hint = hint
        self.example = example
        self.timestamp = time.time()

    @abstractmethod
    def display(self, display_instance: Any, part_index: int) -> None:
        """Отображает содержимое части урока"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует часть урока в словарь для сохранения"""
        return {
            "content": self.content,
            "hint": self.hint,
            "example": self.example,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LessonPart':
        """Создает часть урока из словаря"""
        instance = cls(
            content=data.get("content", ""),
            hint=data.get("hint", ""),
            example=data.get("example", "")
        )
        instance.timestamp = data.get("timestamp", time.time())
        return instance


class TextPart(LessonPart):
    """Часть урока с теоретическим материалом"""

    def display(self, display_instance: Any, part_index: int) -> None:
        """Отображает текстовую часть урока"""
        display_instance.show_text_content(self.content, part_index)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует текстовую часть в словарь"""
        data = super().to_dict()
        data["type"] = "text"
        return data


class CodePart(LessonPart):
    """Часть урока с примером кода"""

    def display(self, display_instance: Any, part_index: int) -> None:
        """Отображает пример кода"""
        display_instance.show_text_content(self.content, part_index)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует часть с кодом в словарь"""
        data = super().to_dict()
        data["type"] = "code"
        return data


class AssignmentPart(LessonPart):
    """Часть урока с заданием"""

    def __init__(self, content: str, hint: str = "", example: str = "",
                 success_message: str = "Отлично! Задание выполнено верно.",
                 error_message: str = "Проверьте ваше решение и попробуйте снова."):
        super().__init__(content, hint, example)
        self.success_message = success_message
        self.error_message = error_message

    def display(self, display_instance: Any, part_index: int) -> None:
        """Отображает задание"""
        display_instance.show_assignment(self.content, part_index)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует задание в словарь"""
        data = super().to_dict()
        data["type"] = "assignment"
        data["success_message"] = self.success_message
        data["error_message"] = self.error_message
        return data


class Lesson:
    """Класс для работы с уроком"""

    def __init__(self, title: str, parts: List[LessonPart] = None):
        self.title = title
        self.parts = parts or []

    def add_part(self, part: LessonPart) -> None:
        """Добавляет часть в урок"""
        self.parts.append(part)

    def to_dict(self) -> Dict[str, Any]:
        """Преобразует урок в словарь для сохранения"""
        return {
            "title": self.title,
            "parts": [part.to_dict() for part in self.parts]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Lesson':
        """Создает урок из словаря"""
        lesson = cls(data.get("title", "Без названия"))
        for part_data in data.get("parts", []):
            part_type = part_data.get("type")
            if part_type == "text":
                part = TextPart.from_dict(part_data)
            elif part_type == "assignment":
                part = AssignmentPart.from_dict(part_data)
            else:
                continue
            lesson.add_part(part)
        return lesson


class LearnlyEngine:
    """Основной класс для управления процессом обучения"""

    def __init__(self):
        self.lesson = create_new_lesson()
        self.display = LearnlyDisplay()
        self.lesson_progress: List[Dict[str, Any]] = []
        self.lesson_file = "lesson.json"
        self.current_part_index: int = 1
        self.memory: Dict[str, Any] = {'tasks': {}}

        # Создаём (или очищаем) JSON файл с прогрессом урока
        self._save_progress()

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

    def _wrap_text(self, text: str, max_length: int = 77) -> str:
        """Разбивает текст на строки по указанной максимальной длине"""
        words = text.split()
        lines = []
        current_line = "# "

        for word in words:
            if len(current_line + word) > max_length:
                lines.append(current_line)
                current_line = "# " + word
            else:
                current_line += (" " + word if current_line != "# " else word)

        lines.append(current_line)
        return "\n".join(lines)

    def create_solution_cell(self, problem: str) -> None:
        """Создает новую ячейку с магической командой"""
        shell = get_ipython()
        wrapped_problem = self._wrap_text(problem)
        shell.set_next_input(
            f"%%check_solution\n\n{wrapped_problem}\n# Напишите ваше решение здесь:\n\n",
            replace=False
        )

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Получает следующее задание"""
        # Реальная реализация должна генерировать или получать задания
        # Пример реализации:
        task = {
            'problem': f'Задание {len(self.memory["tasks"]) + 1}: Напишите функцию для...',
            'hint': 'Используйте стандартные операторы Python...',
            'success': 'Отлично! Задание выполнено правильно.',
            'error': 'В вашем решении есть ошибка. Попробуйте еще раз.',
            'check': lambda ns: 'solution' in ns and callable(ns['solution'])
        }
        task_index = len(self.memory["tasks"])
        self.memory['tasks'][task_index] = task
        return task

    def check_solution(self, cell: str, user_namespace: dict) -> None:
        """Проверяет решение пользователя"""
        clean_cell = cell.strip().lower()

        if any(word in clean_cell for word in ['hint', 'help']):
            self.show_hint(self.current_part_index)
            return

        if 'finish' in clean_cell:
            self.finish_lesson()
            return

        if 'skip' in clean_cell:
            self.skip_task()
            return

        task_index = self.current_part_index
        if task_index in self.memory['tasks']:
            task = self.memory['tasks'][task_index]
            try:
                if task['check'](user_namespace):
                    self.display.show_success(task['success'])
                    time.sleep(1)
                    self.advance_to_next_task()
                else:
                    self.display.show_error(task['error'])
                    self.create_solution_cell(task['problem'])
            except Exception as e:
                self.display.show_error(f"Ошибка при проверке: {str(e)}")
                self.create_solution_cell(task['problem'])

    def show_hint(self, task_index: int) -> None:
        """Показывает подсказку для указанного задания"""
        if task_index in self.memory['tasks']:
            self.display.show_hint(self.memory['tasks'][task_index]['hint'])
            self.create_solution_cell(self.memory['tasks'][task_index]['problem'])

            # Сохраняем запрос подсказки в прогресс урока
            self.lesson_progress.append({
                "part_index": task_index,
                "action": "запрос_подсказки",
                "timestamp": time.time()
            })
            self._save_progress()
        else:
            self.display.show_error("Не удалось найти текущее задание")

    def show_task(self, task_index: int) -> None:
        """Показывает задание с указанным номером"""
        if task_index not in self.memory['tasks']:
            task = self.get_next_task()
            if not task:
                self.display.show_error("Не удалось сгенерировать задание")
                return

        self.display.show_assignment(
            self.memory['tasks'][task_index]['problem'],
            task_index
        )
        self.create_solution_cell(self.memory['tasks'][task_index]['problem'])

        # Сохраняем показ задания в прогресс урока
        self.lesson_progress.append({
            "part_index": task_index,
            "type": "assignment",
            "content": self.memory['tasks'][task_index]['problem'],
            "timestamp": time.time()
        })
        self._save_progress()

    def finish_lesson(self) -> None:
        """Завершает урок и показывает сводку"""
        # Сохраняем завершение урока в прогресс
        self.lesson_progress.append({
            "action": "finish_lesson",
            "timestamp": time.time()
        })
        self._save_progress()

        # Показываем сообщение о завершении
        self.display.show_text_content("## Урок завершён\n\nВсе части урока пройдены.", -1)

        # Показываем статистику
        completed_parts = len([p for p in self.lesson_progress if p.get("type") in ["text", "assignment"]])
        total_parts = len(self.lesson.parts)

        stats = f"""
### Статистика урока:
- Пройдено частей: {completed_parts} из {total_parts}
- Время выполнения: {int((time.time() - self.lesson_progress[0]["timestamp"]) / 60)} минут
"""
        self.display.show_text_content(stats, -1)

    def start_lesson(self) -> None:
        """Начинает урок"""
        self.display.show_welcome_message()

        # Загружаем прогресс урока если он есть
        try:
            with open(self.lesson_file, "r", encoding="utf-8") as f:
                self.lesson_progress = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.lesson_progress = []
        
        current_step = self.get_current_step() # добавлено Игорь

        # Показываем текущий прогресс
        self.display.show_lesson_progress(self.lesson_progress)

        # Запускаем интерактивный урок
        self.begin_lesson()

    def advance_to_next_task(self) -> None:
        """Переходит к следующему заданию"""
        self.current_part_index += 1
        self.show_task(self.current_part_index)

    def skip_task(self) -> None:
        """Пропускает текущее задание"""
        # Сохраняем пропуск задания в прогресс
        self.lesson_progress.append({
            "part_index": self.current_part_index,
            "action": "пропуск_задания",
            "timestamp": time.time()
        })
        self._save_progress()

        self.advance_to_next_task()

    def _save_progress(self) -> None:
        """Сохраняет прогресс урока в файл"""
        try:
            with open(self.lesson_file, "w", encoding="utf-8") as f:
                json.dump(self.lesson_progress, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении прогресса: {str(e)}")

    def _create_command_widget(self) -> widgets.HBox:
        """Создает виджет с кнопками для управления уроком"""
        next_button = widgets.Button(
            description='Дальше',
            button_style='',
            icon='arrow-right',
            style={
                'button_color': '#E6F7FF',  # очень светлый голубой
                'text_color': '#1A4971',    # очень темный синий
                'font_weight': 'normal'
            }
        )

        details_button = widgets.Button(
            description='Подробнее',
            button_style='',
            icon='info',
            style={
                'button_color': '#E3F2FF',  # очень светлый голубой
                'text_color': '#1E3A5F',    # очень темный синий
                'font_weight': 'normal'
            }
        )

        example_button = widgets.Button(
            description='Пример',
            button_style='',
            icon='code',
            style={
                'button_color': '#E8F7ED',  # очень светлый зеленый
                'text_color': '#1C4532',    # очень темный зеленый
                'font_weight': 'normal'
            }
        )

        finish_button = widgets.Button(
            description='Закончить урок',
            button_style='',
            icon='check',
            style={
                'button_color': '#D4C6CC',  # очень светлый серо-розовый
                'text_color': '#2D3748',    # очень темный серый
                'font_weight': 'normal'
            }
        )

        # Добавляем отступы между кнопками
        return widgets.HBox(
            [next_button, details_button, example_button, finish_button],
            layout=widgets.Layout(
                gap='10px',
                padding='5px'
            )
        )

    def _handle_button_click(self, button: widgets.Button, part: LessonPart) -> None:
        """Обрабатывает нажатие кнопок управления уроком"""
        if button.description == 'Дальше':
            self.current_part_index += 1
            if self.current_part_index < len(self.lesson.parts):
                self._display_current_part()
            else:
                self.finish_lesson()
        elif button.description == 'Подробнее':
            self.display.show_hint(part.hint)
            self.lesson_progress.append({
                "part_index": self.current_part_index,
                "action": "расскажи подробнее",
                "detail": part.hint,
                "timestamp": time.time()
            })
            self._save_progress()
        elif button.description == 'Пример':
            self.display.show_example(part.example)
            self.lesson_progress.append({
                "part_index": self.current_part_index,
                "action": "приведи пример кода",
                "example": part.example,
                "timestamp": time.time()
            })
            self._save_progress()
        elif button.description == 'Закончить урок':
            self.finish_lesson()

    def _display_current_part(self) -> None:
        """Отображает текущую часть урока"""
        if self.current_part_index >= len(self.lesson.parts):
            self.finish_lesson()
            return

        current_part = self.lesson.parts[self.current_part_index]

        # Отображаем содержимое части урока
        current_part.display(self.display, self.current_part_index)

        # Если это задание, добавляем поле для ввода
        if isinstance(current_part, AssignmentPart):
            answer_widget = widgets.Textarea(
                placeholder='Введите ваш ответ здесь...',
                description='Ваш ответ:',
                rows=5,
                style={'description_width': 'initial'}
            )
            display(answer_widget)

        # Сохраняем в прогресс урока
        self.lesson_progress.append({
            "type": current_part.__class__.__name__.lower().replace('part', ''),
            "content": current_part.content,
            "part_index": self.current_part_index,
            "timestamp": time.time()
        })
        self._save_progress()

        # Создаем и отображаем кнопки управления
        command_buttons = self._create_command_widget()
        for button in command_buttons.children:
            button.on_click(lambda b, part=current_part: self._handle_button_click(b, part))
        display(command_buttons)

    def begin_lesson(self) -> None:
        """Запускает урок"""
        # Создаем новый урок
        self.lesson = Lesson("Введение в Python")

        # Добавляем части урока
        parts = [
            TextPart(
                content="Добро пожаловать на урок по Python! Сегодня мы познакомимся с основными концепциями языка.",
                hint="Python – это интерпретируемый язык, удобный для быстрого прототипирования.",
                example="print('Hello, world!')"
            ),
            AssignmentPart(
                content="Напишите функцию, которая принимает два числа и возвращает их сумму.",
                hint="Подумайте, как объявить функцию и вернуть результат.",
                example="def add(a, b):\n    return a + b"
            ),
            TextPart(
                content="Отлично! Вы успешно справились с заданием. Продолжим изучение более сложных конструкций.",
                hint="Возможно, стоит обратить внимание на условные операторы и циклы.",
                example=""
            )
        ]

        # Добавляем части в урок
        for part in parts:
            self.lesson.add_part(part)

        self.current_part_index = 0
        self._display_current_part()

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
