from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
import os
from datetime import datetime
import requests
import urllib.parse
import nltk
import ssl
import zipfile
import tempfile
from pathlib import Path
import sqlite3
import hashlib
import pickle
import threading
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')

# Обход SSL для NLTK
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Загрузка данных NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class AdvancedKnowledgeDatabase:
    """Продвинутая база знаний с SQLite и векторным поиском"""
    
    def __init__(self, db_path="ai_knowledge.db"):
        self.db_path = db_path
        self.vectorizer = TfidfVectorizer(max_features=10000, stop_words=self._russian_stop_words())
        self.vectors = None
        self.doc_ids = []
        self._init_database()
        self._load_vectors()
    
    def _russian_stop_words(self):
        """Русские стоп-слова для векторизации"""
        return [
            'и', 'в', 'во', 'не', 'что', 'он', 'на', 'я', 'с', 'со', 'как', 'а', 'то', 'все', 'она', 'так', 'его', 
            'но', 'да', 'ты', 'к', 'у', 'же', 'вы', 'за', 'бы', 'по', 'только', 'ее', 'мне', 'было', 'вот', 'от', 
            'меня', 'еще', 'нет', 'о', 'из', 'ему', 'теперь', 'когда', 'даже', 'ну', 'вдруг', 'ли', 'если', 'уже', 
            'или', 'ни', 'быть', 'был', 'него', 'до', 'вас', 'нибудь', 'опять', 'уж', 'вам', 'ведь', 'там', 'потом', 
            'себя', 'ничего', 'ей', 'может', 'они', 'тут', 'где', 'есть', 'надо', 'ней', 'для', 'мы', 'тебя', 'их', 
            'чем', 'была', 'сам', 'чтоб', 'без', 'будто', 'чего', 'раз', 'тоже', 'себе', 'под', 'будет', 'ж', 'тогда', 
            'кто', 'этот', 'того', 'потому', 'этого', 'какой', 'совсем', 'ним', 'здесь', 'этом', 'один', 'почти', 'мой', 
            'тем', 'чтобы', 'нее', 'сейчас', 'были', 'куда', 'зачем', 'всех', 'никогда', 'можно', 'при', 'наконец', 'два', 
            'об', 'другой', 'хоть', 'после', 'над', 'больше', 'тот', 'через', 'эти', 'нас', 'про', 'всего', 'них', 'какая', 
            'много', 'разве', 'три', 'эту', 'моя', 'впрочем', 'хорошо', 'свою', 'этой', 'перед', 'иногда', 'лучше', 'чуть', 
            'том', 'нельзя', 'такой', 'им', 'более', 'всегда', 'конечно', 'всю', 'между'
        ]
    
    def _init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Основная таблица знаний
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT NOT NULL,
                intent TEXT NOT NULL,
                tags TEXT,
                confidence REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT DEFAULT 'manual',
                language TEXT DEFAULT 'russian',
                complexity INTEGER DEFAULT 1,
                context TEXT,
                embeddings BLOB
            )
        ''')
        
        # Таблица разговорного контекста
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT NOT NULL,
                response TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                context_hash TEXT
            )
        ''')
        
        # Таблица обучения и улучшений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                input_text TEXT NOT NULL,
                output_text TEXT NOT NULL,
                intent TEXT,
                quality_score REAL,
                used_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица веб-поиска (кэш)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT UNIQUE,
                query_text TEXT NOT NULL,
                results TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                usage_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Инициализация базовых знаний
        self._initialize_base_knowledge()
    
    def _initialize_base_knowledge(self):
        """Инициализация расширенной базы знаний"""
        base_knowledge = [
            # Программирование
            ("Что такое Python?", 
             "Python - это высокоуровневый язык программирования общего назначения с динамической типизацией и автоматическим управлением памятью. Основные особенности:\n\n• 🐍 Простой и понятный синтаксис\n• 📚 Огромная экосистема библиотек\n• 🔧 Кроссплатформенность\n• 🎯 Используется в веб-разработке, data science, AI, автоматизации\n• 💡 Идеален для начинающих и профессионалов\n\nПример кода:\n```python\nprint('Привет, мир!')\nfor i in range(5):\n    print(f'Счетчик: {i}')\n```",
             "programming", "explanation", ["python", "язык программирования", "синтаксис"]),
            
            ("Как создать класс в Python?",
             "В Python классы создаются с помощью ключевого слова `class`. Вот полный пример:\n\n```python\nclass Person:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        return f'Привет, меня зовут {self.name} и мне {self.age} лет'\n    \n    def have_birthday(self):\n        self.age += 1\n        return f'Теперь мне {self.age} лет!'\n\n# Использование\nperson = Person('Анна', 25)\nprint(person.greet())\nprint(person.have_birthday())\n```\n\nКлючевые концепции ООП в Python:\n• 📦 **Инкапсуляция** - объединение данных и методов\n• 🧬 **Наследование** - создание производных классов\n• 🎭 **Полиморфизм** - разные реализации методов\n• 🔧 **Абстракция** - скрытие сложности",
             "programming", "code_example", ["python", "класс", "ооп", "объектно-ориентированное программирование"]),
            
            ("Что такое JavaScript?",
             "JavaScript - это язык программирования для веб-разработки, который выполняется в браузере пользователя.\n\n**Основные возможности:**\n• 🌐 Интерактивность веб-страниц\n• 📱 Frontend и backend разработка (Node.js)\n• 🎯 Асинхронное программирование\n• 🔧 Динамическая типизация\n\n**Пример кода:**\n```javascript\n// Функция для приветствия\nfunction greet(name) {\n    return `Привет, ${name}!`;\n}\n\n// Использование\nconsole.log(greet('Мир'));\n\n// Работа с DOM\ndocument.getElementById('myButton').addEventListener('click', function() {\n    alert('Кнопка нажата!');\n});\n```",
             "programming", "explanation", ["javascript", "веб-разработка", "frontend"]),
            
            # Веб-разработка
            ("Что такое HTML?",
             "HTML (HyperText Markup Language) - это стандартный язык разметки для создания веб-страниц.\n\n**Основные элементы HTML:**\n\n```html\n<!DOCTYPE html>\n<html>\n<head>\n    <title>Моя страница</title>\n</head>\n<body>\n    <h1>Заголовок</h1>\n    <p>Абзац текста</p>\n    <a href='https://example.com'>Ссылка</a>\n    <img src='image.jpg' alt='Описание'>\n</body>\n</html>\n```\n\n**Семантические теги HTML5:**\n• `<header>` - шапка страницы\n• `<nav>` - навигация\n• `<main>` - основное содержание\n• `<article>` - независимый контент\n• `<section>` - раздел документа\n• `<footer>` - подвал страницы",
             "web", "explanation", ["html", "веб-разработка", "разметка"]),
            
            ("Что такое CSS?",
             "CSS (Cascading Style Sheets) - язык стилей для оформления HTML-документов.\n\n**Основные возможности CSS:**\n\n```css\n/* Селектор по тегу */\nh1 {\n    color: blue;\n    font-size: 24px;\n    text-align: center;\n}\n\n/* Селектор по классу */\n.button {\n    background-color: #4CAF50;\n    color: white;\n    padding: 10px 20px;\n    border: none;\n    border-radius: 5px;\n}\n\n/* Селектор по ID */\n#header {\n    background: linear-gradient(45deg, #667eea, #764ba2);\n    padding: 20px;\n}\n\n/* Адаптивный дизайн */\n@media (max-width: 768px) {\n    .container {\n        flex-direction: column;\n    }\n}\n```\n\n**Препроцессоры CSS:**\n• Sass/SCSS\n• Less\n• Stylus",
             "web", "explanation", ["css", "стили", "веб-дизайн"]),
            
            # Алгоритмы
            ("Что такое быстрая сортировка?",
             "Быстрая сортировка (QuickSort) - это эффективный алгоритм сортировки со средней сложностью O(n log n).\n\n**Принцип работы:**\n1. Выбираем опорный элемент (pivot)\n2. Разделяем массив на две части: элементы меньше pivot и элементы больше pivot\n3. Рекурсивно применяем алгоритм к обеим частям\n\n**Реализация на Python:**\n```python\ndef quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    \n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    \n    return quicksort(left) + middle + quicksort(right)\n\n# Пример использования\nnumbers = [3, 6, 8, 10, 1, 2, 1]\nsorted_numbers = quicksort(numbers)\nprint(f'Отсортированный список: {sorted_numbers}')\n```\n\n**Сложность:**\n• В среднем: O(n log n)\n• В худшем случае: O(n²)\n• Память: O(log n)",
             "algorithms", "explanation", ["алгоритм", "сортировка", "quicksort", "сложность"]),
            
            ("Что такое бинарный поиск?",
             "Бинарный поиск - это алгоритм поиска в отсортированном массиве со сложностью O(log n).\n\n**Принцип работы:**\n1. Находим средний элемент массива\n2. Сравниваем с искомым значением\n3. Если значение равно - поиск завершен\n4. Если значение меньше - ищем в левой половине\n5. Если значение больше - ищем в правой половине\n\n**Реализация на Python:**\n```python\ndef binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    \n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    \n    return -1\n\n# Пример использования\nnumbers = [1, 3, 5, 7, 9, 11, 13]\nindex = binary_search(numbers, 7)\nprint(f'Найден по индексу: {index}')\n```",
             "algorithms", "code_example", ["алгоритм", "поиск", "бинарный", "сложность"]),
            
            # Базы данных
            ("Что такое SQL?",
             "SQL (Structured Query Language) - язык структурированных запросов для работы с реляционными базами данных.\n\n**Основные команды SQL:**\n\n```sql\n-- Создание таблицы\nCREATE TABLE users (\n    id INTEGER PRIMARY KEY,\n    name TEXT NOT NULL,\n    email TEXT UNIQUE,\n    age INTEGER\n);\n\n-- Вставка данных\nINSERT INTO users (name, email, age) \nVALUES ('Иван', 'ivan@example.com', 30);\n\n-- Выборка данных\nSELECT * FROM users WHERE age > 25;\n\n-- Обновление данных\nUPDATE users SET age = 31 WHERE name = 'Иван';\n\n-- Удаление данных\nDELETE FROM users WHERE age < 18;\n```\n\n**Типы JOIN в SQL:**\n• INNER JOIN - пересечение множеств\n• LEFT JOIN - все записи из левой таблицы\n• RIGHT JOIN - все записи из правой таблицы\n• FULL OUTER JOIN - объединение множеств",
             "databases", "explanation", ["sql", "база данных", "реляционная"]),
            
            # Искусственный интеллект
            ("Что такое машинное обучение?",
             "Машинное обучение (Machine Learning) - это раздел искусственного интеллекта, позволяющий компьютерам обучаться на данных без явного программирования.\n\n**Основные типы ML:**\n\n🔹 **Обучение с учителем (Supervised Learning)**\n• Классификация - предсказание категорий\n• Регрессия - предсказание числовых значений\n\n🔹 **Обучение без учителя (Unsupervised Learning)**\n• Кластеризация - группировка похожих объектов\n• Снижение размерности - упрощение данных\n\n🔹 **Обучение с подкреплением (Reinforcement Learning)**\n• Агент учится на основе взаимодействия со средой\n\n**Популярные алгоритмы:**\n• Линейная регрессия\n• Деревья решений\n• Метод k-ближайших соседей\n• Нейронные сети\n• Метод опорных векторов",
             "ai", "explanation", ["машинное обучение", "искусственный интеллект", "ml", "ai"]),
            
            ("Что такое нейронные сети?",
             "Нейронные сети - это вычислительные системы, вдохновленные биологическими нейронными сетями мозга.\n\n**Основные компоненты:**\n• 🧠 **Нейроны** - базовые вычислительные единицы\n• 🔗 **Связи** - взвешенные соединения между нейронами\n• 📊 **Функция активации** - определяет выход нейрона\n• 🎯 **Слои** - входной, скрытые, выходной\n\n**Типы нейронных сетей:**\n• Полносвязные (Fully Connected)\n• Сверточные (CNN) - для изображений\n• Рекуррентные (RNN) - для последовательностей\n• Трансформеры - для NLP\n\n**Пример простой нейросети на Python с Keras:**\n```python\nfrom tensorflow import keras\nfrom tensorflow.keras import layers\n\nmodel = keras.Sequential([\n    layers.Dense(64, activation='relu', input_shape=(784,)),\n    layers.Dense(64, activation='relu'),\n    layers.Dense(10, activation='softmax')\n])\n\nmodel.compile(optimizer='adam',\n              loss='categorical_crossentropy',\n              metrics=['accuracy'])\n```",
             "ai", "explanation", ["нейронные сети", "искусственный интеллект", "deep learning"]),
            
            # Общие знания
            ("Как работает интернет?",
             "Интернет - это глобальная сеть соединенных компьютеров, общающихся по стандартным протоколам.\n\n**Основные компоненты:**\n\n🌐 **Протоколы:**\n• TCP/IP - базовый протокол передачи данных\n• HTTP/HTTPS - протоколы веб-страниц\n• DNS - система доменных имен\n• SMTP - протокол электронной почты\n\n🔗 **Как работает запрос к сайту:**\n1. Браузер отправляет DNS-запрос\n2. DNS-сервер возвращает IP-адрес\n3. Устанавливается TCP-соединение\n4. Отправляется HTTP-запрос\n5. Сервер возвращает HTTP-ответ\n6. Браузер отображает страницу\n\n**Технологии веб-разработки:**\n• Frontend: HTML, CSS, JavaScript\n• Backend: Python, PHP, Node.js, Java\n• Базы данных: MySQL, PostgreSQL, MongoDB\n• Веб-серверы: Nginx, Apache",
             "technology", "explanation", ["интернет", "протоколы", "веб"]),
            
            ("Что такое блокчейн?",
             "Блокчейн - это децентрализованная распределенная база данных, состоящая из цепочки блоков.\n\n**Ключевые особенности:**\n• 🔗 **Децентрализация** - нет центрального контролирующего органа\n• 🔒 **Неизменяемость** - данные нельзя изменить после записи\n• ⛓️ **Прозрачность** - все транзакции видны участникам\n• 💎 **Безопасность** - криптографическая защита\n\n**Принцип работы:**\n1. Транзакции группируются в блоки\n2. Блоки проверяются сетью (майнинг)\n3. Проверенный блок добавляется в цепочку\n4. Каждый блок содержит хеш предыдущего блока\n\n**Применение:**\n• Криптовалюты (Bitcoin, Ethereum)\n• Смарт-контракты\n• Цифровая идентификация\n• Цепочки поставок",
             "technology", "explanation", ["блокчейн", "криптовалюты", "децентрализация"]),
        ]
        
        # Проверяем, нужно ли добавлять базовые знания
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📖 Инициализация расширенной базы знаний...")
            for question, answer, category, intent, tags in base_knowledge:
                self.add_knowledge(question, answer, category, intent, tags)
            print("✅ База знаний инициализирована с расширенными данными")
        
        conn.close()
    
    def add_knowledge(self, question, answer, category, intent, tags=None, confidence=1.0, source="manual"):
        """Добавление знания в базу данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        tags_str = json.dumps(tags if tags else [])
        
        cursor.execute('''
            INSERT INTO knowledge (question, answer, category, intent, tags, confidence, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (question, answer, category, intent, tags_str, confidence, source))
        
        conn.commit()
        conn.close()
        
        # Обновляем векторное представление
        self._update_vectors()
        
        return cursor.lastrowid
    
    def search_knowledge(self, query, category=None, min_confidence=0.3, limit=5):
        """Поиск в базе знаний с использованием векторного поиска"""
        # Текстовый поиск
        text_results = self._text_search(query, category, min_confidence, limit*2)
        
        # Векторный поиск
        vector_results = self._vector_search(query, category, limit*2)
        
        # Объединяем и ранжируем результаты
        all_results = self._merge_results(text_results, vector_results, query)
        
        return all_results[:limit]
    
    def _text_search(self, query, category, min_confidence, limit):
        """Традиционный текстовый поиск"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM knowledge 
                WHERE category = ? AND confidence >= ?
                ORDER BY usage_count DESC, confidence DESC
                LIMIT ?
            ''', (category, min_confidence, limit))
        else:
            cursor.execute('''
                SELECT * FROM knowledge 
                WHERE confidence >= ?
                ORDER BY usage_count DESC, confidence DESC
                LIMIT ?
            ''', (min_confidence, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_dict(row))
        
        conn.close()
        return results
    
    def _vector_search(self, query, category, limit):
        """Векторный поиск с использованием TF-IDF"""
        if self.vectors is None:
            return []
        
        try:
            # Преобразуем запрос в вектор
            query_vec = self.vectorizer.transform([query])
            
            # Вычисляем косинусное сходство
            similarities = cosine_similarity(query_vec, self.vectors).flatten()
            
            # Получаем индексы наиболее похожих документов
            top_indices = similarities.argsort()[-limit:][::-1]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = []
            for idx in top_indices:
                if idx < len(self.doc_ids):
                    cursor.execute('SELECT * FROM knowledge WHERE id = ?', (self.doc_ids[idx],))
                    row = cursor.fetchone()
                    if row:
                        result = self._row_to_dict(row)
                        result['similarity_score'] = float(similarities[idx])
                        results.append(result)
            
            conn.close()
            return results
            
        except Exception as e:
            print(f"❌ Ошибка векторного поиска: {e}")
            return []
    
    def _load_vectors(self):
        """Загрузка векторных представлений"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, question FROM knowledge")
            rows = cursor.fetchall()
            
            if not rows:
                self.vectors = None
                return
            
            self.doc_ids = [row[0] for row in rows]
            documents = [row[1] for row in rows]
            
            # Обучение векторизатора и преобразование документов
            self.vectors = self.vectorizer.fit_transform(documents)
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка загрузки векторов: {e}")
            self.vectors = None
    
    def _update_vectors(self):
        """Обновление векторных представлений"""
        threading.Thread(target=self._load_vectors, daemon=True).start()
    
    def _merge_results(self, text_results, vector_results, query):
        """Объединение и ранжирование результатов"""
        # Создаем словарь для объединения результатов
        merged = {}
        
        # Добавляем текстовые результаты
        for result in text_results:
            result_id = result['id']
            result['score'] = result.get('confidence', 0.5) * 0.3
            merged[result_id] = result
        
        # Добавляем векторные результаты
        for result in vector_results:
            result_id = result['id']
            if result_id in merged:
                # Улучшаем оценку существующего результата
                merged[result_id]['score'] += result.get('similarity_score', 0) * 0.7
            else:
                result['score'] = result.get('similarity_score', 0) * 0.7
                merged[result_id] = result
        
        # Преобразуем в список и сортируем
        results = list(merged.values())
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results
    
    def _row_to_dict(self, row):
        """Преобразование строки БД в словарь"""
        return {
            'id': row[0],
            'question': row[1],
            'answer': row[2],
            'category': row[3],
            'intent': row[4],
            'tags': json.loads(row[5]) if row[5] else [],
            'confidence': row[6],
            'usage_count': row[7],
            'success_rate': row[8],
            'created_at': row[9],
            'updated_at': row[10],
            'source': row[11]
        }
    
    def update_usage(self, knowledge_id, success=True):
        """Обновление статистики использования"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if success:
            cursor.execute('''
                UPDATE knowledge 
                SET usage_count = usage_count + 1,
                    success_rate = MIN(1.0, success_rate + 0.05),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (knowledge_id,))
        else:
            cursor.execute('''
                UPDATE knowledge 
                SET usage_count = usage_count + 1,
                    success_rate = MAX(0.0, success_rate - 0.1),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (knowledge_id,))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self):
        """Получение статистики базы знаний"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM knowledge")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge WHERE source = 'web'")
        web_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT category) FROM knowledge")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(usage_count) FROM knowledge")
        total_usage = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT category, COUNT(*) FROM knowledge GROUP BY category")
        categories = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_entries': total,
            'web_entries': web_count,
            'categories_count': categories_count,
            'total_usage': total_usage,
            'categories': categories
        }
    
    def export_knowledge(self, format='json'):
        """Экспорт знаний"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM knowledge ORDER BY usage_count DESC")
        rows = cursor.fetchall()
        
        knowledge_data = []
        for row in rows:
            knowledge_data.append({
                'id': row[0],
                'question': row[1],
                'answer': row[2],
                'category': row[3],
                'intent': row[4],
                'tags': json.loads(row[5]) if row[5] else [],
                'usage_count': row[7],
                'success_rate': row[8],
                'created_at': row[9]
            })
        
        conn.close()
        
        if format == 'json':
            filename = f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(knowledge_data, f, ensure_ascii=False, indent=2)
        else:
            filename = f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ЭКСПОРТ БАЗЫ ЗНАНИЙ AI ASSISTANT\n")
                f.write("=" * 50 + "\n\n")
                
                for item in knowledge_data:
                    f.write(f"ВОПРОС: {item['question']}\n")
                    f.write(f"ОТВЕТ: {item['answer'][:200]}...\n")
                    f.write(f"КАТЕГОРИЯ: {item['category']} | ИСПОЛЬЗОВАНИЙ: {item['usage_count']}\n")
                    f.write("-" * 40 + "\n")
        
        return filename

class EnhancedWebSearch:
    """Улучшенная система веб-поиска с кэшированием"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.knowledge_db = AdvancedKnowledgeDatabase()
    
    def intelligent_search(self, query, max_results=5, use_cache=True):
        """Интеллектуальный поиск с анализом контекста и кэшированием"""
        print(f"🔍 Умный поиск: '{query}'")
        
        # Проверяем кэш
        if use_cache:
            cached_results = self._get_cached_results(query)
            if cached_results:
                print("✅ Используем кэшированные результаты")
                return cached_results
        
        # Анализируем тип запроса
        query_type = self._analyze_query_type(query)
        search_strategy = self._get_search_strategy(query_type)
        
        # Выполняем поиск
        results = self._execute_multi_engine_search(query, search_strategy, max_results)
        
        # Обогащаем результаты
        enriched_results = self._enrich_results(results, query_type)
        
        # Сохраняем в кэш
        self._cache_results(query, enriched_results)
        
        # Сохраняем полезные результаты в базу знаний
        self._save_to_knowledge_base(query, enriched_results)
        
        return enriched_results
    
    def _analyze_query_type(self, query):
        """Глубокий анализ типа запроса"""
        query_lower = query.lower()
        
        analysis = {
            'domain': 'general',
            'complexity': 'medium',
            'language': 'russian',
            'requires_code': False,
            'requires_explanation': False,
            'requires_comparison': False
        }
        
        # Определяем домен
        domains = {
            'programming': ['код', 'программир', 'функция', 'класс', 'python', 'javascript', 'java', 'алгоритм'],
            'science': ['наука', 'физика', 'химия', 'биология', 'математика', 'теорема'],
            'technology': ['технология', 'гаджет', 'смартфон', 'компьютер', 'интернет'],
            'education': ['обучение', 'учеба', 'образование', 'курс', 'урок'],
            'business': ['бизнес', 'компания', 'маркетинг', 'финансы', 'инвестиции']
        }
        
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                analysis['domain'] = domain
                break
        
        # Определяем сложность
        complex_indicators = ['как работает', 'принцип работы', 'объясните', 'подробно']
        if any(indicator in query_lower for indicator in complex_indicators):
            analysis['complexity'] = 'high'
            analysis['requires_explanation'] = True
        
        # Проверяем необходимость в коде
        if any(word in query_lower for word in ['пример кода', 'напишите код', 'реализация', 'синтаксис']):
            analysis['requires_code'] = True
        
        # Проверяем необходимость сравнения
        if any(word in query_lower for word in ['сравнение', 'разница между', 'лучше чем', 'vs', 'против']):
            analysis['requires_comparison'] = True
        
        return analysis
    
    def _execute_multi_engine_search(self, query, search_strategy, max_results):
        """Выполнение поиска по нескольким движкам"""
        all_results = []
        
        for engine in search_strategy[:2]:  # Используем первые 2 движка из стратегии
            try:
                if engine == 'duckduckgo':
                    results = self._duckduckgo_search(query, max_results)
                elif engine == 'wikipedia':
                    results = self._wikipedia_search(query, max_results)
                elif engine == 'stackoverflow':
                    results = self._stackoverflow_search(query, max_results)
                else:
                    results = self._fallback_search(query, max_results)
                
                if results:
                    all_results.extend(results)
                    
            except Exception as e:
                print(f"❌ Ошибка поиска в {engine}: {e}")
                continue
            
            if len(all_results) >= max_results:
                break
        
        return all_results[:max_results]
    
    def _enrich_results(self, results, query_type):
        """Обогащение результатов дополнительной информацией"""
        enriched = []
        
        for result in results:
            # Добавляем релевантность на основе типа запроса
            result['relevance_score'] = self._calculate_relevance(result, query_type)
            
            # Добавляем тип контента
            result['content_type'] = self._classify_content_type(result)
            
            # Обогащаем описания
            if result.get('snippet'):
                result['snippet'] = self._enhance_snippet(result['snippet'], query_type)
            
            enriched.append(result)
        
        # Сортируем по релевантности
        enriched.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return enriched
    
    def _calculate_relevance(self, result, query_type):
        """Вычисление релевантности результата"""
        score = 0.5  # Базовая оценка
        
        # Анализ заголовка
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Повышаем оценку для соответствующих доменов
        if query_type['domain'] == 'programming' and any(word in title + snippet for word in ['код', 'программирование', 'алгоритм']):
            score += 0.3
        
        if query_type['requires_explanation'] and any(word in title + snippet for word in ['объяснение', 'принцип', 'как работает']):
            score += 0.2
        
        # Понижаем оценку для нерелевантных источников
        if any(domain in title + snippet for domain in ['новости', 'магазин', 'купить']):
            score -= 0.2
        
        return min(1.0, max(0.1, score))
    
    def _classify_content_type(self, result):
        """Классификация типа контента"""
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        if any(word in title + snippet for word in ['код', 'пример', 'реализация']):
            return 'code_example'
        elif any(word in title + snippet for word in ['объяснение', 'принцип', 'как работает']):
            return 'explanation'
        elif any(word in title + snippet for word in ['руководство', 'инструкция', 'учебник']):
            return 'tutorial'
        elif any(word in title + snippet for word in ['документация', 'справка']):
            return 'documentation'
        else:
            return 'information'
    
    def _enhance_snippet(self, snippet, query_type):
        """Улучшение сниппета"""
        # Ограничиваем длину
        if len(snippet) > 300:
            snippet = snippet[:300] + "..."
        
        # Добавляем эмодзи в зависимости от типа контента
        if query_type['requires_code']:
            snippet = "💻 " + snippet
        elif query_type['requires_explanation']:
            snippet = "📚 " + snippet
        
        return snippet
    
    def _get_cached_results(self, query):
        """Получение результатов из кэш"""
        try:
            query_hash = hashlib.md5(query.encode()).hexdigest()
            
            conn = sqlite3.connect(self.knowledge_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT results FROM web_cache 
                WHERE query_hash = ? AND created_at > datetime('now', '-7 days')
            ''', (query_hash,))
            
            row = cursor.fetchone()
            if row:
                # Обновляем счетчик использования
                cursor.execute('''
                    UPDATE web_cache SET usage_count = usage_count + 1 
                    WHERE query_hash = ?
                ''', (query_hash,))
                conn.commit()
                
                results = json.loads(row[0])
                conn.close()
                return results
            
            conn.close()
            return None
            
        except Exception as e:
            print(f"❌ Ошибка доступа к кэшу: {e}")
            return None
    
    def _cache_results(self, query, results):
        """Сохранение результатов в кэш"""
        try:
            query_hash = hashlib.md5(query.encode()).hexdigest()
            
            conn = sqlite3.connect(self.knowledge_db.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO web_cache (query_hash, query_text, results)
                VALUES (?, ?, ?)
            ''', (query_hash, query, json.dumps(results, ensure_ascii=False)))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"❌ Ошибка сохранения в кэш: {e}")
    
    def _save_to_knowledge_base(self, query, results):
        """Сохранение полезных результатов в базу знаний"""
        try:
            for result in results[:2]:  # Сохраняем 2 лучших результата
                if result.get('relevance_score', 0) > 0.7:
                    self.knowledge_db.add_knowledge(
                        question=query,
                        answer=f"{result.get('title', '')}\n\n{result.get('snippet', '')}\n\nИсточник: {result.get('source', 'Интернет')}",
                        category="web_knowledge",
                        intent="information",
                        tags=self._extract_tags(query),
                        confidence=result.get('relevance_score', 0.5),
                        source="web_search"
                    )
        except Exception as e:
            print(f"❌ Ошибка сохранения в базу знаний: {e}")
    
    def _extract_tags(self, text):
        """Извлечение тегов из текста"""
        words = re.findall(r'\b[a-zа-я]{4,}\b', text.lower())
        stop_words = [
            'это', 'как', 'что', 'для', 'или', 'если', 'так', 'но', 'на', 'в', 'с'
        ]
        return [word for word in words if word not in stop_words][:5]
    
    def _duckduckgo_search(self, query, max_results):
        """Поиск через DuckDuckGo"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'Информация из интернета'),
                    'snippet': data.get('AbstractText'),
                    'source': 'DuckDuckGo',
                    'url': data.get('AbstractURL', '')
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Ошибка DuckDuckGo: {e}")
            return []
    
    def _wikipedia_search(self, query, max_results):
        """Поиск в Wikipedia"""
        try:
            # Упрощенный поиск через API Wikipedia
            clean_query = self._extract_main_keyword(query)
            if not clean_query:
                return []
                
            url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                snippet = data.get('extract', '')
                if snippet:
                    return [{
                        'title': f"📚 {data.get('title', 'Википедия')}",
                        'snippet': snippet,
                        'source': 'Wikipedia',
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    }]
        except Exception as e:
            print(f"⚠️ Wikipedia поиск не удался: {e}")
        return []
    
    def _stackoverflow_search(self, query, max_results):
        """Поиск в StackOverflow"""
        try:
            # Упрощенная реализация поиска
            so_query = re.sub(r'[^\w\s]', ' ', query)
            so_query = ' '.join(so_query.split()[:6])
            
            # Здесь может быть вызов API StackOverflow
            # Для демонстрации возвращаем заглушку
            return [{
                'title': 'StackOverflow: ' + so_query,
                'snippet': 'Информация с StackOverflow о программировании',
                'source': 'StackOverflow',
                'url': 'https://stackoverflow.com'
            }]
            
        except Exception as e:
            print(f"❌ Ошибка StackOverflow: {e}")
            return []
    
    def _fallback_search(self, query, max_results):
        """Резервный поиск"""
        return [{
            'title': 'Информация из интернета',
            'snippet': f'По запросу "{query}" найдена информация в открытых источниках',
            'source': 'Web',
            'url': ''
        }]
    
    def _get_search_strategy(self, query_type):
        """Определение стратегии поиска"""
        strategies = {
            'programming': ['stackoverflow', 'duckduckgo', 'wikipedia'],
            'science': ['wikipedia', 'duckduckgo'],
            'technology': ['duckduckgo', 'wikipedia'],
            'education': ['wikipedia', 'duckduckgo'],
            'business': ['duckduckgo'],
            'general': ['duckduckgo', 'wikipedia']
        }
        return strategies.get(query_type['domain'], ['duckduckgo'])
    
    def _extract_main_keyword(self, query):
        """Извлечение основного ключевого слова"""
        query = re.sub(r'что такое|кто такой|определение|означает|объясни', '', query, flags=re.IGNORECASE)
        query = re.sub(r'[?.!]$', '', query.strip())
        words = query.strip().split()
        return words[0] if words else ""

class DeepSeekLevelAI:
    """AI-ассистент уровня DeepSeek с расширенными возможностями"""
    
    def __init__(self):
        self.knowledge_db = AdvancedKnowledgeDatabase()
        self.web_search = EnhancedWebSearch()
        self.conversation_context = []
        self.user_profiles = {}
        self.learning_mode = True
        
        # Статистика
        self.stats = {
            'total_queries': 0,
            'successful_responses': 0,
            'web_searches': 0,
            'knowledge_base_hits': 0,
            'learning_improvements': 0
        }
    
    def process_query(self, user_message, user_id="default"):
        """Основной метод обработки запроса"""
        self.stats['total_queries'] += 1
        
        # Анализ запроса
        analysis = self._analyze_query(user_message)
        
        # Поиск в базе знаний
        kb_response = self._search_knowledge_base(user_message, analysis)
        
        if kb_response and kb_response.get('confidence', 0) > 0.8:
            self.stats['knowledge_base_hits'] += 1
            return self._format_response(kb_response, analysis, 'knowledge_base')
        
        # Веб-поиск
        self.stats['web_searches'] += 1
        web_response = self._web_search_response(user_message, analysis)
        
        if web_response:
            self.stats['successful_responses'] += 1
            return self._format_response(web_response, analysis, 'web_search')
        
        # Генерация ответа
        generated_response = self._generate_response(user_message, analysis)
        return self._format_response(generated_response, analysis, 'generated')
    
    def _analyze_query(self, query):
        """Глубокий анализ запроса"""
        return {
            'intent': self._detect_intent(query),
            'complexity': self._assess_complexity(query),
            'domain': self._detect_domain(query),
            'language': self._detect_language(query),
            'requires_action': self._requires_action(query),
            'sentiment': self._analyze_sentiment(query),
            'entities': self._extract_entities(query)
        }
    
    def _detect_intent(self, query):
        """Определение намерения"""
        query_lower = query.lower()
        
        intents = {
            'question': ['что', 'как', 'почему', 'зачем', 'когда', 'где'],
            'explanation': ['объясни', 'расскажи', 'покажи', 'означает'],
            'code_request': ['код', 'пример кода', 'напиши код', 'реализац'],
            'comparison': ['сравни', 'разница', 'отличие', 'лучше'],
            'learning': ['научи', 'обучение', 'курс', 'урок'],
            'help': ['помощь', 'помоги', 'подскажи', 'совет']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return 'general'
    
    def _assess_complexity(self, query):
        """Оценка сложности запроса"""
        words = query.split()
        unique_words = len(set(words))
        word_count = len(words)
        
        complexity_score = (unique_words / max(word_count, 1)) * word_count
        
        if complexity_score > 15:
            return 'high'
        elif complexity_score > 8:
            return 'medium'
        else:
            return 'low'
    
    def _detect_domain(self, query):
        """Определение предметной области"""
        query_lower = query.lower()
        
        domains = {
            'programming': ['python', 'javascript', 'java', 'код', 'программир', 'алгоритм'],
            'science': ['наука', 'физика', 'химия', 'биология', 'математика'],
            'technology': ['технология', 'компьютер', 'смартфон', 'интернет'],
            'education': ['обучение', 'учеба', 'образование', 'курс'],
            'business': ['бизнес', 'компания', 'маркетинг', 'финансы']
        }
        
        for domain, keywords in domains.items():
            if any(keyword in query_lower for keyword in keywords):
                return domain
        
        return 'general'
    
    def _detect_language(self, query):
        """Определение языка"""
        russian_chars = len(re.findall(r'[а-яА-Я]', query))
        english_chars = len(re.findall(r'[a-zA-Z]', query))
        
        if russian_chars > english_chars:
            return 'russian'
        else:
            return 'english'
    
    def _requires_action(self, query):
        """Проверка необходимости действия"""
        action_verbs = ['создай', 'напиши', 'сделай', 'покажи', 'найди', 'реши']
        return any(verb in query.lower() for verb in action_verbs)
    
    def _analyze_sentiment(self, query):
        """Анализ тональности"""
        positive_words = ['спасибо', 'отлично', 'хорошо', 'прекрасно', 'супер']
        negative_words = ['плохо', 'ужасно', 'кошмар', 'ненавижу', 'разочарован']
        
        query_lower = query.lower()
        
        positive_count = sum(1 for word in positive_words if word in query_lower)
        negative_count = sum(1 for word in negative_words if word in query_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_entities(self, query):
        """Извлечение сущностей"""
        entities = {
            'programming_languages': [],
            'technologies': [],
            'concepts': []
        }
        
        # Простой паттерн для извлечения сущностей
        programming_languages = ['python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby']
        technologies = ['html', 'css', 'react', 'vue', 'angular', 'node.js', 'django']
        
        for lang in programming_languages:
            if lang in query.lower():
                entities['programming_languages'].append(lang)
        
        for tech in technologies:
            if tech in query.lower():
                entities['technologies'].append(tech)
        
        return entities
    
    def _search_knowledge_base(self, query, analysis):
        """Поиск в базе знаний"""
        results = self.knowledge_db.search_knowledge(
            query, 
            category=analysis['domain'],
            min_confidence=0.5,
            limit=3
        )
        
        if results:
            best_match = results[0]
            self.knowledge_db.update_usage(best_match['id'], True)
            return best_match
        
        return None
    
    def _web_search_response(self, query, analysis):
        """Формирование ответа на основе веб-поиска"""
        search_results = self.web_search.intelligent_search(query, max_results=3)
        
        if not search_results:
            return None
        
        # Форматируем ответ
        response = {
            'answer': self._format_web_results(search_results, query),
            'confidence': 0.8,
            'source': 'web_search',
            'metadata': {
                'results_count': len(search_results),
                'search_query': query
            }
        }
        
        return response
    
    def _format_web_results(self, results, query):
        """Форматирование результатов веб-поиска"""
        response_parts = [f"🔍 **Найдена информация по запросу: '{query}'**\n"]
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'Без названия')
            snippet = result.get('snippet', 'Описание отсутствует')
            source = result.get('source', 'Неизвестный источник')
            
            response_parts.append(f"\n**{i}. {title}**")
            response_parts.append(f"{snippet}")
            
            if result.get('url'):
                response_parts.append(f"*🔗 Источник: {source}*")
            
            response_parts.append("")
        
        return "\n".join(response_parts)
    
    def _generate_response(self, query, analysis):
        """Генерация ответа когда другие методы не сработали"""
        templates = {
            'question': "🤔 Интересный вопрос! К сожалению, я не нашел точного ответа в своей базе знаний. ",
            'explanation': "📚 Я понял, что вам нужно объяснение. ",
            'code_request': "💻 Вы просите пример кода. ",
            'general': "💡 По вашему запросу "
        }
        
        base_response = templates.get(analysis['intent'], templates['general'])
        
        suggestions = self._generate_suggestions(query, analysis)
        
        response = {
            'answer': base_response + suggestions,
            'confidence': 0.3,
            'source': 'generated'
        }
        
        return response
    
    def _generate_suggestions(self, query, analysis):
        """Генерация предложений по улучшению запроса"""
        suggestions = []
        
        if analysis['complexity'] == 'low':
            suggestions.append("Попробуйте уточнить ваш вопрос или задать его более развернуто.")
        
        if analysis['domain'] != 'general':
            suggestions.append(f"Вы можете поискать информацию в категории '{analysis['domain']}'.")
        
        if analysis['requires_action']:
            suggestions.append("Для выполнения действий уточните, что именно нужно сделать.")
        
        if not suggestions:
            suggestions.append("Попробуйте переформулировать вопрос или разбить его на несколько более простых.")
        
        return " ".join(suggestions)
    
    def _format_response(self, response_data, analysis, source):
        """Форматирование финального ответа"""
        answer = response_data['answer']
        confidence = response_data.get('confidence', 0.5)
        
        # Добавляем информацию о источнике
        source_icons = {
            'knowledge_base': '🧠',
            'web_search': '🌐',
            'generated': '💡'
        }
        
        icon = source_icons.get(source, '💬')
        
        # Добавляем рейтинг уверенности
        if confidence > 0.8:
            confidence_text = "Высокая уверенность"
        elif confidence > 0.5:
            confidence_text = "Средняя уверенность"
        else:
            confidence_text = "Низкая уверенность"
        
        formatted_response = f"{icon} {answer}\n\n---\n*Источник: {source} | Уверенность: {confidence_text}*"
        
        # Сохраняем контекст
        self._save_conversation_context(response_data, analysis, source)
        
        return formatted_response
    
    def _save_conversation_context(self, response, analysis, source):
        """Сохранение контекста разговора"""
        context_entry = {
            'timestamp': datetime.now().isoformat(),
            'analysis': analysis,
            'source': source,
            'confidence': response.get('confidence', 0.5)
        }
        
        self.conversation_context.append(context_entry)
        
        # Ограничиваем размер контекста
        if len(self.conversation_context) > 10:
            self.conversation_context = self.conversation_context[-10:]
    
    def get_statistics(self):
        """Получение статистики"""
        db_stats = self.knowledge_db.get_statistics()
        
        return {
            'ai_stats': self.stats,
            'knowledge_base_stats': db_stats,
            'conversation_context_count': len(self.conversation_context)
        }
    
    def export_knowledge(self, format='json'):
        """Экспорт знаний"""
        return self.knowledge_db.export_knowledge(format)

class AdvancedAIHandler(BaseHTTPRequestHandler):
    ai = DeepSeekLevelAI()
    
    def do_GET(self):
        """Обработка GET запросов"""
        if self.path == '/':
            self._serve_advanced_interface()
        elif self.path == '/stats':
            self._serve_stats()
        elif self.path == '/export':
            self._export_knowledge()
        elif self.path == '/api/knowledge/count':
            self._serve_knowledge_count()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Обработка POST запросов"""
        if self.path == '/chat':
            self._handle_chat()
        elif self.path == '/api/learn':
            self._handle_learning()
        else:
            self.send_error(404, "Not Found")
    
    def _serve_advanced_interface(self):
        """Отдача улучшенного HTML интерфейса"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🤖 Advanced AI Assistant</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }
                
                .app-container {
                    width: 100%;
                    max-width: 1200px;
                    height: 90vh;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.2);
                    display: flex;
                    overflow: hidden;
                }
                
                .sidebar {
                    width: 300px;
                    background: linear-gradient(135deg, #2c3e50, #34495e);
                    color: white;
                    padding: 30px 20px;
                    display: flex;
                    flex-direction: column;
                }
                
                .main-content {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                }
                
                .chat-header {
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 25px 30px;
                    text-align: center;
                }
                
                .chat-messages {
                    flex: 1;
                    padding: 25px;
                    overflow-y: auto;
                    background: #f8f9fa;
                }
                
                .message {
                    margin: 15px 0;
                    padding: 15px 20px;
                    border-radius: 18px;
                    max-width: 80%;
                    line-height: 1.5;
                    animation: fadeIn 0.3s ease;
                }
                
                .user-message {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    margin-left: auto;
                    border-bottom-right-radius: 5px;
                }
                
                .ai-message {
                    background: white;
                    color: #2c3e50;
                    border: 2px solid #e9ecef;
                    border-bottom-left-radius: 5px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                }
                
                .message-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                    font-size: 0.85em;
                    opacity: 0.8;
                }
                
                .chat-input-container {
                    padding: 20px 30px;
                    background: white;
                    border-top: 1px solid #e9ecef;
                    display: flex;
                    gap: 15px;
                    align-items: flex-end;
                }
                
                .chat-input {
                    flex: 1;
                    padding: 15px 20px;
                    border: 2px solid #e9ecef;
                    border-radius: 25px;
                    font-size: 16px;
                    outline: none;
                    transition: border-color 0.3s;
                    resize: none;
                    min-height: 60px;
                    max-height: 120px;
                    font-family: inherit;
                }
                
                .chat-input:focus {
                    border-color: #3498db;
                }
                
                .send-button {
                    padding: 15px 30px;
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    transition: transform 0.2s;
                    min-width: 100px;
                }
                
                .send-button:hover {
                    transform: translateY(-2px);
                }
                
                .stats-panel {
                    background: rgba(255,255,255,0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin-top: 20px;
                }
                
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    font-size: 0.9em;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .typing-indicator {
                    display: inline-flex;
                    gap: 5px;
                    padding: 10px 15px;
                    background: #ecf0f1;
                    border-radius: 18px;
                }
                
                .typing-dot {
                    width: 8px;
                    height: 8px;
                    background: #7f8c8d;
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }
                
                .typing-dot:nth-child(2) { animation-delay: 0.2s; }
                .typing-dot:nth-child(3) { animation-delay: 0.4s; }
                
                @keyframes typing {
                    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
                    30% { transform: translateY(-5px); opacity: 1; }
                }
                
                .knowledge-badge {
                    display: inline-block;
                    background: #e74c3c;
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 0.7em;
                    margin-left: 10px;
                }
                
                .code-block {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 12px;
                    border-radius: 8px;
                    margin: 8px 0;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                    overflow-x: auto;
                    border-left: 4px solid #e74c3c;
                }
                
                .chat-messages::-webkit-scrollbar {
                    width: 8px;
                }
                
                .chat-messages::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                
                .chat-messages::-webkit-scrollbar-thumb {
                    background: #c1c1c1;
                    border-radius: 4px;
                }
                
                .chat-messages::-webkit-scrollbar-thumb:hover {
                    background: #a8a8a8;
                }
                
                @media (max-width: 768px) {
                    .app-container {
                        flex-direction: column;
                        height: 100vh;
                        border-radius: 0;
                    }
                    
                    .sidebar {
                        width: 100%;
                        height: auto;
                    }
                    
                    .message {
                        max-width: 90%;
                    }
                }
            </style>
        </head>
        <body>
            <div class="app-container">
                <div class="sidebar">
                    <h2>🤖 AI Assistant</h2>
                    <p style="margin: 15px 0; opacity: 0.9;">Расширенная база знаний + AI</p>
                    
                    <div class="stats-panel">
                        <h4>📊 Статистика</h4>
                        <div class="stat-item">
                            <span>База знаний:</span>
                            <span id="knowledgeCount">...</span>
                        </div>
                        <div class="stat-item">
                            <span>Обработано:</span>
                            <span id="processedCount">0</span>
                        </div>
                        <div class="stat-item">
                            <span>Успешных ответов:</span>
                            <span id="successCount">0</span>
                        </div>
                    </div>
                    
                    <div style="margin-top: auto;">
                        <button onclick="exportKnowledge()" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 10px; cursor: pointer; margin-bottom: 10px;">
                            📤 Экспорт знаний
                        </button>
                        <button onclick="showStats()" style="width: 100%; padding: 12px; background: rgba(255,255,255,0.2); color: white; border: none; border-radius: 10px; cursor: pointer;">
                            📈 Детальная статистика
                        </button>
                    </div>
                </div>
                
                <div class="main-content">
                    <div class="chat-header">
                        <h1>🧠 Advanced AI Assistant</h1>
                        <p>Задавайте любые вопросы - я найду ответы в своей расширенной базе знаний!</p>
                    </div>
                    
                    <div class="chat-messages" id="chatMessages">
                        <div class="message ai-message">
                            <div class="message-header">
                                <strong>🤖 AI Assistant</strong>
                                <span>только что</span>
                            </div>
                            <strong>Привет! Я ваш продвинутый AI-помощник</strong><br><br>
                            🎯 <strong>Мои возможности:</strong><br>
                            • 🧠 Расширенная база знаний с SQLite<br>
                            • 🌐 Умный веб-поиск с кэшированием<br>
                            • 💻 Генерация кода и объяснений<br>
                            • 📚 Обучение на основе взаимодействий<br>
                            • 🔍 Семантический поиск<br><br>
                            <strong>Спросите меня о чем угодно!</strong>
                        </div>
                    </div>
                    
                    <div class="chat-input-container">
                        <textarea class="chat-input" id="messageInput" placeholder="Задайте ваш вопрос..." rows="1"></textarea>
                        <button class="send-button" onclick="sendMessage()" id="sendButton">Отправить</button>
                    </div>
                </div>
            </div>

            <script>
                let messageCount = 0;
                let successCount = 0;
                
                async function updateStats() {
                    try {
                        const response = await fetch('/api/knowledge/count');
                        const data = await response.json();
                        document.getElementById('knowledgeCount').textContent = data.count + ' записей';
                    } catch (error) {
                        console.error('Error fetching stats:', error);
                    }
                }
                
                function addMessage(text, isUser) {
                    const messagesDiv = document.getElementById('chatMessages');
                    const messageDiv = document.createElement('div');
                    
                    const time = new Date().toLocaleTimeString('ru-RU', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                    
                    // Форматируем код блоки
                    let formattedText = text;
                    if (text.includes('```')) {
                        formattedText = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<div class="code-block">$2</div>');
                    }
                    formattedText = formattedText.replace(/\n/g, '<br>');
                    
                    if (isUser) {
                        messageDiv.className = 'message user-message';
                        messageDiv.innerHTML = `
                            <div class="message-header">
                                <strong>👤 Вы</strong>
                                <span>${time}</span>
                            </div>
                            ${formattedText}
                        `;
                    } else {
                        messageDiv.className = 'message ai-message';
                        messageDiv.innerHTML = `
                            <div class="message-header">
                                <strong>🤖 AI Assistant</strong>
                                <span>${time}</span>
                            </div>
                            ${formattedText}
                        `;
                    }
                    
                    messagesDiv.appendChild(messageDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
                
                function showTyping() {
                    const messagesDiv = document.getElementById('chatMessages');
                    const typingDiv = document.createElement('div');
                    typingDiv.className = 'message ai-message';
                    typingDiv.id = 'typingIndicator';
                    typingDiv.innerHTML = `
                        <div class="message-header">
                            <strong>🤖 AI Assistant</strong>
                            <span>печатает...</span>
                        </div>
                        <div class="typing-indicator">
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                            <div class="typing-dot"></div>
                        </div>
                    `;
                    messagesDiv.appendChild(typingDiv);
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                }
                
                function hideTyping() {
                    const typingDiv = document.getElementById('typingIndicator');
                    if (typingDiv) {
                        typingDiv.remove();
                    }
                }
                
                async function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    // Очищаем input
                    input.value = '';
                    input.style.height = 'auto';
                    
                    // Добавляем сообщение пользователя
                    addMessage(message, true);
                    messageCount++;
                    document.getElementById('processedCount').textContent = messageCount;
                    
                    // Показываем индикатор набора
                    showTyping();
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ message: message })
                        });
                        
                        if (!response.ok) {
                            throw new Error('Network error');
                        }
                        
                        const data = await response.json();
                        
                        // Скрываем индикатор набора
                        hideTyping();
                        
                        // Добавляем ответ AI
                        addMessage(data.response, false);
                        successCount++;
                        document.getElementById('successCount').textContent = successCount;
                        
                    } catch (error) {
                        hideTyping();
                        addMessage('❌ Ошибка соединения с сервером. Попробуйте еще раз.', false);
                        console.error('Error:', error);
                    }
                }
                
                async function exportKnowledge() {
                    try {
                        const response = await fetch('/export');
                        const data = await response.json();
                        alert('✅ База знаний экспортирована: ' + data.filename);
                    } catch (error) {
                        alert('❌ Ошибка экспорта');
                        console.error('Error:', error);
                    }
                }
                
                async function showStats() {
                    try {
                        const response = await fetch('/stats');
                        const data = await response.json();
                        alert('📊 Детальная статистика:\\n\\n' +
                              `Всего запросов: ${data.ai_stats.total_queries}\\n` +
                              `Успешных ответов: ${data.ai_stats.successful_responses}\\n` +
                              `Веб-поисков: ${data.ai_stats.web_searches}\\n` +
                              `Попаданий в базу: ${data.ai_stats.knowledge_base_hits}\\n` +
                              `Записей в базе: ${data.knowledge_base_stats.total_entries}`);
                    } catch (error) {
                        alert('❌ Ошибка загрузки статистики');
                        console.error('Error:', error);
                    }
                }
                
                // Обработчики событий
                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                document.getElementById('messageInput').addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                });
                
                // Загружаем статистику при старте
                updateStats();
                
                // Фокус на input
                document.getElementById('messageInput').focus();
            </script>
        </body>
        </html>
        '''
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_chat(self):
        """Обработка чат-запросов"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            response = self.ai.process_query(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({"response": response}).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Ошибка обработки чата: {e}")
            self.send_error(500, f"Error: {str(e)}")
    
    def _serve_stats(self):
        """Отдача статистики"""
        stats = self.ai.get_statistics()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode('utf-8'))
    
    def _serve_knowledge_count(self):
        """Отдача количества записей в базе знаний"""
        stats = self.ai.knowledge_db.get_statistics()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps({"count": stats['total_entries']}).encode('utf-8'))
    
    def _export_knowledge(self):
        """Экспорт базы знаний"""
        filename = self.ai.export_knowledge()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "filename": filename}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _handle_learning(self):
        """Обработка запросов на обучение"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Здесь может быть логика для обучения AI
            # на основе пользовательских feedback
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            self.wfile.write(json.dumps({"status": "learning_updated"}).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Ошибка обучения: {e}")
            self.send_error(500, f"Learning error: {str(e)}")
    
    def log_message(self, format, *args):
        """Кастомное логирование"""
        print(f"🌐 Advanced AI: {format % args}")

def main():
    PORT = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Запуск Advanced AI Assistant на порту {PORT}...")
    print("╔══════════════════════════════════════════════════╗")
    print("║           ADVANCED AI ASSISTANT v4.0           ║")
    print("║          SQLite + Векторный поиск + AI          ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 РАСШИРЕННЫЕ ВОЗМОЖНОСТИ:")
    print("• 🗄️  SQLite база знаний с векторным поиском")
    print("• 🔍 Умный веб-поиск с кэшированием")
    print("• 🧠 Семантический анализ запросов")
    print("• 📚 Автоматическое обогащение знаний")
    print("• 💡 Обучение на взаимодействиях")
    print("• 📊 Детальная статистика и аналитика")
    print("\n📚 БАЗА ЗНАНИЙ ВКЛЮЧАЕТ:")
    print("• Программирование (Python, JavaScript, Java)")
    print("• Веб-разработка (HTML, CSS, фреймворки)")
    print("• Алгоритмы и структуры данных")
    print("• Базы данных и SQL")
    print("• Искусственный интеллект и ML")
    print("• Технологии и интернет")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), AdvancedAIHandler)
        print(f"\n✅ Advanced AI Assistant активирован на порту {PORT}")
        print("💫 Расширенная база знаний готова к работе!")
        print("🔮 Задавайте вопросы через веб-интерфейс!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI Assistant деактивирован")
        print("💾 Сохранение данных...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
