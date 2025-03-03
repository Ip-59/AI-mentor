import os
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

        
        # Инициализируем список для хранения прогресса урока
        self.lesson_progress = []
                
        # Определяем путь к файлу прогресса урока
        self.lesson_file = "lesson.json"
        
        # Создаём (или очищаем) JSON файл с прогрессом урока в самом начале урока
        with open(self.lesson_file, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)


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

# Функция для красивого вывода текста лекции и прогресса урока из JSON файла
# Создано ChatGPT для Игоря
    def display_lesson_and_progress():
        """
        Выводит на экран:
        1. Текст лекции (фильтруя записи типа 'text')
        2. Полный прогресс урока, сохранённый в lesson.json
        
        Данные выводятся в отформатированном виде для удобства чтения.
        """
        lesson_file = "lesson.json"
        
        if os.path.exists(lesson_file):
            with open(lesson_file, "r", encoding="utf-8") as f:
                lesson_progress = json.load(f)
        else:
            print("Файл с прогрессом урока не найден.")
            return
        
        print("\n===== Текст лекции =====")
        for entry in lesson_progress:
            if entry.get("type") == "text":
                print(f"Часть {entry.get('part_index')}: {entry.get('content')}")
        
        print("\n===== Прогресс урока =====")
        # Выводим весь прогресс в формате JSON с отступами для лучшей читаемости
        print(json.dumps(lesson_progress, ensure_ascii=False, indent=4))


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
        with open(self.lesson_file, "r") as f:
            self.lesson_progress = json.load(f)

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

    # Создано ChatGPT для Игоря
    # def begin_lesson():
        """
        Запускает цикл урока с интерактивной обработкой ввода ученика.
        
        Функция:
        - Инициализирует список для хранения прогресса урока;
        - Создаёт (очищает) файл lesson.json в начале урока;
        - Поочередно выводит части урока (текст или задание);
        - Обрабатывает команды ученика: "дальше", "расскажи подробнее",
            "приведи пример кода" или "закончи урок";
        - Сохраняет все действия (вывод, ответы, команды) в список словарей.
        
        Каждый элемент списка имеет следующую структуру (пример):
        {
            "part_index": <номер части урока>,
            "type": "text" или "assignment",
            "content": <текст урока или задание>,
            "action": <команда ученика, если применимо>,
            "student_answer": <ответ ученика, если применимо>,
            "timestamp": <метка времени>
        }
        
        По завершении урока список сохраняется в JSON-файл lesson.json.
        
        Создано ChatGPT для Игоря.
        """
        
        # Пример структуры урока: список частей, каждая из которых описывается словарём.
        # Поля:
        #   type: "text" – обычный текст лекции,
        #         "assignment" – задание для ученика;
        #   content: содержание текста или задание;
        #   hint: дополнительная подсказка (опционально);
        #   example: пример кода для иллюстрации (опционально).
        lesson_parts = [
            {
                "type": "text",
                "content": "Добро пожаловать на урок по Python! Сегодня мы познакомимся с основными концепциями языка.",
                "hint": "Python – это интерпретируемый язык, удобный для быстрого прототипирования.",
                "example": "print('Hello, world!')"
            },
            {
                "type": "assignment",
                "content": "Напишите функцию, которая принимает два числа и возвращает их сумму.",
                "hint": "Подумайте, как объявить функцию и вернуть результат.",
                "example": "def add(a, b):\n    return a + b"
            },
            {
                "type": "text",
                "content": "Отлично! Вы успешно справились с заданием. Продолжим изучение более сложных конструкций.",
                "hint": "Возможно, стоит обратить внимание на условные операторы и циклы.",
                "example": ""
            }
        ]
        
        part_index = 0  # Индекс текущей части урока
        
        # Бесконечный цикл урока (выход из цикла – исчерпание всех частей урока или команда 'закончи урок')
        while True:
            # Если все части урока пройдены, завершаем цикл
            if part_index >= len(lesson_parts):
                print("\nУрок завершён: все части пройдены.")
                break
            
            current_part = lesson_parts[part_index]
            
            # Если часть урока – текст лекции
            if current_part["type"] == "text":
                print("\n--- Часть урока (текст) ---")
                print(current_part["content"])
                print("\nДоступные команды: 'дальше', 'расскажи подробнее', 'приведи пример кода', 'закончи урок'")
                
                # Сохраняем вывод текста в прогресс урока
                self.lesson_progress.append({
                    "part_index": part_index,
                    "type": "text",
                    "content": current_part["content"],
                    "timestamp": time.time()
                })
                
                # Читаем команду ученика
                command = input("Введите команду: ").strip().lower()
                
                if command == "дальше":
                    part_index += 1
                    continue
                elif command == "расскажи подробнее":
                    print("\nПодсказка:")
                    print(current_part.get("hint", "Подробная информация отсутствует."))
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "расскажи подробнее",
                        "detail": current_part.get("hint", ""),
                        "timestamp": time.time()
                    })
                elif command == "приведи пример кода":
                    print("\nПример кода:")
                    example_code = current_part.get("example", "Пример кода отсутствует.")
                    print(example_code)
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "приведи пример кода",
                        "example": example_code,
                        "timestamp": time.time()
                    })
                elif command == "закончи урок":
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "закончи урок",
                        "timestamp": time.time()
                    })
                    break
                else:
                    print("Неизвестная команда. Продолжаем урок.")
            
            # Если часть урока – задание для ученика
            elif current_part["type"] == "assignment":
                print("\n--- Задание для ученика ---")
                print("Задание (код):")
                print(current_part["content"])
                print("\nОжидается выполнение задания. Введите ваш код или комментарий, а затем введите команду для продолжения (например, 'дальше', 'расскажи подробнее', 'приведи пример кода', 'закончи урок').")
                
                # Сохраняем задание в прогресс
                self.lesson_progress.append({
                    "part_index": part_index,
                    "type": "assignment",
                    "content": current_part["content"],
                    "timestamp": time.time()
                })
                
                # Получаем ответ ученика (код или комментарий)
                student_answer = input("Ваш ответ на задание:\n")
                self.lesson_progress.append({
                    "part_index": part_index,
                    "student_answer": student_answer,
                    "timestamp": time.time()
                })
                
                # Читаем команду ученика
                command = input("Введите команду: ").strip().lower()
                
                if command == "дальше":
                    part_index += 1
                    continue
                elif command == "расскажи подробнее":
                    print("\nПодсказка:")
                    print(current_part.get("hint", "Подробная информация отсутствует."))
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "расскажи подробнее",
                        "detail": current_part.get("hint", ""),
                        "timestamp": time.time()
                    })
                elif command == "приведи пример кода":
                    print("\nПример кода:")
                    example_code = current_part.get("example", "Пример кода отсутствует.")
                    print(example_code)
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "приведи пример кода",
                        "example": example_code,
                        "timestamp": time.time()
                    })
                elif command == "закончи урок":
                    self.lesson_progress.append({
                        "part_index": part_index,
                        "action": "закончи урок",
                        "timestamp": time.time()
                    })
                    break
                else:
                    print("Неизвестная команда. Продолжаем урок.")
            
            # После обработки текущей части переходим к следующей
            part_index += 1

        # По завершении урока сохраняем весь прогресс в JSON файл lesson.json
        with open(self.lesson_file, "w", encoding="utf-8") as f:
            json.dump(self.lesson_progress, f, ensure_ascii=False, indent=4)
        print("\nПрогресс урока сохранен в файле", self.lesson_file)


# Если модуль запускается напрямую, запускаем урок и затем выводим прогресс
#if __name__ == "__main__":
#    begin_lesson()
#    display_lesson_and_progress()