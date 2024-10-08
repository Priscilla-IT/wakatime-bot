import json
import os
from typing import Any


def load_json_file(filename: str) -> Any:
    """Загружает данные из JSON-файла и возвращает их."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Ошибка: файл '{filename}' не найден.")
    except json.JSONDecodeError:
        print(
            f"❌ Ошибка: не удалось декодировать JSON из файла '{filename}'."
        )
    return None


def get_languages_and_excluded_languages() -> tuple:
    """Получает языки и исключенные языки из файлов."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    languages_path = os.path.join(current_dir, "..", "languages.json")
    excluded_languages_path = os.path.join(
        current_dir, "..", "excluded_lang.json"
    )

    languages = load_json_file(languages_path)
    excluded_languages = load_json_file(excluded_languages_path)

    return languages, excluded_languages


# Загружаем языки и исключенные языки
LANGUAGES, EXCLUDED_LANGUAGES = get_languages_and_excluded_languages()
