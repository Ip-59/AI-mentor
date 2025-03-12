import json, datetime, time, os

from IPython.core.getipython import get_ipython
from IPython.display import display, Markdown
from IPython.core.magic import register_line_magic, register_cell_magic

from .lesson import create_new_lesson, generate_lesson_part, check_file_exists, load_json_data, save_json_data
from .lesson import generate_or_load_lesson_json

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
    # def __init__(self):
    #     self.lesson = create_new_lesson()
    # от ChatGPT для Игоря
    def __init__(
        self,
        student_name=None,
        student_email=None,
        hours_planned=0,
        difficulty="средний",
        preferred_tasks=None,
        student_file_prefix="student_data",
        protocol_file_prefix="lesson_protocol"
        ):

        # Основной движок обучения. Хранит данные о студенте, управляет логикой урока.
        
        # от ChatGPT для Игоря: Здесь можно сохранить переданные данные студента в атрибутах
        self.student_name = student_name
        self.student_email = student_email
        self.hours_planned = hours_planned
        self.difficulty = difficulty
        self.preferred_tasks = preferred_tasks or []

        # Формируем имена файлов (например, 'ivan_data.json' и 'ivan_protocol.json')
        base_prefix = self.student_email.split("@")[0] if self.student_email else student_file_prefix
        self.student_data_filename = f"{base_prefix}_data.json"
        self.protocol_filename = f"{base_prefix}_protocol.json"

        # Пытаемся загрузить или создать файл с данными о студенте
        self.student_data = self.load_or_init_student_data()

        # Название основного lesson-файла (общий для всех)
        self.lesson_filename = "lesson.json"
        # Условно считаем, что есть лишь одна "активная тема" или одна тема за раз
        self.current_topic = "Введение в машинное обучение"

    def load_or_init_student_data(self):
        """ Загружает JSON файл с данными о студенте (progress), 
        если его нет — создает новую структуру. """

        if check_file_exists(self.student_data_filename):
            student_data = load_json_data(self.student_data_filename)
            return student_data
        else:
            # Создаём новую структуру
            now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            student_data = {
                "name": self.student_name,
                "email": self.student_email,
                "hours_planned": self.hours_planned,
                "difficulty": self.difficulty,
                "preferred_tasks": self.preferred_tasks,
                "topics_studied": [],
                "overall_rating": 0.0,
                "last_activity": now
            }
            save_json_data(self.student_data_filename, student_data)
            return student_data

    def update_student_data(self):
        # Сохраняет (перезаписывает) обновлённые данные о студенте в JSON.
        save_json_data(self.student_data_filename, self.student_data)

    def log_lesson_event(self, protocol_filename, event_data):
        # Добавляет запись в lesson_protocol.json (протокол занятия). 
        # При каждом событии (вывод текста, ввод ответа, команда и т.д.) добавляем запись с датой-временем.

        protocol = []
        if check_file_exists(protocol_filename):
            protocol = load_json_data(protocol_filename)

        # Добавляем метку времени, если нет
        if "timestamp" not in event_data:
            now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
            event_data["timestamp"] = now

        protocol.append(event_data)
        save_json_data(protocol_filename, protocol)

    # от ChatGPT для Игоря
    # Функции для расчёта рейтинга, обновления данных студента, логгирования и т. п.
    def calculate_overall_rating(self, student_data):
        # Пересчитывает общий рейтинг студента как среднее арифметическое всех оценок за задания

        all_grades = []
        if "topics_studied" not in student_data:
            return 0.0
        for topic in student_data["topics_studied"]:
            if "blocks" in topic:
                for block in topic["blocks"]:
                    if "tasks" in block:
                        for task in block["tasks"]:
                            grade = task.get("grade")
                            if grade is not None:
                                all_grades.append(grade)
        if not all_grades:
            return 0.0
        return sum(all_grades) / len(all_grades)


