Для представления блок-схемы проекта AI-учителя в более приятном и наглядном виде я использую структурированный подход с помощью markdown. Это включает таблицы, списки и текстовые обозначения потоков данных, чтобы сделать схему понятной и удобной для восприятия.

---

## Блок-схема проекта AI-учителя

### Основные компоненты проекта
- **Точка входа**: `learnly.ipynb` — файл, запускающий весь процесс.
- **Модули**:
  - `lesson.py` — содержит класс `Lesson` для управления уроками.
  - `engine.py` — содержит класс `LearnlyEngine` для управления процессом обучения.
- **JSON-файлы**:
  - `<email>_data.json` — хранит данные студента и прогресс.
  - `lesson.json` — хранит структуру урока.
  - `<email>_protocol.json` — логирует взаимодействия.

---

### Поток данных и взаимодействие

#### 1. Точка входа: `learnly.ipynb`
- **Описание**: Основной файл, который запускает систему и собирает начальные данные.
- **Действия**:
  1. Запрашивает у пользователя:
     - Имя
     - E-mail
     - Часы на обучение
     - Уровень сложности
     - Типы заданий
  2. Создает или читает файл `<email>_data.json`.
  3. Инициализирует класс `Lesson`.
  4. Инициализирует класс `LearnlyEngine`.
  5. Запускает метод `start_lesson_loop()` для начала урока.
- **Поток данных**:
  ```
  Пользователь → Ввод данных → learnly.ipynb → <email>_data.json
  learnly.ipynb → Lesson → lesson.json
  learnly.ipynb → LearnlyEngine → start_lesson_loop()
  ```

#### 2. Класс `Lesson` (`lesson.py`)
- **Описание**: Управляет структурой урока и его частями.
- **Атрибуты**:
  - `parts` — список частей урока.
  - `last_two_parts` — последние две части урока.
  - `lesson_file` — путь к файлу `lesson.json`.
- **Методы**:
  - `__init__(lesson_file)` — инициализирует урок и загружает данные.
  - `load_lesson()` — загружает или создает `lesson.json`.
  - `add_part(new_part)` — добавляет новую часть в урок.
  - `get_part(index)` — возвращает часть урока по индексу.
- **Поток данных**:
  ```
  learnly.ipynb → Lesson.__init__ → load_lesson → lesson.json
  Lesson.add_part → Обновление lesson.json
  Lesson.get_part → Передача данных в LearnlyEngine
  ```

#### 3. Класс `LearnlyEngine` (`engine.py`)
- **Описание**: Управляет процессом обучения и взаимодействием со студентом.
- **Атрибуты**:
  - `student_data` — данные студента.
  - `lesson` — объект класса `Lesson`.
  - `protocol_file` — путь к `<email>_protocol.json`.
- **Методы**:
  - `__init__(student_data, lesson, protocol_file)` — инициализирует движок.
  - `start_lesson_loop()` — запускает цикл урока.
  - `log_interaction(role, message_type, content)` — записывает действия в лог.
  - `update_student_data(part, time_spent, answer, grade)` — обновляет данные студента.
  - `evaluate_answer(part, answer)` — оценивает ответы студента.
- **Поток данных**:
  ```
  learnly.ipynb → LearnlyEngine.__init__
  LearnlyEngine.start_lesson_loop → Lesson.get_part → Вывод студенту
  Студент → Ввод → LearnlyEngine → log_interaction → <email>_protocol.json
  LearnlyEngine → update_student_data → <email>_data.json
  evaluate_answer → update_student_data
  ```

#### 4. JSON-файлы
- **Описание**: Хранят данные для работы системы.
- **Типы**:
  - `<email>_data.json` — данные студента и прогресс.
  - `lesson.json` — структура урока.
  - `<email>_protocol.json` — лог взаимодействий.
- **Поток данных**:
  ```
  learnly.ipynb ↔ <email>_data.json
  Lesson ↔ lesson.json
  LearnlyEngine ↔ <email>_protocol.json
  LearnlyEngine ↔ <email>_data.json
  ```

---

### Текстовая блок-схема

```
+---------------------------+
|       learnly.ipynb       |
+---------------------------+
| 1. Запрос данных          |
| 2. <email>_data.json      |
| 3. Инициализация Lesson   |
| 4. Инициализация Engine   |
| 5. start_lesson_loop()    |
+---------------------------+
            ↓
+---------------------------+
|         Lesson            |
+---------------------------+
| - parts                   |
| - last_two_parts          |
| - lesson_file             |
| - load_lesson()           |
| - add_part()              |
| - get_part()              |
+---------------------------+
            ↓
+---------------------------+
|      LearnlyEngine        |
+---------------------------+
| - student_data            |
| - lesson                  |
| - protocol_file           |
| - start_lesson_loop()     |
| - log_interaction()       |
| - update_student_data()   |
| - evaluate_answer()       |
+---------------------------+
            ↓
+---------------------------+
|       JSON-файлы          |
+---------------------------+
| - <email>_data.json       |
| - lesson.json             |
| - <email>_protocol.json   |
+---------------------------+
```

---

### Как это работает
1. **Пользователь** вводит свои данные в `learnly.ipynb`.
2. **`learnly.ipynb`** сохраняет их в `<email>_data.json`.
3. Создается объект `Lesson`, который загружает или создает `lesson.json`.
4. Создается объект `LearnlyEngine`, который запускает цикл обучения через `start_lesson_loop()`.
5. **`LearnlyEngine`**:
   - Получает части урока из `Lesson`.
   - Выводит их студенту.
   - Обрабатывает ответы, логирует действия в `<email>_protocol.json` и обновляет прогресс в `<email>_data.json`.

---

Эта структура делает блок-схему проекта AI-учителя максимально наглядной и понятной, сохраняя всю необходимую информацию о компонентах и их взаимодействии.