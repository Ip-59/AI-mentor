import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class LearnlyMemory:
    def __init__(self, storage_type="local", file_path="learnly_memory.json", google_drive_folder_id=None):
        """Инициализация памяти."""
        self.storage_type = storage_type
        self.file_path = file_path
        self.google_drive_folder_id = google_drive_folder_id
        self.data = {
            "progress": {},
            "errors": [],
            "context": {}
        }
        self.load()  # Загружаем данные при инициализации

    def save(self):
        """Сохранение данных."""
        try:
            if self.storage_type == "local":
                self._save_to_local()
            elif self.storage_type == "google_drive":
                self._save_to_google_drive()
            else:
                raise ValueError("Неподдерживаемый тип хранилища.")
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")

    def load(self):
        """Загрузка данных."""
        try:
            if self.storage_type == "local":
                self._load_from_local()
            elif self.storage_type == "google_drive":
                self._load_from_google_drive()
            else:
                raise ValueError("Неподдерживаемый тип хранилища.")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

    def _save_to_local(self):
        """Сохранение в локальный файл с обработкой ошибок."""
        try:
            with open(self.file_path, "w") as file:
                json.dump(self.data, file, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении в файл: {e}")

    def _load_from_local(self):
        """Загрузка из локального файла с проверкой наличия."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as file:
                    self.data = json.load(file)
            except json.JSONDecodeError:
                print("Ошибка: Файл повреждён, загружаем пустые данные.")
                self.data = {"progress": {}, "errors": [], "context": {}}

    def _save_to_google_drive(self):
        """Сохранение на Google Drive."""
        creds = self._get_google_drive_credentials()
        service = build("drive", "v3", credentials=creds)

        self._save_to_local()  # Локальное сохранение перед загрузкой

        file_metadata = {
            "name": os.path.basename(self.file_path),
            "parents": [self.google_drive_folder_id] if self.google_drive_folder_id else None
        }
        media = MediaFileUpload(self.file_path, mimetype="application/json")
        file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()
        print(f"Файл сохранен на Google Drive с ID: {file.get('id')}")

    def _load_from_google_drive(self):
        """Загрузка с Google Drive."""
        creds = self._get_google_drive_credentials()
        service = build("drive", "v3", credentials=creds)

        query = f"name='{os.path.basename(self.file_path)}'"
        if self.google_drive_folder_id:
            query += f" and '{self.google_drive_folder_id}' in parents"
        
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get("files", [])

        if not files:
            print("Файл не найден на Google Drive.")
            return

        file_id = files[0]["id"]
        request = service.files().get_media(fileId=file_id)
        with open(self.file_path, "wb") as file:
            file.write(request.execute())

        self._load_from_local()  # Обновить локальные данные

    def _get_google_drive_credentials(self):
        """Получение токена доступа к Google Drive."""
        SCOPES = ["https://www.googleapis.com/auth/drive.file"]
        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists("credentials.json"):
                    raise FileNotFoundError("Файл credentials.json не найден!")
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return creds