# это было в оригинале
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

    # def start_lesson_loop(self):
        """
        Запускает "бесконечный" цикл урока: 
        - получает следующую часть урока,
        - выводит её студенту,
        - обрабатывает команды пользователя,
        - фиксирует окончание урока либо по исчерпанию материалов, либо по команде "закончи урок"
        """
        # Инициализируем/загружаем lesson.json 
        lesson_data = generate_or_load_lesson_json(self.lesson_filename)

        # "Части урока" будем получать поочередно
        current_part_index = 0
        parts = lesson_data["parts"]  # общий массив частей

        # Цикл обучения
        while True:
            if current_part_index >= len(parts):
                # Если мы достигли конца массива частей - тема исчерпана
                print("Тема исчерпана, урок завершается.")
                self.finish_lesson()
                break

            part = parts[current_part_index]

            # Выводим часть урока
            part_type = part.get("type")
            part_content = part.get("content", "")

            # Логируем событие в протокол
            self.log_lesson_event(self.protocol_filename, {
                "role": "system",
                "message_type": f"lesson_part_{part_type}",
                "message_content": part_content
            })

            print(f"Часть {current_part_index+1}:")
            print(part_content)

            # Если это задание, здесь можно провести логику обработки ответа
            if part_type in ["multiple_choice", "open_question", "code_task"]:

                self.show_task(part_number=current_part_index+1)
                
                # Заставляем "пользователя" ввести ответ
                user_answer = input("Введите ваш ответ (или 'пропустить'): ")
                self.log_lesson_event(self.protocol_filename, {
                    "role": "student",
                    "message_type": "answer",
                    "answer_content": user_answer
                })
                # Для простоты выставим какую-то фиктивную оценку (например, 5)
                # или логику проверки, если multiple_choice.
                grade = 5
                # В реальном проекте здесь может быть разбор ответа, проверка, присвоение реальной оценки...

                # Сохраним информацию о задаче, времени и оценке в структуре student_data
                self.save_task_result_to_student_data(topic_name=self.current_topic,
                                                      part_index=current_part_index+1,
                                                      task_type=part_type,
                                                      student_answer=user_answer,
                                                      grade=grade,
                                                      time_spent=10)  # условные 10 минут

                # Пересчитаем рейтинг
                self.student_data["overall_rating"] = self.calculate_overall_rating(self.student_data)
                # Обновим дату последней активности
                self.student_data["last_activity"] = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
                # Сохраним
                self.update_student_data()

            # Предлагаем команды
            print("Доступные команды: [дальше], [расскажи подробнее], [приведи пример кода], [закончи урок]")
            user_command = input("Введите команду: ")
            user_command = user_command.strip().lower()

            self.log_lesson_event(self.protocol_filename, {
                "role": "student",
                "message_type": "command",
                "command": user_command
                })

            if user_command == "дальше":
                # Переходим к следующей части
                current_part_index += 1
                continue
            elif user_command == "расскажи подробнее":
                # Выводим подсказку
                hint_text = "Это дополнительное пояснение или более детальное описание..."
                print(hint_text)
                self.log_lesson_event(self.protocol_filename, {
                    "role": "system",
                    "message_type": "hint",
                    "message_content": hint_text
                })
                # после "расскажи подробнее" логика может остаться та же, ждём новой команды
                continue
            elif user_command == "приведи пример кода":
                code_example = "print('Пример кода: перебор массива...')"
                print(code_example)
                self.log_lesson_event(self.protocol_filename, {
                    "role": "system",
                    "message_type": "code_example",
                    "message_content": code_example
                })
                continue
            elif user_command == "закончи урок":
                print("Урок прерван по запросу студента.")
                self.finish_lesson()
                break
            else:
                print("Неизвестная команда. Переходим к следующей части.")
                current_part_index += 1

    def save_task_result_to_student_data(self, topic_name, part_index, task_type, student_answer, grade, time_spent):
        """
        Сохраняет результат выполнения задания в структуру student_data:
        - название темы
        - номер части
        - тип задания (multiple_choice, open_question, code_task)
        - сам ответ
        - оценку
        - затраченное время
        """
        # Ищем в student_data соответствующую тему, если нет - добавляем
        topics = self.student_data.setdefault("topics_studied", [])
        topic_entry = None
        for t in topics:
            if t.get("topic_name") == topic_name:
                topic_entry = t
                break
        if not topic_entry:
            topic_entry = {
                "topic_name": topic_name,
                "blocks": []
            }
            topics.append(topic_entry)

        # Для простоты считаем, что "каждая часть" - это "блок"
        block_data = {
            "block_number": part_index,
            "time_spent": time_spent,  # в минутах
            "tasks": [
                {
                    "task_type": task_type,
                    "answer": student_answer,
                    "grade": grade
                }
            ]
        }
        topic_entry["blocks"].append(block_data)

    def finish_lesson(self):
        # Действия при завершении урока: вывести итоговую оценку, сохранить данные, протокол, и т.д.
        overall_rating = self.student_data.get("overall_rating", 0)
        print(f"Ваш итоговый рейтинг: {overall_rating:.2f}")
        print("Урок завершён.")
        # Записываем финальные данные ещё раз
        self.update_student_data()
        # При необходимости, можно здесь "закрыть" урок, добавить запись в протокол
        self.log_lesson_event(self.protocol_filename, {
            "role": "system",
            "message_type": "lesson_finished",
            "message_content": f"Урок завершён, итоговый рейтинг: {overall_rating:.2f}"
        })
        
