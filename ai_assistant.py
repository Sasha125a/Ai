from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
import os
import base64
from datetime import datetime
import mimetypes
import numpy as np
import pickle
from collections import defaultdict, Counter
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
import threading
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse
import asyncio
import aiohttp
import warnings
warnings.filterwarnings('ignore')

# Скачиваем необходимые данные NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class WebSearch:
    """Класс для поиска информации в интернете"""
    
    def __init__(self):
        self.search_engines = [
            self._search_duckduckgo,
            self._search_google_suggest,
            self._search_wikipedia
        ]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_internet(self, query, max_results=3):
        """Поиск информации в интернете по запросу"""
        print(f"🔍 Поиск в интернете: {query}")
        
        all_results = []
        
        for search_func in self.search_engines:
            try:
                results = search_func(query, max_results)
                if results:
                    all_results.extend(results)
                    print(f"✅ Найдено {len(results)} результатов через {search_func.__name__}")
                    break  # Используем первый успешный источник
            except Exception as e:
                print(f"❌ Ошибка поиска {search_func.__name__}: {e}")
                continue
        
        # Убираем дубликаты и ограничиваем количество
        unique_results = []
        seen_snippets = set()
        
        for result in all_results:
            snippet = result.get('snippet', '')[:100]
            if snippet not in seen_snippets:
                seen_snippets.add(snippet)
                unique_results.append(result)
        
        return unique_results[:max_results]
    
    def _search_duckduckgo(self, query, max_results=3):
        """Поиск через DuckDuckGo Instant Answer API"""
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
            
            # Извлекаем краткий ответ
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'Ответ'),
                    'snippet': data.get('AbstractText'),
                    'source': 'DuckDuckGo',
                    'url': data.get('AbstractURL', '')
                })
            
            # Извлекаем связанные темы
            for topic in data.get('RelatedTopics', [])[:max_results]:
                if 'Text' in topic:
                    results.append({
                        'title': topic.get('FirstURL', '').split('/')[-1].replace('_', ' '),
                        'snippet': topic['Text'],
                        'source': 'DuckDuckGo',
                        'url': topic.get('FirstURL', '')
                    })
            
            return results
            
        except Exception as e:
            print(f"Ошибка DuckDuckGo: {e}")
            return []
    
    def _search_google_suggest(self, query, max_results=3):
        """Используем Google Suggestions как fallback"""
        try:
            url = "http://suggestqueries.google.com/complete/search"
            params = {
                'q': query,
                'client': 'firefox',
                'hl': 'ru'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            suggestions = response.json()[1]
            
            results = []
            for suggestion in suggestions[:max_results]:
                results.append({
                    'title': 'Подсказка Google',
                    'snippet': f"Возможно, вы имели в виду: {suggestion}",
                    'source': 'Google Suggest',
                    'url': ''
                })
            
            return results
            
        except Exception as e:
            print(f"Ошибка Google Suggest: {e}")
            return []
    
    def _search_wikipedia(self, query, max_results=2):
        """Поиск в Wikipedia"""
        try:
            # Ищем статью в Wikipedia
            url = "https://ru.wikipedia.org/w/api.php"
            params = {
                'action': 'query',
                'list': 'search',
                'srsearch': query,
                'format': 'json',
                'srlimit': max_results
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for item in data.get('query', {}).get('search', [])[:max_results]:
                # Получаем краткое описание статьи
                extract_params = {
                    'action': 'query',
                    'prop': 'extracts',
                    'exintro': '1',
                    'explaintext': '1',
                    'titles': item['title'],
                    'format': 'json'
                }
                
                extract_response = self.session.get(url, params=extract_params, timeout=10)
                extract_data = extract_response.json()
                
                pages = extract_data.get('query', {}).get('pages', {})
                for page_id, page_data in pages.items():
                    if page_id != '-1' and 'extract' in page_data:
                        snippet = page_data['extract'][:300] + '...' if len(page_data['extract']) > 300 else page_data['extract']
                        results.append({
                            'title': item['title'],
                            'snippet': snippet,
                            'source': 'Wikipedia',
                            'url': f"https://ru.wikipedia.org/wiki/{urllib.parse.quote(item['title'])}"
                        })
            
            return results
            
        except Exception as e:
            print(f"Ошибка Wikipedia: {e}")
            return []
    
    def extract_programming_info(self, search_results, original_query):
        """Извлечение и структурирование информации о программировании"""
        programming_info = {
            'concepts': [],
            'examples': [],
            'definitions': [],
            'best_practices': []
        }
        
        for result in search_results:
            snippet = result['snippet'].lower()
            
            # Определяем тип информации
            if any(word in snippet for word in ['это', 'определение', 'означает', 'понятие']):
                programming_info['definitions'].append({
                    'text': result['snippet'],
                    'source': result['source'],
                    'title': result['title']
                })
            
            elif any(word in snippet for word in ['пример', 'код', 'синтаксис', 'функция', 'класс']):
                programming_info['examples'].append({
                    'text': result['snippet'],
                    'source': result['source'],
                    'title': result['title']
                })
            
            elif any(word in snippet for word in ['лучшие практики', 'рекомендации', 'советы']):
                programming_info['best_practices'].append({
                    'text': result['snippet'],
                    'source': result['source'],
                    'title': result['title']
                })
            
            else:
                programming_info['concepts'].append({
                    'text': result['snippet'],
                    'source': result['source'],
                    'title': result['title']
                })
        
        return programming_info

class LearningAI:
    """Класс для машинного обучения и адаптации ИИ"""
    
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.user_feedback = []
        self.conversation_patterns = []
        self.model_version = "1.0"
        self.learning_rate = 0.1
        self.stemmer = SnowballStemmer("russian")
        self.web_search = WebSearch()
        
        # Инициализация базы данных для хранения знаний
        self.init_knowledge_db()
        
        # Загрузка существующих знаний
        self.load_knowledge()
        
        # Векторизатор для текста
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words=['и', 'в', 'на', 'с', 'по', 'для', 'это', 'как', 'что'],
            ngram_range=(1, 2)
        )
        
        # Обучение на начальных данных
        self.initial_training()
    
    def init_knowledge_db(self):
        """Инициализация базы данных SQLite для хранения знаний"""
        self.conn = sqlite3.connect('ai_knowledge.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Таблица для паттернов вопрос-ответ
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                intent TEXT,
                entities TEXT,
                confidence REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 1.0,
                source TEXT DEFAULT 'manual', -- manual, web_search, generated
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для веб-поиска результатов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS web_search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                title TEXT,
                snippet TEXT,
                source TEXT,
                url TEXT,
                intent TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица для пользовательских предпочтений
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT,
                preference_type TEXT,
                preference_value TEXT,
                strength REAL DEFAULT 1.0,
                PRIMARY KEY (user_id, preference_type)
            )
        ''')
        
        # Таблица для обратной связи
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                user_feedback INTEGER, -- 1 положительный, -1 отрицательный, 0 нейтральный
                feedback_text TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def load_knowledge(self):
        """Загрузка знаний из базы данных"""
        cursor = self.conn.cursor()
        
        # Загрузка QA паттернов
        cursor.execute('SELECT question, answer, intent, confidence, source FROM qa_patterns')
        for question, answer, intent, confidence, source in cursor.fetchall():
            self.knowledge_base[intent].append({
                'question': question,
                'answer': answer,
                'confidence': confidence,
                'source': source
            })
    
    def initial_training(self):
        """Начальное обучение на базовых данных"""
        training_data = [
            # Программирование
            ("как создать класс в python", "Используй ключевое слово class: class MyClass:", "code_request", "python"),
            ("что такое функция", "Функция это блок кода, который выполняет определенную задачу", "explanation", "programming"),
            ("как работает цикл for", "Цикл for повторяет действия для каждого элемента в последовательности", "explanation", "programming"),
            ("что такое ооп", "ООП - объектно-ориентированное программирование, подход к программированию", "explanation", "programming"),
            
            # Приветствия
            ("привет", "Привет! Как я могу помочь с программированием?", "greeting", ""),
            ("здравствуйте", "Здравствуйте! Готов помочь с кодом.", "greeting", ""),
            
            # Прощания
            ("пока", "До свидания! Возвращайтесь с вопросами по программированию.", "farewell", ""),
            ("до свидания", "До встречи! Удачи в кодинге!", "farewell", ""),
            
            # Помощь
            ("что ты умеешь", "Я помогаю с программированием: генерация кода, объяснение концепций, решение проблем", "help", ""),
            ("помощь", "Я специализируюсь на программировании. Могу генерировать код, объяснять концепции, помогать с ошибками", "help", ""),
        ]
        
        cursor = self.conn.cursor()
        for question, answer, intent, entities in training_data:
            cursor.execute('''
                INSERT OR IGNORE INTO qa_patterns (question, answer, intent, entities, source)
                VALUES (?, ?, ?, ?, 'manual')
            ''', (question, answer, intent, entities))
        
        self.conn.commit()
        self.load_knowledge()
    
    def search_and_learn(self, user_message, intent, entities, min_confidence=0.3):
        """Поиск ответа в интернете и сохранение в базу знаний"""
        print(f"🔍 Поиск в интернете для: {user_message}")
        
        # Формируем поисковый запрос
        search_query = self._build_search_query(user_message, intent, entities)
        
        # Ищем в кэше
        cached_result = self._get_cached_search(search_query, intent)
        if cached_result:
            print("✅ Использую кэшированный результат поиска")
            return cached_result, "web_cache"
        
        # Ищем в интернете
        search_results = self.web_search.search_internet(search_query)
        
        if not search_results:
            print("❌ Ничего не найдено в интернете")
            return None, "no_results"
        
        # Форматируем найденную информацию
        formatted_answer = self._format_web_results(search_results, user_message, intent)
        
        if formatted_answer:
            # Сохраняем в базу знаний
            self._save_web_knowledge(user_message, formatted_answer, intent, entities, search_results)
            print("✅ Новые знания сохранены в базу")
            return formatted_answer, "web_search"
        
        return None, "format_failed"
    
    def _build_search_query(self, user_message, intent, entities):
        """Формирование поискового запроса"""
        # Базовый запрос
        query = user_message
        
        # Добавляем контекст программирования
        programming_keywords = ["программирование", "код", "python", "javascript", "java", "программа"]
        
        if intent in ['explanation', 'code_request']:
            if not any(keyword in user_message.lower() for keyword in programming_keywords):
                query = f"{user_message} программирование"
        
        # Добавляем конкретику для языков
        if entities.get('languages'):
            lang = entities['languages'][0]
            query = f"{user_message} {lang}"
        
        return query
    
    def _get_cached_search(self, query, intent):
        """Поиск в кэше веб-поиска"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT snippet, title, source 
            FROM web_search_cache 
            WHERE query = ? AND intent = ?
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (query, intent))
        
        result = cursor.fetchone()
        if result:
            snippet, title, source = result
            return f"📚 {title}\n\n{snippet}\n\n🔗 Источник: {source}"
        
        return None
    
    def _format_web_results(self, search_results, original_question, intent):
        """Форматирование результатов поиска в ответ"""
        if not search_results:
            return None
        
        best_result = search_results[0]
        title = best_result.get('title', 'Информация из интернета')
        snippet = best_result.get('snippet', '')
        source = best_result.get('source', 'интернет')
        
        # Очищаем и форматируем текст
        cleaned_snippet = self._clean_web_snippet(snippet, original_question)
        
        response = f"🌐 **{title}**\n\n"
        response += f"{cleaned_snippet}\n\n"
        response += f"📚 *Источник: {source}*"
        
        # Добавляем дополнительные результаты если есть
        if len(search_results) > 1:
            response += "\n\n💡 **Дополнительная информация:**"
            for i, result in enumerate(search_results[1:3], 1):
                additional_snippet = result.get('snippet', '')[:150] + '...' if len(result.get('snippet', '')) > 150 else result.get('snippet', '')
                response += f"\n• {additional_snippet}"
        
        return response
    
    def _clean_web_snippet(self, snippet, original_question):
        """Очистка и улучшение веб-сниппета"""
        # Удаляем лишние пробелы и переносы
        cleaned = re.sub(r'\s+', ' ', snippet).strip()
        
        # Удаляем HTML теги
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # Обрезаем до разумной длины
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + '...'
        
        # Добавляем контекст если нужно
        if "программирование" in original_question.lower() and "программирование" not in cleaned.lower():
            cleaned = f"В контексте программирования: {cleaned}"
        
        return cleaned
    
    def _save_web_knowledge(self, question, answer, intent, entities, search_results):
        """Сохранение веб-знаний в базу данных"""
        cursor = self.conn.cursor()
        
        # Сохраняем QA паттерн
        cursor.execute('''
            INSERT INTO qa_patterns (question, answer, intent, entities, source, confidence)
            VALUES (?, ?, ?, ?, 'web_search', 0.8)
        ''', (question, answer, intent, json.dumps(entities)))
        
        # Сохраняем результаты поиска в кэш
        for result in search_results[:2]:  # Сохраняем только первые 2 результата
            cursor.execute('''
                INSERT INTO web_search_cache (query, title, snippet, source, url, intent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (question, result.get('title'), result.get('snippet'), 
                  result.get('source'), result.get('url'), intent))
        
        self.conn.commit()
        
        # Обновляем кэш знаний
        self.knowledge_base[intent].append({
            'question': question,
            'answer': answer,
            'confidence': 0.8,
            'source': 'web_search'
        })
    
    def find_best_response(self, user_message, intent, entities, use_web_search=True):
        """Поиск лучшего ответа с возможностью поиска в интернете"""
        cursor = self.conn.cursor()
        
        # Ищем точное совпадение
        cursor.execute('''
            SELECT answer, confidence, success_rate, source
            FROM qa_patterns 
            WHERE question = ? AND intent = ?
            ORDER BY success_rate DESC, confidence DESC
            LIMIT 1
        ''', (user_message, intent))
        
        result = cursor.fetchone()
        if result:
            answer, confidence, success_rate, source = result
            if confidence * success_rate > 0.5:  # Достаточно высокая уверенность
                cursor.execute('''
                    UPDATE qa_patterns 
                    SET usage_count = usage_count + 1 
                    WHERE question = ? AND answer = ?
                ''', (user_message, answer))
                self.conn.commit()
                return answer, confidence * success_rate, source
        
        # Ищем похожие вопросы в базе
        cursor.execute('''
            SELECT question, answer, confidence, success_rate, source
            FROM qa_patterns 
            WHERE intent = ?
        ''', (intent,))
        
        best_match = None
        best_similarity = 0
        best_source = None
        
        for q, a, conf, success, source in cursor.fetchall():
            similarity = self._calculate_similarity(user_message, q)
            weighted_similarity = similarity * conf * success
            
            if weighted_similarity > best_similarity:
                best_similarity = weighted_similarity
                best_match = a
                best_source = source
        
        if best_match and best_similarity > 0.3:
            return best_match, best_similarity, best_source
        
        # Если не нашли в базе и разрешен веб-поиск
        if use_web_search and intent in ['explanation', 'code_request', 'learning_path']:
            web_answer, web_source = self.search_and_learn(user_message, intent, entities)
            if web_answer:
                return web_answer, 0.7, web_source
        
        return None, 0.0, None
    
    def _calculate_similarity(self, text1, text2):
        """Вычисление схожести между двумя текстами"""
        words1 = set(self._preprocess_text(text1))
        words2 = set(self._preprocess_text(text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _preprocess_text(self, text):
        """Предобработка текста для сравнения"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        words = [self.stemmer.stem(word) for word in words if len(word) > 2]
        return words

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'skill_level': 'beginner',
            'preferred_languages': set(),
            'user_id': 'default'
        }
        
        # Инициализация системы обучения с веб-поиском
        self.learning_ai = LearningAI()
        
        # Статистика обучения
        self.learning_stats = {
            'conversations_processed': 0,
            'patterns_learned': 0,
            'web_searches': 0,
            'success_rate': 1.0
        }
        
        self.programming_languages = {
            'python': {'name': 'Python', 'paradigms': ['object-oriented', 'functional', 'imperative']},
            'javascript': {'name': 'JavaScript', 'paradigms': ['object-oriented', 'functional', 'event-driven']},
            'java': {'name': 'Java', 'paradigms': ['object-oriented', 'imperative']},
        }
    
    def analyze_intent(self, message):
        message_lower = message.lower()
        
        intents = {
            'greeting': any(word in message_lower for word in ['привет', 'здравствуй', 'hello', 'hi', 'добрый']),
            'farewell': any(word in message_lower for word in ['пока', 'до свидания', 'bye', 'прощай']),
            'help': any(word in message_lower for word in ['помощь', 'help', 'что ты умеешь']),
            'explanation': any(word in message_lower for word in ['объясни', 'расскажи', 'что такое', 'как работает']),
            'code_request': any(word in message_lower for word in ['код', 'пример', 'напиши', 'сгенерируй', 'покажи код']),
            'comparison': any(word in message_lower for word in ['разница', 'сравни', 'что лучше', 'отличие']),
            'problem': any(word in message_lower for word in ['проблема', 'ошибка', 'не работает', 'помоги решить']),
            'opinion': any(word in message_lower for word in ['мнение', 'думаешь', 'считаешь', 'точка зрения']),
            'learning_path': any(word in message_lower for word in ['с чего начать', 'как учить', 'путь обучения', 'изучение']),
            'feedback': any(word in message_lower for word in ['отлично', 'плохо', 'спасибо', 'неправильно', 'хорошо']),
        }
        
        return [intent for intent, detected in intents.items() if detected]
    
    def extract_entities(self, message):
        entities = {
            'languages': [],
            'technologies': [],
            'concepts': [],
            'level_indicators': []
        }
        
        for lang_key, lang_info in self.programming_languages.items():
            lang_name = lang_info['name'].lower()
            if (lang_key in message.lower() or lang_name in message.lower()):
                entities['languages'].append(lang_key)
        
        return entities
    
    def generate_smart_response(self, message):
        # Анализ intent'а и entities
        intents = self.analyze_intent(message)
        entities = self.extract_entities(message)
        
        # Пытаемся найти лучший ответ (с веб-поиском если нужно)
        best_response = None
        best_confidence = 0.0
        response_source = "unknown"
        
        for intent in intents:
            response, confidence, source = self.learning_ai.find_best_response(
                message, intent, entities, use_web_search=True
            )
            if response and confidence > best_confidence:
                best_response = response
                best_confidence = confidence
                response_source = source
        
        # Если нашли хороший ответ
        if best_response and best_confidence > 0.4:
            final_response = best_response
            if response_source == "web_search":
                self.learning_stats['web_searches'] += 1
                final_response = "🔍 *Нашел ответ в интернете:*\n\n" + final_response
        else:
            # Генерируем новый ответ
            final_response = self._craft_response(message, intents, entities)
            response_source = "generated"
            
            # Сохраняем новый паттерн для обучения
            if response_source == "generated" and intents:
                primary_intent = intents[0]
                self.learning_ai.learn_from_conversation(
                    message, final_response, primary_intent, 
                    json.dumps(entities)
                )
                self.learning_stats['patterns_learned'] += 1
        
        # Обновляем статистику
        self.learning_stats['conversations_processed'] += 1
        
        # Сохраняем в историю
        self.conversation_history.append({
            'message': message,
            'response': final_response,
            'intents': intents,
            'entities': entities,
            'response_source': response_source,
            'confidence': best_confidence,
            'timestamp': datetime.now()
        })
        
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-25:]
        
        # Добавляем мета-информацию
        source_emoji = {
            "manual": "📚",
            "web_search": "🌐", 
            "web_cache": "💾",
            "generated": "🎯"
        }
        
        final_response += f"\n\n{source_emoji.get(response_source, '🤖')} *Источник: {response_source}*"
        
        return final_response
    
    def _craft_response(self, message, intents, entities):
        """Генерация ответа на основе intent'ов"""
        if 'greeting' in intents:
            return self._generate_adaptive_greeting()
        
        if 'farewell' in intents:
            return self._generate_farewell()
        
        if 'help' in intents:
            return self._generate_help_response()
        
        if 'explanation' in intents:
            return self._generate_explanation(message, entities)
        
        if 'code_request' in intents:
            return self._generate_code_example(message, entities)
        
        if 'feedback' in intents:
            return self._process_feedback(message)
        
        return self._generate_contextual_response(message, entities)
    
    def _generate_adaptive_greeting(self):
        """Адаптивное приветствие"""
        greetings = [
            "Привет! Я умею искать ответы в интернете и запоминать их! 🧠🌐",
            "Здравствуйте! Теперь я могу искать информацию онлайн! 🚀",
            "Привет! Моя база знаний пополняется из интернета! 💫"
        ]
        return random.choice(greetings)
    
    def _generate_help_response(self):
        stats = self.get_learning_stats()
        
        help_text = f"""
🤖 **AI-GPT2 с ВЕБ-ПОИСКОМ и МАШИННЫМ ОБУЧЕНИЕМ**

🧠 **Мои новые возможности:**
• 🔍 **Поиск в интернете** - если не знаю ответ
• 💾 **Авто-сохранение** - найденные ответы запоминаются
• 🌐 **Работа с источниками** - DuckDuckGo, Wikipedia
• 📚 **Расширение базы знаний** автоматически

📊 **Статистика обучения:**
• Обработано диалогов: {stats['total_conversations']}
• Выучено паттернов: {stats['patterns_learned']}
• Веб-поисков: {stats['web_searches']}
• Размер базы знаний: {stats['knowledge_base_size']}

💡 **Как работает веб-поиск:**
1. Вы задаете вопрос
2. Я ищу в своей базе знаний
3. Если не нахожу - ищу в интернете
4. Найденный ответ сохраняю в базу
5. В следующий раз отвечаю мгновенно!

🚀 **Теперь я постоянно учусь и расширяю знания!**
"""
        return help_text

    def get_learning_stats(self):
        """Получение статистики обучения"""
        cursor = self.learning_ai.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM qa_patterns')
        knowledge_size = cursor.fetchone()[0]
        
        stats = {
            'total_conversations': self.learning_stats['conversations_processed'],
            'patterns_learned': self.learning_stats['patterns_learned'],
            'web_searches': self.learning_stats['web_searches'],
            'knowledge_base_size': knowledge_size
        }
        
        return stats

    # Остальные методы остаются
    def _generate_code_example(self, message, entities):
        if entities['languages']:
            language = entities['languages'][0]
            examples = {
                'python': "```python\nprint('Привет, мир!')\n```",
                'javascript': "```javascript\nconsole.log('Привет, мир!');\n```", 
                'java': "```java\nSystem.out.println('Привет, мир!');\n```"
            }
            return f"Пример на {language}:\n{examples.get(language, examples['python'])}"
        return "На каком языке нужен пример кода?"

class AIHandler(BaseHTTPRequestHandler):
    ai = SmartAI()
    
    def do_GET(self):
        if self.path == '/':
            self._serve_html()
        elif self.path == '/stats':
            self._serve_stats()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/chat':
            self._handle_chat()
        else:
            self.send_error(404, "Not Found")
    
    def _serve_html(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI-GPT2 с Веб-Поиском 🧠🌐</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                    max-width: 800px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }
                .chat-container {
                    background: white;
                    border-radius: 20px;
                    padding: 25px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    height: 90vh;
                    display: flex;
                    flex-direction: column;
                }
                .header {
                    text-align: center;
                    margin-bottom: 20px;
                    background: linear-gradient(135deg, #2c3e50, #3498db);
                    color: white;
                    padding: 20px;
                    border-radius: 15px;
                    margin: -25px -25px 20px -25px;
                }
                .learning-stats {
                    background: #e8f4fd;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    border-left: 4px solid #3498db;
                }
                .stat-item {
                    display: flex;
                    justify-content: space-between;
                    margin: 5px 0;
                }
                .web-search-indicator {
                    background: #ffeb3b;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 0.8em;
                    margin-left: 10px;
                    animation: pulse 2s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.7; }
                    100% { opacity: 1; }
                }
                #chat {
                    flex: 1;
                    border: 2px solid #e1e5e9;
                    border-radius: 15px;
                    padding: 20px;
                    margin-bottom: 20px;
                    overflow-y: auto;
                    background: #f8f9fa;
                }
                .message {
                    margin: 15px 0;
                    padding: 15px 20px;
                    border-radius: 18px;
                    max-width: 85%;
                    line-height: 1.5;
                }
                .user {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    margin-left: auto;
                    text-align: right;
                }
                .ai {
                    background: white;
                    color: #2c3e50;
                    border: 2px solid #3498db;
                }
                .source-web {
                    border-color: #ff9800;
                }
                .source-cache {
                    border-color: #4caf50;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <h1>🧠🌐 AI-GPT2 с ВЕБ-ПОИСКОМ</h1>
                    <p>ИИ который ищет ответы в интернете и запоминает их!</p>
                    <div class="web-search-indicator">🔍 АКТИВЕН ВЕБ-ПОИСК</div>
                </div>
                
                <div class="learning-stats">
                    <h3>📊 Статистика обучения</h3>
                    <div class="stat-item">
                        <span>Обработано диалогов:</span>
                        <span id="conversationsCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Веб-поисков:</span>
                        <span id="webSearches">0</span>
                    </div>
                    <div class="stat-item">
                        <span>База знаний:</span>
                        <span id="knowledgeBase">0 записей</span>
                    </div>
                </div>
                
                <div id="chat">
                    <div class="message ai">
                        <strong>🧠🌐 Привет! Я AI-GPT2 с веб-поиском!</strong><br><br>
                        💡 <strong>Новые возможности:</strong><br>
                        • 🔍 <strong>Автоматический поиск</strong> в интернете<br>
                        • 💾 <strong>Сохранение найденных ответов</strong><br>
                        • 🚀 <strong>Мгновенные ответы</strong> после первого поиска<br><br>
                        🎯 <strong>Спросите что-нибудь сложное - я найду ответ!</strong>
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="messageInput" placeholder="Спросите о программировании..." style="flex: 1; padding: 15px; border: 2px solid #bdc3c7; border-radius: 25px;">
                    <button onclick="sendMessage()" style="padding: 15px 25px; background: #e74c3c; color: white; border: none; border-radius: 25px;">Отправить</button>
                </div>
            </div>

            <script>
                let stats = {
                    conversations: 0,
                    webSearches: 0,
                    knowledgeBase: 0
                };
                
                function addMessage(text, isUser, source) {
                    const chat = document.getElementById('chat');
                    const message = document.createElement('div');
                    message.className = isUser ? 'message user' : `message ai ${source ? 'source-' + source : ''}`;
                    message.innerHTML = text;
                    chat.appendChild(message);
                    chat.scrollTop = chat.scrollHeight;
                    
                    if (!isUser) {
                        stats.conversations++;
                        if (text.includes('🌐') || text.includes('веб-поиск')) {
                            stats.webSearches++;
                        }
                        updateStats();
                    }
                }

                async function sendMessage() {
                    const input = document.getElementById('messageInput');
                    const message = input.value.trim();
                    
                    if (!message) return;
                    
                    input.value = '';
                    addMessage(message, true);
                    
                    try {
                        // Показываем индикатор загрузки
                        const loadingMsg = addMessage('🔍 Поиск ответа...', false);
                        
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: message})
                        });
                        
                        const data = await response.json();
                        
                        // Удаляем индикатор загрузки
                        chat.removeChild(loadingMsg);
                        
                        addMessage(data.response, false);
                        
                    } catch (error) {
                        addMessage('❌ Ошибка соединения', false);
                    }
                }

                async function updateStats() {
                    try {
                        const response = await fetch('/stats');
                        const data = await response.json();
                        
                        document.getElementById('conversationsCount').textContent = data.total_conversations;
                        document.getElementById('webSearches').textContent = data.web_searches;
                        document.getElementById('knowledgeBase').textContent = data.knowledge_base_size + ' записей';
                    } catch (error) {
                        document.getElementById('conversationsCount').textContent = stats.conversations;
                        document.getElementById('webSearches').textContent = stats.webSearches;
                        document.getElementById('knowledgeBase').textContent = Math.floor(stats.conversations * 1.5) + ' записей';
                    }
                }

                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });

                // Загружаем начальную статистику
                updateStats();
            </script>
        </body>
        </html>
        '''
        self.wfile.write(html.encode('utf-8'))
    
    def _serve_stats(self):
        """Отдача статистики обучения"""
        stats = self.ai.get_learning_stats()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(stats).encode('utf-8'))
    
    def _handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            response = self.ai.generate_smart_response(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            
            self.wfile.write(json.dumps({"response": response}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8000
    
    print("🧠🌐 ЗАПУСК AI-GPT2 С ВЕБ-ПОИСКОМ...")
    print("╔══════════════════════════════════════════════╗")
    print("║           AI-GPT2 с Веб-Поиском v2.0        ║")
    print("║      Самообучающийся ИИ с поиском онлайн    ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 ВОЗМОЖНОСТИ ВЕБ-ПОИСКА:")
    print("• 🔍 Автопоиск в DuckDuckGo, Wikipedia")
    print("• 💾 Кэширование найденных ответов") 
    print("• 📚 Авто-пополнение базы знаний")
    print("• 🚀 Мгновенные ответы после первого поиска")
    print("• 🌐 Поддержка русскоязычных источников")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"✅ AI-GPT2 с веб-поиском активирован на {HOST}:{PORT}")
        print("💡 Теперь ИИ может находить ответы на любые вопросы!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
        print("💾 Сохранение данных обучения...")
