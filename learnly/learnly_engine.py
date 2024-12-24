import time

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown
from IPython.core.magic import register_line_magic, register_cell_magic


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


class LearnlyEngine:
    def __init__(self):
        self.current_task = 1
        self.tasks = {
            1: {
                'title': 'Создайте переменную x и присвойте ей значение 42',
                'hint': 'Используйте оператор присваивания =, например: variable = value',
                'check': lambda ns: 'x' in ns and ns['x'] == 42,
                'error': 'Нужно создать переменную x со значением 42',
                'success': 'Отлично! Задание выполнено правильно!'
            },
            2: {
                'title': 'Создайте список numbers, содержащий числа от 1 до 5',
                'hint': '''Списки создаются с помощью квадратных скобок: [1, 2, ...]''',
                'check': lambda ns: ('numbers' in ns and
                                   isinstance(ns['numbers'], list) and
                                   ns['numbers'] == [1, 2, 3, 4, 5]),
                'error': 'Список numbers должен содержать числа от 1 до 5 в порядке возрастания',
                'success': 'Превосходно! Вы справились со вторым заданием!'
            },
            3: {
                'title': 'Напишите функцию square(n), которая возвращает квадрат числа n',
                'hint': '''                    Функция определяется так:
                    def square(n):
                        return ...''',
                'check': lambda ns: ('square' in ns and
                                   callable(ns['square']) and
                                   all(ns['square'](n) == n*n for n in [-2, 0, 4])),
                'error': 'Функция square должна возвращать квадрат числа. Проверьте случаи: square(4)=16, square(0)=0, square(-2)=4',
                'success': 'Отлично! Функция square работает правильно!'
            }
        }

    def show_hint(self, task_num: int) -> None:
        """Показывает подсказку для указанного задания"""
        if task_num in self.tasks:
            display(Markdown(f"💡 **Подсказка:** {self.tasks[task_num]['hint']}"))
            self.create_solution_cell(self.tasks[task_num]['title'])
        else:
            display(Markdown("❌ Не удалось найти текущее задание"))

    def create_solution_cell(self, title: str) -> None:
        """Создает новую ячейку с магической командой"""
        shell = get_ipython()
        shell.set_next_input(f'%%check_solution\n\n# {title}\n# Напишите ваше решение здесь:\n\n', replace=False)

    def show_task(self, task_num: int) -> None:
        """Показывает задание с указанным номером"""
        if task_num in self.tasks:
            display(Markdown(f"### Задание {task_num}\n{self.tasks[task_num]['title']}"))
            self.create_solution_cell(self.tasks[task_num]['title'])

    def check_solution(self, cell: str, user_namespace: dict) -> None:
        """Проверяет решение пользователя"""
        clean_cell = cell.strip().lower()

        if any(word in clean_cell for word in ['hint', 'help']):
            self.show_hint(self.current_task)
            return

        if self.current_task in self.tasks:
            task = self.tasks[self.current_task]
            try:
                if task['check'](user_namespace):
                    display(Markdown(f"✅ {task['success']}"))
                    time.sleep(1)

                    self.current_task += 1
                    if self.current_task in self.tasks:
                        self.show_task(self.current_task)
                    else:
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
                    self.create_solution_cell(task['title'])
            except Exception as e:
                display(Markdown(f"❌ Ошибка при проверке: {str(e)}"))
                self.create_solution_cell(task['title'])

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
