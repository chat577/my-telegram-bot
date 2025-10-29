import os
import json

def load_data_files():
    """Загружает данные из JSON файлов"""
    data = {
        'verbs': {},
        'words': {}, 
        'phrases': {},
        'grammar': {}
    }
    
    files = {
        'verbs': 'data/verbs.json',
        'words': 'data/words.json',
        'phrases': 'data/phrases.json', 
        'grammar': 'data/grammar.json'
    }
    
    for data_type, filename in files.items():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data[data_type] = json.load(f)
            print(f"✅ Загружен {filename}")
        except Exception as e:
            print(f"❌ Ошибка загрузки {filename}: {e}")
    
    return data['verbs'], data['words'], data['phrases'], data['grammar']

# Загружаем данные
verbs, words, phrases, grammar = load_data_files()
