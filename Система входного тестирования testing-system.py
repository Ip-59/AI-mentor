import time
import random
import numpy as np
from typing import Dict, List, Tuple, Any, Callable

class TestingSystem:
    def __init__(self):
        self.results = {
            'logic': 0,
            'programming': 0,
            'ai_concepts': 0
        }
        self.detailed_results = {
            'logic': {},
            'programming': {},
            'ai_concepts': {}
        }
        self.total_score = 0
        self.user_name = ""

    def start(self):
        print("Добро пожаловать в систему тестирования для нейро-репетитора!")
        self.user_name = input("Пожалуйста, введите ваше имя: ")
        print(f"\nЗдравствуйте, {self.user_name}! Сейчас мы проведем тестирование по трем направлениям:")
        print("1. Логическое и алгоритмическое мышление")
        print("2. Практическое программирование")
        print("3. Базовые концепции ИИ")
        input("\nНажмите Enter, чтобы начать тестирование...")

        self.run_logic_test()
        self.run_programming_test()
        self.run_ai_concepts_test()
        self.show_final_results()

    def run_logic_test(self):
        print("\n=== Тест на логическое и алгоритмическое мышление ===")
        
        # Примеры заданий
        tasks = [
            {
                'question': 'Определите следующее число в последовательности: 2, 4, 8, 16, ...',
                'options': ['24', '28', '32', '36'],
                'correct': 2,
                'explanation': 'Каждое следующее число получается умножением предыдущего на 2'
            },
            {
                'question': 'У вас есть 3 сосуда: 8 литров, 5 литров и 3 литра. Можно ли отмерить ровно 4 литра воды?',
                'options': ['Да', 'Нет'],
                'correct': 0,
                'explanation': 'Можно наполнить 5л сосуд, перелить из него в 3л, останется 2л. Вылить 3л сосуд, перелить в него 2л. Снова наполнить 5л и долить в 3л сосуд 1л. В 5л сосуде останется 4л.'
            }
        ]

        score = 0
        for i, task in enumerate(tasks, 1):
            print(f"\nЗадание {i}:")
            print(task['question'])
            for j, option in enumerate(task['options']):
                print(f"{chr(97 + j)}) {option}")
            
            answer = input("Ваш ответ (введите букву): ").lower()
            answer_index = ord(answer) - ord('a')
            
            if answer_index == task['correct']:
                print("Правильно!")
                score += 1
            else:
                print("Неверно.")
            print("Объяснение:", task['explanation'])

        self.results['logic'] = score
        self.detailed_results['logic'] = {'total_tasks': len(tasks), 'correct': score}

    def run_programming_test(self):
        print("\n=== Тест по программированию ===")
        
        def test_function(func: Callable, test_cases: List[Dict], task_name: str) -> int:
            score = 0
            for i, test in enumerate(test_cases, 1):
                try:
                    result = func(*test['input']) if isinstance(test['input'], tuple) else func(test['input'])
                    if result == test['expected']:
                        print(f"Тест {i} пройден")
                        score += 1
                    else:
                        print(f"Тест {i} не пройден. Ожидалось: {test['expected']}, Получено: {result}")
                except Exception as e:
                    print(f"Ошибка в тесте {i}: {str(e)}")
            return score

        tasks = [
            {
                'name': 'Сумма чисел',
                'description': 'Напишите функцию, которая принимает два числа и возвращает их сумму.',
                'function_template': 'def add_numbers(a, b):\n    # Ваш код здесь\n    pass',
                'test_cases': [
                    {'input': (2, 3), 'expected': 5},
                    {'input': (-1, 5), 'expected': 4}
                ]
            }
        ]

        total_score = 0
        for task in tasks:
            print(f"\nЗадание: {task['description']}")
            print("Шаблон функции:")
            print(task['function_template'])
            
            user_code = input("Введите ваше решение (все в одну строку, замените pass на ваш код):\n")
            
            try:
                # Безопасное выполнение кода пользователя
                local_dict = {}
                exec(user_code, {"__builtins__": {}}, local_dict)
                func = local_dict[task['name'].lower().replace(' ', '_')]
                
                score = test_function(func, task['test_cases'], task['name'])
                total_score += score
                
            except Exception as e:
                print(f"Ошибка при выполнении кода: {str(e)}")

        self.results['programming'] = total_score
        self.detailed_results['programming'] = {'total_tasks': len(tasks), 'correct': total_score}

    def run_ai_concepts_test(self):
        print("\n=== Тест по базовым концепциям ИИ ===")
        
        questions = [
            {
                'question': 'Что из перечисленного является примером задачи машинного обучения?',
                'options': [
                    'Сортировка массива чисел',
                    'Распознавание лиц на фотографии',
                    'Вычисление суммы элементов в списке',
                    'Создание резервной копии данных'
                ],
                'correct': 1
            },
            {
                'question': 'Что такое переобучение (overfitting) в машинном обучении?',
                'options': [
                    'Ситуация, когда модель слишком хорошо запоминает тренировочные данные',
                    'Ситуация, когда модель учится слишком медленно',
                    'Ситуация, когда модели не хватает вычислительных ресурсов',
                    'Ситуация, когда датасет слишком маленький'
                ],
                'correct': 0
            }
        ]

        score = 0
        for i, q in enumerate(questions, 1):
            print(f"\nВопрос {i}:")
            print(q['question'])
            for j, option in enumerate(q['options']):
                print(f"{j + 1}) {option}")
            
            try:
                answer = int(input("Ваш ответ (введите номер): ")) - 1
                if answer == q['correct']:
                    print("Правильно!")
                    score += 1
                else:
                    print("Неверно. Правильный ответ:", q['options'][q['correct']])
            except ValueError:
                print("Пожалуйста, введите число.")

        self.results['ai_concepts'] = score
        self.detailed_results['ai_concepts'] = {'total_tasks': len(questions), 'correct': score}

    def calculate_level(self, category: str) -> str:
        score = self.results[category]
        total = self.detailed_results[category]['total_tasks']
        percentage = (score / total) * 100
        
        if percentage >= 80:
            return "Продвинутый"
        elif percentage >= 50:
            return "Средний"
        else:
            return "Начальный"

    def get_recommendations(self, category: str, level: str) -> List[str]:
        recommendations = {
            'logic': {
                'Начальный': [
                    "Решайте больше логических задач и головоломок",
                    "Изучите основы алгоритмического мышления"
                ],
                'Средний': [
                    "Практикуйтесь в решении сложных алгоритмических задач",
                    "Изучите различные техники оптимизации алгоритмов"
                ],
                'Продвинутый': [
                    "Попробуйте свои силы в олимпиадном программировании",
                    "Изучите продвинутые алгоритмы и структуры данных"
                ]
            },
            'programming': {
                'Начальный': [
                    "Пройдите базовый курс по Python",
                    "Практикуйтесь в написании простых программ"
                ],
                'Средний': [
                    "Изучите продвинутые возможности Python",
                    "Начните работать с библиотеками для анализа данных"
                ],
                'Продвинутый': [
                    "Изучите лучшие практики написания кода",
                    "Начните работу над собственными проектами"
                ]
            },
            'ai_concepts': {
                'Начальный': [
                    "Изучите основные понятия и терминологию ИИ",
                    "Пройдите вводный курс по машинному обучению"
                ],
                'Средний': [
                    "Изучите различные алгоритмы машинного обучения",
                    "Начните практиковаться с простыми наборами данных"
                ],
                'Продвинутый': [
                    "Изучите продвинутые техники машинного обучения",
                    "Начните работу над реальными проектами в области ИИ"
                ]
            }
        }
        return recommendations[category][level]

    def show_final_results(self):
        print("\n=== Результаты тестирования ===")
        print(f"Студент: {self.user_name}")
        
        for category in self.results:
            score = self.results[category]
            total = self.detailed_results[category]['total_tasks']
            percentage = (score / total) * 100
            level = self.calculate_level(category)
            
            print(f"\n{category.upper()}:")
            print(f"Правильных ответов: {score} из {total} ({percentage:.1f}%)")
            print(f"Уровень: {level}")
            
            print("Рекомендации:")
            for rec in self.get_recommendations(category, level):
                print(f"- {rec}")

    def get_ai_tutor_path(self) -> List[str]:
        levels = {cat: self.calculate_level(cat) for cat in self.results}
        
        path = ["Начало обучения"]
        
        if all(level == "Продвинутый" for level in levels.values()):
            path.extend([
                "Продвинутые алгоритмы машинного обучения",
                "Глубокие нейронные сети",
                "Работа над реальными проектами"
            ])
        elif all(level != "Начальный" for level in levels.values()):
            path.extend([
                "Основы машинного обучения",
                "Практика с базовыми алгоритмами",
                "Введение в нейронные сети"
            ])
        else:
            path.extend([
                "Основы программирования Python",
                "Базовые алгоритмы",
                "Введение в машинное обучение"
            ])
        
        return path

if __name__ == "__main__":
    testing_system = TestingSystem()
    testing_system.start()
