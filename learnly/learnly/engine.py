import time

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown
from IPython.core.magic import register_line_magic, register_cell_magic

from .tasks import generate_ml_task


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
        self.current_task = 1

        # TODO:
        # Получаем задания от AI. См. файл learnly_ai.py

        task_knn = generate_ml_task("KNN")
        task_second = generate_ml_task(f"Уже выполненные задания: {task_knn['context']}")
        self.tasks = {
            1: task_knn,
            2: task_second,
        }

    def show_hint(self, task_num: int) -> None:
        """Показывает подсказку для указанного задания"""
        if task_num in self.tasks:
            display(Markdown(f"💡 **Подсказка:** {self.tasks[task_num]['hint']}"))
            self.create_solution_cell(self.tasks[task_num]['problem'])
        else:
            display(Markdown("❌ Не удалось найти текущее задание"))

    def create_solution_cell(self, problem: str) -> None:
        """Создает новую ячейку с магической командой"""
        shell = get_ipython()
        shell.set_next_input(
            f"%%check_solution\n\n"
            f"# {problem}\n"
            f"# Напишите ваше решение здесь:\n\n",
            replace=False
        )

    def show_task(self, task_num: int) -> None:
        """Показывает задание с указанным номером"""
        if task_num in self.tasks:
            display(Markdown(f"### Задание {task_num}\n{self.tasks[task_num]['problem']}"))
            self.create_solution_cell(self.tasks[task_num]['problem'])

    def check_solution(self, cell: str, user_namespace: dict) -> None:
        """Проверяет решение пользователя"""
        clean_cell = cell.strip().lower()

        if any(word in clean_cell for word in ['hint', 'help']):
            self.show_hint(self.current_task)
            return

        # TODO: добавить возможность пропустить задание: skip

        if self.current_task in self.tasks:
            task = self.tasks[self.current_task]
            try:

                if ('skip' in clean_cell) or task['check'](user_namespace):
                    display(Markdown(f"✅ {task['success']}"))
                    time.sleep(1)

                    self.current_task += 1
                    if self.current_task in self.tasks:
                        self.show_task(self.current_task)
                    else:
                        # TODO: добавить возможность завершить обучение
                        display(Markdown(
                            "### 🎉 Поздравляем! \n"
                            "Вы успешно завершили все задания!\n"
                            "Вы научились:\n"
                            "* Создавать переменные\n"
                            "* Работать со списками\n"
                            "* Создавать функции\n"
                        ))
                else:
                    display(Markdown(f"❌ {task['error']}"))
                    self.create_solution_cell(task['problem'])
            except Exception as e:
                display(Markdown(f"❌ Ошибка при проверке: {str(e)}"))
                self.create_solution_cell(task['problem'])

    def show_welcome(self) -> None:
        """Показывает приветственное сообщение"""
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
        self.show_task(self.current_task)
