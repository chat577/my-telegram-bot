import json
import os

def load_data(filename):
    """Загружает данные из JSON файла"""
    try:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}

# Загружаем все данные
verbs = load_data('verbs.json')
words = load_data('words.json')
phrases = load_data('phrases.json')
grammar = load_data('grammar.json')
