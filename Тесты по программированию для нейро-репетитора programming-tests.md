# Тесты по программированию для нейро-репетитора

## 1. Базовые концепции Python

### Уровень 1: Переменные и типы данных
**Задание 1.1**
Напишите программу, которая принимает два числа и выводит их сумму, разность, произведение и частное.

```python
def basic_operations(a, b):
    # Ваш код здесь
    pass

# Тестовые случаи
test_cases = [
    {"input": (10, 2), "expected": (12, 8, 20, 5.0)},
    {"input": (7, 3), "expected": (10, 4, 21, 2.3333333333333335)}
]

def check_solution(func):
    for test in test_cases:
        a, b = test["input"]
        expected = test["expected"]
        try:
            result = func(a, b)
            assert result == expected, f"Для входных данных {a}, {b} ожидается {expected}, получено {result}"
            print(f"Тест пройден для входных данных {a}, {b}")
        except Exception as e:
            print(f"Ошибка для входных данных {a}, {b}: {str(e)}")
```

*Правильное решение:*
```python
def basic_operations(a, b):
    return (a + b, a - b, a * b, a / b)
```

*Оценка:* Проверяет базовое понимание арифметических операций и работы с числами в Python.

### Уровень 2: Списки и циклы
**Задание 1.2**
Напишите функцию, которая находит все числа в заданном диапазоне, которые делятся на 3 или на 5.

```python
def find_multiples(start, end):
    # Ваш код здесь
    pass

# Тестовые случаи
test_cases = [
    {"input": (1, 10), "expected": [3, 5, 6, 9, 10]},
    {"input": (1, 15), "expected": [3, 5, 6, 9, 10, 12, 15]}
]

def check_solution(func):
    for test in test_cases:
        start, end = test["input"]
        expected = test["expected"]
        try:
            result = func(start, end)
            assert result == expected, f"Для диапазона {start}-{end} ожидается {expected}, получено {result}"
            print(f"Тест пройден для диапазона {start}-{end}")
        except Exception as e:
            print(f"Ошибка для диапазона {start}-{end}: {str(e)}")
```

*Правильное решение:*
```python
def find_multiples(start, end):
    return [x for x in range(start, end+1) if x % 3 == 0 or x % 5 == 0]
```

## 2. Структуры данных

### Уровень 1: Словари
**Задание 2.1**
Напишите функцию, которая принимает список слов и возвращает словарь, где ключи - это слова, а значения - количество их появлений в списке.

```python
def word_frequency(words):
    # Ваш код здесь
    pass

# Тестовые случаи
test_cases = [
    {"input": ["apple", "banana", "apple", "cherry"], 
     "expected": {"apple": 2, "banana": 1, "cherry": 1}},
    {"input": ["cat", "dog", "cat", "cat", "dog"], 
     "expected": {"cat": 3, "dog": 2}}
]

def check_solution(func):
    for test in test_cases:
        input_data = test["input"]
        expected = test["expected"]
        try:
            result = func(input_data)
            assert result == expected, f"Для входных данных {input_data} ожидается {expected}, получено {result}"
            print(f"Тест пройден для входных данных {input_data}")
        except Exception as e:
            print(f"Ошибка для входных данных {input_data}: {str(e)}")
```

*Правильное решение:*
```python
def word_frequency(words):
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    return freq
```

### Уровень 2: Работа с массивами NumPy
**Задание 2.2**
Напишите функцию, которая создает матрицу 3x3, заполняет ее числами от 1 до 9 и возвращает сумму элементов на главной диагонали.

```python
import numpy as np

def diagonal_sum():
    # Ваш код здесь
    pass

# Тестовые случаи
def check_solution(func):
    try:
        result = func()
        expected = 15  # 1 + 5 + 9
        assert result == expected, f"Ожидается {expected}, получено {result}"
        print(f"Тест пройден. Сумма диагональных элементов: {result}")
    except Exception as e:
        print(f"Ошибка: {str(e)}")
```

*Правильное решение:*
```python
def diagonal_sum():
    matrix = np.array(range(1, 10)).reshape(3, 3)
    return np.trace(matrix)
```

## 3. Функции и алгоритмы

### Уровень 1: Простые алгоритмы
**Задание 3.1**
Напишите функцию, которая находит наибольший общий делитель (НОД) двух чисел по алгоритму Евклида.

```python
def gcd(a, b):
    # Ваш код здесь
    pass

# Тестовые случаи
test_cases = [
    {"input": (48, 18), "expected": 6},
    {"input": (54, 24), "expected": 6},
    {"input": (17, 13), "expected": 1}
]

def check_solution(func):
    for test in test_cases:
        a, b = test["input"]
        expected = test["expected"]
        try:
            result = func(a, b)
            assert result == expected, f"Для чисел {a} и {b} ожидается НОД {expected}, получено {result}"
            print(f"Тест пройден для чисел {a} и {b}")
        except Exception as e:
            print(f"Ошибка для чисел {a} и {b}: {str(e)}")
```

*Правильное решение:*
```python
def gcd(a, b):
    while b:
        a, b = b, a % b
    return a
```

### Уровень 2: Работа с данными
**Задание 3.2**
Напишите функцию, которая принимает список чисел и возвращает скользящее среднее с окном размера 3.

```python
def moving_average(numbers):
    # Ваш код здесь
    pass

# Тестовые случаи
test_cases = [
    {"input": [1, 2, 3, 4, 5], 
     "expected": [2.0, 3.0, 4.0]},
    {"input": [2, 4, 6, 8], 
     "expected": [4.0, 6.0]}
]

def check_solution(func):
    for test in test_cases:
        input_data = test["input"]
        expected = test["expected"]
        try:
            result = func(input_data)
            assert result == expected, f"Для входных данных {input_data} ожидается {expected}, получено {result}"
            print(f"Тест пройден для входных данных {input_data}")
        except Exception as e:
            print(f"Ошибка для входных данных {input_data}: {str(e)}")
```

*Правильное решение:*
```python
def moving_average(numbers):
    return [sum(numbers[i:i+3])/3 for i in range(len(numbers)-2)]
```

## Система оценки

За каждое правильно решенное задание:
- Уровень 1: 1 балл
- Уровень 2: 2 балла

Дополнительные баллы:
- За оптимальность решения: +0.5 балла
- За использование продвинутых конструкций языка: +0.5 балла

Общая оценка:
- 0-3 балла: Базовый уровень Python
- 4-7 баллов: Средний уровень
- 8-10 баллов: Продвинутый уровень

## Рекомендации по результатам

- Базовый уровень: 
  - Изучить основные структуры данных Python
  - Практиковаться в решении алгоритмических задач
  - Освоить работу с библиотекой NumPy

- Средний уровень:
  - Углубить знания алгоритмов
  - Изучить продвинутые возможности Python
  - Начать работу с pandas и основами машинного обучения

- Продвинутый уровень:
  - Готов к изучению сложных концепций машинного обучения
  - Рекомендуется практика на реальных проектах
  - Изучение дополнительных библиотек для работы с данными
