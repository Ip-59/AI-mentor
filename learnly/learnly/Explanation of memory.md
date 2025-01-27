Как это работает:
Локальное хранение:

Данные сохраняются в JSON-файл на локальном компьютере.

Методы _save_to_local и _load_from_local отвечают за сохранение и загрузку данных.

Google Drive:

Данные сохраняются на Google Drive с помощью API.

Методы _save_to_google_drive и _load_from_google_drive отвечают за загрузку и скачивание файла.

Для работы с Google Drive требуется файл credentials.json, который можно получить через Google Cloud Console.

Основные функции:

update_progress — обновляет прогресс выполнения заданий.

add_error — добавляет ошибку в список ошибок.

update_context — обновляет контекст урока.

get_progress, get_errors, get_context — возвращают сохраненные данные.

Пример использования:
python
Copy
# Локальное хранилище
memory = LearnlyMemory(storage_type="local", file_path="learnly_memory.json")

# Обновляем прогресс
memory.update_progress(task_id=1, status="completed")
memory.add_error("Ошибка в задании 1: неправильное использование функции.")
memory.update_context("last_lesson", "Линейная регрессия")

# Получаем данные
print("Прогресс:", memory.get_progress())
print("Ошибки:", memory.get_errors())
print("Контекст:", memory.get_context())

# Google Drive (требуется credentials.json и token.json)
# memory = LearnlyMemory(storage_type="google_drive", file_path="learnly_memory.json", google_drive_folder_id="ваш_folder_id")
Что нужно для запуска:
Локальное хранилище:

Ничего дополнительно настраивать не нужно.

Google Drive:

Создайте проект в Google Cloud Console.

Включите API Google Drive.

Скачайте файл credentials.json и поместите его в корень проекта.

При первом запуске система запросит авторизацию и создаст файл token.json.

Итог:
Этот код реализует систему памяти для проекта Learnly с поддержкой локального хранения и Google Drive. Он позволяет сохранять прогресс, ошибки и контекст уроков, а также восстанавливать их при необходимости.
