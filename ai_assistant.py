from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
import os
import sqlite3
from datetime import datetime
import requests
import urllib.parse
import nltk
import ssl
import math
from collections import defaultdict, Counter

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

class SimpleTextSimilarity:
    """Упрощенная реализация TF-IDF и косинусного сходства"""
    
    def __init__(self):
        self.vocab = set()
        self.doc_freq = defaultdict(int)
        self.documents = []
        self.stemmer = nltk.stem.SnowballStemmer("russian")
    
    def fit(self, documents):
        """Обучение на документах"""
        self.documents = documents
        self.vocab = set()
        
        # Строим словарь и частоты документов
        for doc in documents:
            words = self._preprocess_text(doc)
            self.vocab.update(words)
            for word in set(words):
                self.doc_freq[word] += 1
    
    def _preprocess_text(self, text):
        """Предобработка текста"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        words = [self.stemmer.stem(word) for word in words if len(word) > 2]
        return words
    
    def tfidf_vector(self, text):
        """Вычисление TF-IDF вектора для текста"""
        words = self._preprocess_text(text)
        word_count = Counter(words)
        total_words = len(words)
        
        vector = {}
        for word in self.vocab:
            if word in word_count:
                # TF (Term Frequency)
                tf = word_count[word] / total_words
                # IDF (Inverse Document Frequency)
                idf = math.log(len(self.documents) / (1 + self.doc_freq[word]))
                vector[word] = tf * idf
            else:
                vector[word] = 0.0
        
        return vector
    
    def cosine_similarity(self, vec1, vec2):
        """Вычисление косинусного сходства между двумя векторами"""
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in self.vocab)
        norm1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        norm2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_most_similar(self, query, documents):
        """Нахождение наиболее похожего документа"""
        query_vec = self.tfidf_vector(query)
        similarities = []
        
        for i, doc in enumerate(documents):
            doc_vec = self.tfidf_vector(doc)
            similarity = self.cosine_similarity(query_vec, doc_vec)
            similarities.append((similarity, i))
        
        similarities.sort(reverse=True)
        return similarities[0] if similarities else (0.0, -1)

class SimpleClassifier:
    """Простой классификатор на основе ключевых слов"""
    
    def __init__(self):
        self.patterns = {
            'greeting': ['привет', 'здравствуй', 'hello', 'hi', 'добрый', 'здравствуйте'],
            'farewell': ['пока', 'до свидания', 'bye', 'прощай', 'до встречи'],
            'help': ['помощь', 'help', 'что ты умеешь', 'функции'],
            'explanation': ['объясни', 'расскажи', 'что такое', 'как работает', 'означает'],
            'code_request': ['код', 'пример', 'напиши', 'сгенерируй', 'покажи код'],
            'comparison': ['разница', 'сравни', 'что лучше', 'отличие', 'отличия'],
            'problem': ['проблема', 'ошибка', 'не работает', 'помоги решить', 'исправить'],
            'opinion': ['мнение', 'думаешь', 'считаешь', 'точка зрения'],
            'learning_path': ['с чего начать', 'как учить', 'путь обучения', 'изучение'],
            'feedback': ['отлично', 'плохо', 'спасибо', 'неправильно', 'хорошо'],
            'create_code': ['создай', 'придумай', 'новый класс', 'сгенерируй класс', 'напиши класс']
        }
    
    def predict(self, text):
        """Предсказание intent'а текста"""
        text_lower = text.lower()
        scores = defaultdict(int)
        
        for intent, keywords in self.patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[intent] += 1
        
        if scores:
            best_intent = max(scores.items(), key=lambda x: x[1])
            return [best_intent[0]] if best_intent[1] > 0 else []
        
        return []

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

