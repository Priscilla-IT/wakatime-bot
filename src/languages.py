import json
import os


def load_languages(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def load_excluded_lang(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


current_dir = os.path.dirname(os.path.abspath(__file__))


languages_path = os.path.join(current_dir, "..", "languages.json")
excluded_languages_path = os.path.join(current_dir, "..", "excluded_lang.json")


LANGUAGES = load_languages(languages_path)
EXCLUDED_LANGUAGES = load_excluded_lang(excluded_languages_path)
