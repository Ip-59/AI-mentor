import json
import time

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown
from IPython.core.magic import register_line_magic, register_cell_magic

from .lesson import create_new_lesson


@register_line_magic
def reload_learnly(line):
    """Перезагружает модуль LearnlyEngine"""
    import importlib
    import sys
    if 'learnly_engine' in sys.modules:
        importlib.reload(sys.modules['learnly_engine'])
    return "LearnlyEngine перезагружен"


# Автоматически регистрируем магическую команду при импорте этого модуля
get_ipython().register_magic_function(reload_learnly, 'line')


# TODO: способность задавать проверочные вопросы
# - создавать задания для ученика
# - давать возможность их выполнить и предъявить решение и ответ
# - проверить и написать отзыв для ученика - AI


class LearnlyEngine:
    def __init__(self):
        self.lesson = create_new_lesson()

    def show_hint(self, task_num: int) -> None:
        """Показывает подсказку для указанного задания"""
        if task_num in self.memory['tasks']:
            display(Markdown(f"💡 **Подсказка:** {self.memory['tasks'][task_num]['hint']}"))
            self.create_solution_cell(self.memory['tasks'][task_num]['problem'])
        else:
            display(Markdown("❌ Не удалось найти текущее задание"))

    def create_solution_cell(self, problem: str) -> None:
        """Создает новую ячейку с магической командой"""
        shell = get_ipython()

        # Разбиваем текст задания на строки по 80 символов
        wrapped_problem = []
        words = problem.split()
        current_line = "# "

        for word in words:
            if len(current_line + word) > 77:  # 77 = 80 - 3 для "# " в начале
                wrapped_problem.append(current_line)
                current_line = "# " + word
            else:
                current_line += (" " + word if current_line != "# " else word)

        wrapped_problem.append(current_line)
        problem_text = "\n".join(wrapped_problem)

        shell.set_next_input(
            f"%%check_solution\n\n"
            f"{problem_text}\n"
            f"# Напишите ваше решение здесь:\n\n",
            replace=False
        )

    def show_task(self, task_num: int):
        """Показывает задание с указанным номером"""
        if task_num not in self.memory['tasks']:
            # Если задания еще нет, генерируем его
            task = self.get_next_task()
            if not task:
                display(Markdown("❌ Не удалось сгенерировать задание"))
                return

        display(Markdown(f"### Задание {task_num}\\n{self.memory['tasks'][task_num]['problem']}"))
        self.create_solution_cell(self.memory['tasks'][task_num]['problem'])

    def check_solution(self, cell: str, user_namespace: dict) -> None:
        """Проверяет решение пользователя"""
        clean_cell = cell.strip().lower()

        if any(word in clean_cell for word in ['hint', 'help']):
            self.show_hint(self.current_task)
            return

        if 'finish' in clean_cell:
            self.finish_lesson()
            return

        if 'skip' in clean_cell:
            self.skip_task()
            return

        # TODO

        if self.current_task in self.memory['tasks']:
            task = self.memory['tasks'][self.current_task]
            try:
                if task['check'](user_namespace):
                    display(Markdown(f"✅ {task['success']}"))
                    time.sleep(1)
                    self.advance_to_next_task()
                else:
                    display(Markdown(f"❌ {task['error']}"))
                    self.create_solution_cell(task['problem'])
            except Exception as e:
                display(Markdown(f"❌ Ошибка при проверке: {str(e)}"))
                self.create_solution_cell(task['problem'])


    def finish_lesson(self):
        """Завершает текущий урок"""

        # TODO

        completed_tasks = len(self.memory['tasks'])
        display(Markdown(
            f"### 🎉 Поздравляем!\n"
            f"Вы завершили урок, выполнив {completed_tasks} заданий!\n"
            f"Ваши достижения:\n"
            f"* Количество выполненных заданий: {completed_tasks}\n"
            f"* Изученные темы: {', '.join(task['problem'].split()[0:3] + ['...'] for task in self.memory['tasks'].values())}\n"
        ))

    def start_lesson(self) -> None:
        display(Markdown(
            "# Добро пожаловать в Learnly!\n"
            "Это интерактивный обучающий ноутбук.\n"
            "Как выполнять задания:\n"
            "1. В появившейся ячейке напишите своё решение\n"
            "2. Запустите ячейку (Shift + Enter)\n"
            "3. Получите обратную связь и следующее задание!"
        ))
        display(Markdown(
            "💡 Нужна подсказка? Напишите 'hint' или 'help' в ячейке с %%check_solution"
        ))
        time.sleep(1)

        # TODO:
        # Загружаем прогресс урока
        with open("lesson.json", "r") as f:
            lesson = json.load(f)

        # TODO:
        # цикл
        #   создаем новую часть урока
        #   если часть урока - это текст - выводим его, выводим ячейку с возможнымикомандами

        #   если часть урока - это задание для ученика - выводим его как код, ждем решения
        #   обрабатываем команду ученика
        #     Если "дальше" - продолжаем цикл
        #     Если "расскажи подробнее" - выводим подсказку
        #     Если "приведи пример кода" - выводим пример кода
        #     Если "закончи урок" - завершаем урок
        #     ...
        #   Сохраняем прогресс урока
