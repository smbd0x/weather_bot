import json
from pathlib import Path

from logger import service_logger


class MessageService:
    def __init__(self, texts_dir: str = "bot/texts"):
        self.texts_dir = Path(texts_dir)
        self._cache = {}

    def get(self, file_name: str, key: str) -> str:
        service_logger.info(f'Получение текста сообщения', extra={'file_name': file_name, 'key': key})

        if file_name not in self._cache:
            path = f'{self.texts_dir}/{file_name}'
            with open(path, encoding="utf-8") as f:
                self._cache[file_name] = json.load(f)
        return self._cache[file_name].get(key, f"<Missing text {key}>")