class CodeGenerator:
    """Класс для генерации кода с нуля"""
    
    def __init__(self):
        self.syntax_templates = {
            'python': self._python_syntax,
            'javascript': self._javascript_syntax,
            'java': self._java_syntax,
        }
    
    def _python_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для Python"""
        templates = {
            'class': f"class {name}:\n    def __init__(self{params or ''}):\n        pass",
            'function': f"def {name}({params or 'self'}):\n    pass",
            'method': f"def {name}(self{params or ''}):\n    pass",
        }
        return templates.get(element_type, '')
    
    def _javascript_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для JavaScript"""
        templates = {
            'class': f"class {name} {{\n    constructor({params or ''}) {{\n    }}\n}}",
            'function': f"function {name}({params or ''}) {{\n}}",
            'method': f"{name}({params or ''}) {{\n}}",
        }
        return templates.get(element_type, '')
    
    def _java_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для Java"""
        templates = {
            'class': f"public class {name} {{\n    public {name}({params or ''}) {{\n    }}\n}}",
            'method': f"public void {name}({params or ''}) {{\n}}",
        }
        return templates.get(element_type, '')
    
    def generate_method_logic(self, method_name, language, context):
        """Генерация логики для методов"""
        method_lower = method_name.lower()
        
        logic_templates = {
            'python': {
                'get': "return self.{}",
                'set': "self.{} = {}",
                'validate': "return isinstance({}, str) and len({}) > 0",
                'calculate': "return {} * {}",
            },
            'javascript': {
                'get': "return this.{};",
                'set': "this.{} = {};",
                'validate': "return typeof {} === 'string' && {}.length > 0;",
            }
        }
        
        for prefix, logic in logic_templates.get(language, {}).items():
            if prefix in method_lower:
                field = method_lower.replace(prefix, '').strip('_')
                if field:
                    return logic.format(field, 'value')
        
        return "pass" if language == 'python' else "{}"

class LearningAI:
    """Класс для машинного обучения и адаптации ИИ"""
    
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.model_version = "1.0"
        self.stemmer = nltk.stem.SnowballStemmer("russian")
        self.web_search = WebSearch()
        self.classifier = SimpleClassifier()
        self.similarity_engine = SimpleTextSimilarity()
        self.code_generator = CodeGenerator()
        
        # Инициализация базы данных для хранения знаний
        self.init_knowledge_db()
        
        # Загрузка существующих знаний
        self.load_knowledge()
        
        # Обучение на начальных данных
        self.initial_training()
    
    def init_knowledge_db(self):
        """Инициализация базы данных SQLite для хранения знаний"""
        # Используем файловую базу вместо in-memory для сохранения данных
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
                source TEXT DEFAULT 'manual',
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
        
        self.conn.commit()
    
    def load_knowledge(self):
        """Загрузка знаний из базы данных"""
        cursor = self.conn.cursor()
        
        # Загрузка QA паттернов
        cursor.execute('SELECT question, answer, intent, confidence, source FROM qa_patterns')
        questions = []
        for question, answer, intent, confidence, source in cursor.fetchall():
            self.knowledge_base[intent].append({
                'question': question,
                'answer': answer,
                'confidence': confidence,
                'source': source
            })
            questions.append(question)
        
        # Обучаем similarity engine на вопросах
        if questions:
            self.similarity_engine.fit(questions)
    
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
    
    def analyze_intent(self, message):
        """Анализ intent'а сообщения"""
        return self.classifier.predict(message)
    
    def _parse_code_requirements(self, message):
        """Парсинг требований для генерации кода"""
        requirements = {
            'class_name': 'CustomClass',
            'attributes': [],
            'methods': [],
            'purpose': 'general',
            'language': 'python',
        }
        
        message_lower = message.lower()
        
        # Извлечение названия класса
        class_patterns = [
            r'класс\s+(\w+)',
            r'class\s+(\w+)',
            r'создай\s+класс\s+(\w+)',
        ]
        
        for pattern in class_patterns:
            match = re.search(pattern, message_lower)
            if match:
                requirements['class_name'] = match.group(1).capitalize()
                break
        
        # Извлечение атрибутов
        attribute_patterns = [
            r'атрибут[а-я]*\s+(\w+)',
            r'поле\s+(\w+)',
            r'свойств[а-я]*\s+(\w+)',
        ]
        
        for pattern in attribute_patterns:
            match = re.search(pattern, message_lower)
            if match:
                attrs_text = match.group(1)
                attrs = re.split(r'[,\s]+', attrs_text)
                requirements['attributes'].extend([attr.strip() for attr in attrs if attr.strip()])
        
        # Определение языка
        for lang in ['python', 'javascript', 'java']:
            if lang in message_lower:
                requirements['language'] = lang
                break
        
        return requirements
    
    def _generate_python_from_scratch(self, requirements):
        """Генерация Python кода с нуля"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['name', 'value']
        
        code = f"# Сгенерированный класс {class_name}\n"
        code += f"class {class_name}:\n"
        
        # Конструктор
        init_params = ", ".join([f"{attr}=None" for attr in attributes])
        code += f"    def __init__(self, {init_params}):\n"
        for attr in attributes:
            code += f"        self._{attr} = {attr}\n"
        
        # Геттеры и сеттеры
        for attr in attributes:
            code += f"\n    @property\n"
            code += f"    def {attr}(self):\n"
            code += f"        return self._{attr}\n"
            code += f"\n    @{attr}.setter\n"
            code += f"    def {attr}(self, value):\n"
            code += f"        self._{attr} = value\n"
        
        code += f"\n    def __str__(self):\n"
        code += f"        return f\"{class_name}({', '.join([f'{attr}={{self._{attr}}}' for attr in attributes])})\"\n"
        
        return f"```python\n{code}\n```"
    
    def search_and_learn(self, user_message, intent, entities):
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
        query = user_message
        
        # Добавляем контекст программирования
        programming_keywords = ["программирование", "код", "python", "javascript", "java"]
        
        if intent in ['explanation', 'code_request']:
            if not any(keyword in user_message.lower() for keyword in programming_keywords):
                query = f"{user_message} программирование"
        
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
        
        return response
    
    def _clean_web_snippet(self, snippet, original_question):
        """Очистка и улучшение веб-сниппета"""
        cleaned = re.sub(r'\s+', ' ', snippet).strip()
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        if len(cleaned) > 500:
            cleaned = cleaned[:500] + '...'
        
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
        for result in search_results[:2]:
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
        
        # Если это запрос на создание кода
        if 'create_code' in intent:
            requirements = self._parse_code_requirements(user_message)
            generated_code = self._generate_python_from_scratch(requirements)
            
            response = f"🚀 **Сгенерирован новый код!**\n\n"
            response += f"📋 **Анализ запроса:**\n"
            response += f"• Класс: `{requirements['class_name']}`\n"
            response += f"• Язык: `{requirements['language']}`\n"
            if requirements['attributes']:
                response += f"• Атрибуты: {', '.join(requirements['attributes'])}\n"
            
            response += f"\n💻 **Сгенерированный код:**\n{generated_code}"
            return response, 0.9, "code_generation"
        
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
            if confidence * success_rate > 0.5:
                cursor.execute('''
                    UPDATE qa_patterns 
                    SET usage_count = usage_count + 1 
                    WHERE question = ? AND answer = ?
                ''', (user_message, answer))
                self.conn.commit()
                return answer, confidence * success_rate, source
        
        # Ищем похожие вопросы используя нашу similarity engine
        cursor.execute('''
            SELECT question, answer, confidence, success_rate, source
            FROM qa_patterns 
            WHERE intent = ?
        ''', (intent,))
        
        all_questions = []
        qa_pairs = []
        
        for q, a, conf, success, source in cursor.fetchall():
            all_questions.append(q)
            qa_pairs.append((q, a, conf, success, source))
        
        if all_questions and qa_pairs:
            # Используем нашу similarity engine для поиска похожих вопросов
            similarity, index = self.similarity_engine.find_most_similar(user_message, all_questions)
            if similarity > 0.3 and index != -1:
                best_q, best_a, conf, success, source = qa_pairs[index]
                return best_a, similarity * conf * success, source
        
        # Если не нашли в базе и разрешен веб-поиск
        if use_web_search and intent in ['explanation', 'code_request', 'learning_path']:
            web_answer, web_source = self.search_and_learn(user_message, intent, entities)
            if web_answer:
                return web_answer, 0.7, web_source
        
        return None, 0.0, None

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
        }
        
        self.programming_languages = {
            'python': {'name': 'Python', 'paradigms': ['object-oriented', 'functional', 'imperative']},
            'javascript': {'name': 'JavaScript', 'paradigms': ['object-oriented', 'functional', 'event-driven']},
            'java': {'name': 'Java', 'paradigms': ['object-oriented', 'imperative']},
        }
    
    def analyze_intent(self, message):
        return self.learning_ai.analyze_intent(message)
    
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
        else:
            # Генерируем новый ответ
            final_response = self._craft_response(message, intents, entities)
            response_source = "generated"
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
            "generated": "🎯",
            "code_generation": "🚀"
        }
        
        final_response += f"\n\n{source_emoji.get(response_source, '🤖')} *Источник: {response_source}*"
        
        return final_response
    
    def _craft_response(self, message, intents, entities):
        """Генерация ответа на основе intent'ов"""
        if not intents:
            return "Не совсем понял вопрос. Можете переформулировать? 🤔"
        
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
            "👋 Привет! Я AI-GPT2 - ИИ с веб-поиском и генерацией кода!",
            "🚀 Здравствуйте! Готов создавать код и искать ответы в интернете!",
            "💫 Привет! Моя база знаний пополняется из интернета автоматически!"
        ]
        return random.choice(greetings)
    
    def _generate_help_response(self):
        stats = self.get_learning_stats()
        
        help_text = f"""
🤖 **AI-GPT2 с ВЕБ-ПОИСКОМ и ГЕНЕРАЦИЕЙ КОДА**

🚀 **Мои возможности:**
• 🔍 **Автопоиск в интернете** (DuckDuckGo, Wikipedia)
• 💻 **Генерация кода** с нуля на Python/JavaScript/Java
• 💾 **Авто-сохранение** найденных ответов
• 📚 **Расширение базы знаний** автоматически

🎯 **Примеры запросов:**
• "Создай класс Car с атрибутами brand, model, year"
• "Что такое паттерн синглтон в программировании?"
• "Покажи пример кода на Python"

📊 **Статистика:**
• Обработано диалогов: {stats['total_conversations']}
• Веб-поисков: {stats['web_searches']}
• База знаний: {stats['knowledge_base_size']} записей
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

    def _generate_code_example(self, message, entities):
        if entities['languages']:
            language = entities['languages'][0]
            examples = {
                'python': "```python\n# Пример класса\nclass Example:\n    def __init__(self, name):\n        self.name = name\n    \n    def greet(self):\n        print(f'Привет, {self.name}!')\n\n# Использование\nobj = Example('Мир')\nobj.greet()\n```",
                'javascript': "```javascript\n// Пример класса\nclass Example {\n    constructor(name) {\n        this.name = name;\n    }\n    \n    greet() {\n        console.log(`Привет, ${this.name}!`);\n    }\n}\n\n// Использование\nconst obj = new Example('Мир');\nobj.greet();\n```", 
                'java': "```java\n// Пример класса\npublic class Example {\n    private String name;\n    \n    public Example(String name) {\n        this.name = name;\n    }\n    \n    public void greet() {\n        System.out.println(\"Привет, \" + name + \"!\");\n    }\n    \n    public static void main(String[] args) {\n        Example obj = new Example(\"Мир\");\n        obj.greet();\n    }\n}\n```"
            }
            return f"**Пример на {language}:**\n{examples.get(language, examples['python'])}"
        return "На каком языке программирования нужен пример кода? 💻"

    def _generate_explanation(self, message, entities):
        return f"По вашему запросу '{message}' я пока не нашел точного ответа в базе. Попробую найти информацию в интернете при следующем запросе! 🔍"

    def _process_feedback(self, message):
        return "Спасибо за обратную связь! Продолжаю учиться и улучшать ответы! 📝"

    def _generate_contextual_response(self, message, entities):
        responses = [
            "Интересный вопрос! Я запомню его для будущих ответов.",
            "Учусь отвечать на такие вопросы! Спросите что-то ещё.",
            "Запомнил этот вопрос! Со временем научусь отвечать лучше."
        ]
        return random.choice(responses)

    def _generate_farewell(self):
        farewells = [
            "👋 До свидания! Возвращайтесь с новыми вопросами!",
            "🚀 Пока! Удачи в программировании!",
            "💫 До встречи! Не забывайте, я учусь на наших разговорах!"
        ]
        return random.choice(farewells)

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
            <title>AI Assistant</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                
                .chat-container {
                    width: 100%;
                    max-width: 800px;
                    height: 90vh;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                }
                
                .chat-header {
                    background: linear-gradient(135deg, #2c3e50, #3498db);
                    color: white;
                    padding: 20px;
                    text-align: center;
                }
                
                .chat-header h1 {
                    font-size: 1.5em;
                    margin-bottom: 5px;
                }
                
                .chat-header p {
                    opacity: 0.9;
                    font-size: 0.9em;
                }
                
                .chat-messages {
                    flex: 1;
                    padding: 20px;
                    overflow-y: auto;
                    background: #f8f9fa;
                }
                
                .message {
                    margin: 10px 0;
                    padding: 12px 16px;
                    border-radius: 18px;
                    max-width: 80%;
                    line-height: 1.4;
                    animation: fadeIn 0.3s ease;
                }
                
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .user-message {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    margin-left: auto;
                    border-bottom-right-radius: 5px;
                }
                
                .ai-message {
                    background: white;
                    color: #333;
                    border: 2px solid #e9ecef;
                    border-bottom-left-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }
                
                .message-time {
                    font-size: 0.7em;
                    opacity: 0.7;
                    margin-top: 5px;
                    text-align: right;
                }
                
                .chat-input-container {
                    padding: 20px;
                    background: white;
                    border-top: 1px solid #e9ecef;
                    display: flex;
                    gap: 10px;
                }
                
                .chat-input {
                    flex: 1;
                    padding: 12px 16px;
                    border: 2px solid #e9ecef;
                    border-radius: 25px;
                    font-size: 14px;
                    outline: none;
                    transition: border-color 0.3s;
                }
                
                .chat-input:focus {
                    border-color: #3498db;
                }
                
                .send-button {
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                
                .send-button:hover {
                    transform: translateY(-1px);
                }
                
                .send-button:active {
                    transform: translateY(0);
                }
                
                .typing-indicator {
                    display: none;
                    padding: 12px 16px;
                    background: white;
                    border: 2px solid #e9ecef;
                    border-radius: 18px;
                    border-bottom-left-radius: 5px;
                    max-width: 80px;
                    margin: 10px 0;
                }
                
                .typing-dots {
                    display: flex;
                    gap: 4px;
                }
                
                .typing-dot {
                    width: 8px;
                    height: 8px;
                    background: #999;
                    border-radius: 50%;
                    animation: typing 1.4s infinite;
                }
                
                .typing-dot:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .typing-dot:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                @keyframes typing {
                    0%, 60%, 100% {
                        transform: translateY(0);
                        opacity: 0.4;
                    }
                    30% {
                        transform: translateY(-5px);
                        opacity: 1;
                    }
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
                
                /* Scrollbar styling */
                .chat-messages::-webkit-scrollbar {
                    width: 6px;
                }
                
                .chat-messages::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 3px;
                }
                
                .chat-messages::-webkit-scrollbar-thumb {
                    background: #c1c1c1;
                    border-radius: 3px;
                }
                
                .chat-messages::-webkit-scrollbar-thumb:hover {
                    background: #a8a8a8;
                }
                
                /* Mobile responsiveness */
                @media (max-width: 768px) {
                    .chat-container {
                        height: 100vh;
                        border-radius: 0;
                    }
                    
                    .message {
                        max-width: 90%;
                    }
                    
                    .chat-header {
                        padding: 15px;
                    }
                    
                    .chat-header h1 {
                        font-size: 1.3em;
                    }
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <h1>🧠 AI Assistant</h1>
                    <p>Задайте вопрос о программировании</p>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai-message">
                        <strong>Привет! Я ваш AI-помощник 🤖</strong><br><br>
                        Я могу:<br>
                        • 🔍 Искать информацию в интернете<br>
                        • 💻 Генерировать код на Python/JavaScript/Java<br>
                        • 📚 Объяснять концепции программирования<br><br>
                        Просто задайте вопрос!
                    </div>
                </div>
                
                <div class="typing-indicator" id="typingIndicator">
                    <div class="typing-dots">
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                        <div class="typing-dot"></div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <input type="text" class="chat-input" id="messageInput" placeholder="Введите ваше сообщение..." autocomplete="off">
                    <button class="send-button" onclick="sendMessage()">Отправить</button>
                </div>
            </div>

            <script>
                const chatMessages = document.getElementById('chatMessages');
                const messageInput = document.getElementById('messageInput');
                const typingIndicator = document.getElementById('typingIndicator');
                
                function addMessage(text, isUser) {
                    const messageDiv = document.createElement('div');
                    messageDiv.className = isUser ? 'message user-message' : 'message ai-message';
                    
                    // Format text with code blocks
                    let formattedText = text;
                    if (text.includes('```')) {
                        formattedText = text.replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, '<div class="code-block">$2</div>');
                    }
                    formattedText = formattedText.replace(/\\n/g, '<br>');
                    
                    const time = new Date().toLocaleTimeString('ru-RU', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                    });
                    
                    messageDiv.innerHTML = `${formattedText}<div class="message-time">${time}</div>`;
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                function showTyping() {
                    typingIndicator.style.display = 'block';
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                function hideTyping() {
                    typingIndicator.style.display = 'none';
                }
                
                async function sendMessage() {
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Clear input
                    messageInput.value = '';
                    
                    // Add user message
                    addMessage(message, true);
                    
                    // Show typing indicator
                    showTyping();
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ message: message })
                        });
                        
                        const data = await response.json();
                        
                        // Hide typing indicator
                        hideTyping();
                        
                        // Add AI response
                        addMessage(data.response, false);
                        
                    } catch (error) {
                        hideTyping();
                        addMessage('❌ Ошибка соединения с сервером', false);
                        console.error('Error:', error);
                    }
                }
                
                // Send message on Enter key
                messageInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        sendMessage();
                    }
                });
                
                // Focus input on load
                messageInput.focus();
                
                // Auto-scroll to bottom on load
                chatMessages.scrollTop = chatMessages.scrollHeight;
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
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({"response": response}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
    
    def log_message(self, format, *args):
        print(f"AI Assistant: {format % args}")

def main():
    PORT = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Запуск AI-GPT2 с веб-поиском на порту {PORT}...")
    print("╔══════════════════════════════════════════════╗")
    print("║           AI-GPT2 с Веб-Поиском v2.0        ║")
    print("║      Самообучающийся ИИ с поиском онлайн    ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 ВОЗМОЖНОСТИ:")
    print("• 🔍 Автопоиск в DuckDuckGo, Wikipedia")
    print("• 💻 Генерация кода на 3 языках") 
    print("• 💾 Кэширование найденных ответов")
    print("• 📚 Авто-пополнение базы знаний")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), AIHandler)
        print(f"✅ AI-GPT2 с веб-поиском активирован на порту {PORT}")
        print("💡 Теперь ИИ может находить ответы на любые вопросы!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
        print("💾 Сохранение данных обучения...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
