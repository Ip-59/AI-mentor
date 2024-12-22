import json
from google.colab import drive
import os

# Подключение Google Drive
class DataManager:
    def __init__(self):
        self.drive_mounted = False
        self.data_file = "ai_teacher_data.json"
        self.data = {
            "course": {},
            "student": {
                "name": "",
                "gender": "",
                "preferred_address": ""
            },
            "progress": {
                "completed_topics": [],
                "completed_tasks": [],
                "current_state": ""
            }
        }

    def mount_drive(self):
        if not self.drive_mounted:
            drive.mount('/content/drive')
            self.drive_mounted = True

    def set_file_path(self, folder_path="/content/drive/My Drive/AI_Teacher/"):
        self.folder_path = folder_path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        self.full_path = os.path.join(folder_path, self.data_file)

    def save_data(self):
        try:
            with open(self.full_path, "w") as f:
                json.dump(self.data, f, indent=4)
            print(f"Данные успешно сохранены в {self.full_path}")
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")

    def load_data(self):
        try:
            if os.path.exists(self.full_path):
                with open(self.full_path, "r") as f:
                    self.data = json.load(f)
                print("Данные успешно загружены.")
            else:
                print("Файл данных не найден, создается новый файл.")
                self.save_data()
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

    def update_student_info(self, name, gender, preferred_address):
        self.data["student"] = {
            "name": name,
            "gender": gender,
            "preferred_address": preferred_address
        }
        self.save_data()

    def update_progress(self, completed_topic=None, completed_task=None, current_state=None):
        if completed_topic:
            self.data["progress"]["completed_topics"].append(completed_topic)
        if completed_task:
            self.data["progress"]["completed_tasks"].append(completed_task)
        if current_state:
            self.data["progress"]["current_state"] = current_state
        self.save_data()

# Пример использования
manager = DataManager()
manager.mount_drive()
manager.set_file_path()
manager.load_data()

# Обновление информации об обучающемся
manager.update_student_info(name="Иван Иванов", gender="мужской", preferred_address="вы")

# Обновление прогресса
manager.update_progress(completed_topic="Введение в машинное обучение", current_state="Изучает линейную регрессию")
