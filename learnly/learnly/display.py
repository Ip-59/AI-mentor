from IPython.display import display, Markdown
import json
import time
from typing import Dict, List, Any, Optional


class LearnlyDisplay:
    """Класс для управления отображением урока (будет дорабатываться)"""

    def show_welcome_message(self) -> None:
        display(Markdown(
            "# Добро пожаловать в Learnly!\n"
            "Это интерактивный обучающий ноутбук.\n"
            "Как выполнять задания:\n"
            "1. В появившейся ячейке напишите своё решение\n"
            "2. Запустите ячейку (Shift + Enter)\n"
            "3. Получите обратную связь и следующее задание!"
        ))
        # TODO
        # display(Markdown(
        #     "💡 Нужна подсказка? Напишите 'hint' или 'help' в ячейке с %%check_solution"
        # ))
        time.sleep(0.5)

    def show_text_content(self, content: str, part_index: int) -> None:
        display(Markdown(f"### {part_index + 1}. Часть\n{content}"))

    def show_assignment(self, content: str, part_index: int) -> None:
        display(Markdown(f"### {part_index + 1}. Задание\n{content}"))

    def show_hint(self, hint: str) -> None:
        display(Markdown(f"💡 **Подсказка:** {hint}"))

    def show_example(self, example: str) -> None:
        display(Markdown(f"📝 **Пример кода:**\n```python\n{example}\n```"))

    def show_success(self, message: str) -> None:
        display(Markdown(f"✅ {message}"))

    def show_error(self, message: str) -> None:
        display(Markdown(f"❌ {message}"))

    def show_lesson_progress(self, progress: List[Dict[str, Any]]) -> None:
        for entry in progress:
            if entry.get("type") == "text":
                display(Markdown(f"### {entry['part_index'] + 1}. Часть\n{entry['content']}"))
            elif entry.get("type") == "assignment":
                display(Markdown(f"### {entry['part_index'] + 1}. Задание\n{entry['content']}"))
                if "student_answer" in entry:
                    display(Markdown(f"**Ответ ученика:**\n```python\n{entry['student_answer']}\n```"))

    def show_lesson_summary(self, completed_tasks: int, topics: List[str]) -> None:
        display(Markdown(
            f"### Поздравляем!\n"
            f"Вы завершили урок, выполнив {completed_tasks} заданий!\n"
            f"Ваши достижения:\n"
            f"* Количество выполненных заданий: {completed_tasks}\n"
            f"* Изученные темы: {', '.join(topics)}\n"
        ))
