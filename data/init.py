import json
import os

def load_json_data(filename):
    """Загружает данные из JSON файла"""
    try:
        # Получаем абсолютный путь к файлу
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки {filename}: {e}")
        return {}

# Загружаем данные при импорте модуля
verbs = load_json_data('verbs.json')
words = load_json_data('words.json') 
phrases = load_json_data('phrases.json')
grammar = load_json_data('grammar.json')
