# TODO:
# Реализуем память для AI, см. README.md

import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class LearnlyMemory:
    def __init__(self, storage_type="local", file_path="learnly_memory.json", google_drive_folder_id=None):
        """
        Инициализация системы памяти.

        :param storage_type: Тип хранилища ("local" или "google_drive").
        :param file_path: Путь к локальному файлу (для режима "local").
        :param google_drive_folder_id: ID папки на Google Drive (для режима "google_drive").
        """
        self.storage_type = storage_type
        self.file_path = file_path
        self.google_drive_folder_id = google_drive_folder_id
        self.data = {
            "progress": {},  # Прогресс обучения
            "errors": [],    # Список ошибок
            "context": {}    # Контекст уроков
        }

        # Загружаем данные при инициализации
        self.load()

    def save(self):
        """Сохраняет данные в выбранное хранилище."""
        if self.storage_type == "local":
            self._save_to_local()
        elif self.storage_type == "google_drive":
            self._save_to_google_drive()
        else:
            raise ValueError("Неподдерживаемый тип хранилища.")

    def load(self):
        """Загружает данные из выбранного хранилища."""
        if self.storage_type == "local":
            self._load_from_local()
        elif self.storage_type == "google_drive":
            self._load_from_google_drive()
        else:
            raise ValueError("Неподдерживаемый тип хранилища.")

    def _save_to_local(self):
        """Сохраняет данные в локальный файл."""
        with open(self.file_path, "w") as file:
            json.dump(self.data, file, indent=4)

    def _load_from_local(self):
        """Загружает данные из локального файла."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.data = json.load(file)

    def _save_to_google_drive(self):
        """Сохраняет данные на Google Drive."""
        creds = self._get_google_drive_credentials()
        service = build("drive", "v3", credentials=creds)

        # Сохраняем данные в локальный файл перед загрузкой на Google Drive
        self._save_to_local()

        # Загружаем файл на Google Drive
        file_metadata = {
            "name": os.path.basename(self.file_path),
            "parents": [self.google_drive_folder_id] if self.google_drive_folder_id else None
        }
        media = MediaFileUpload(self.file_path, mimetype="application/json")
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"Файл сохранен на Google Drive с ID: {file.get('id')}")

    def _load_from_google_drive(self):
        """Загружает данные с Google Drive."""
        creds = self._get_google_drive_credentials()
        service = build("drive", "v3", credentials=creds)

        # Ищем файл на Google Drive
        query = f"name='{os.path.basename(self.file_path)}'"
        if self.google_drive_folder_id:
            query += f" and '{self.google_drive_folder_id}' in parents"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])

        if not files:
            print("Файл не найден на Google Drive.")
            return

        # Скачиваем файл
        file_id = files[0]["id"]
        request = service.files().get_media(fileId=file_id)
        with open(self.file_path, "wb") as file:
            file.write(request.execute())

        # Загружаем данные из локального файла
        self._load_from_local()

    def _get_google_drive_credentials(self):
        """Получает учетные данные для доступа к Google Drive."""
        SCOPES = ["https://www.googleapis.com/auth/drive.file"]
        creds = None

        # Проверяем наличие сохраненных учетных данных
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # Если нет действительных учетных данных, запрашиваем их у пользователя
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            # Сохраняем учетные данные для будущего использования
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds

    def update_progress(self, task_id: int, status: str):
        """Обновляет прогресс выполнения задания."""
        self.data["progress"][task_id] = status
        self.save()

    def add_error(self, error: str):
        """Добавляет ошибку в список ошибок."""
        self.data["errors"].append(error)
        self.save()

    def update_context(self, key: str, value: str):
        """Обновляет контекст урока."""
        self.data["context"][key] = value
        self.save()

    def get_progress(self):
        """Возвращает прогресс обучения."""
        return self.data["progress"]

    def get_errors(self):
        """Возвращает список ошибок."""
        return self.data["errors"]

    def get_context(self):
        """Возвращает контекст уроков."""
        return self.data["context"]
    