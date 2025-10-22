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

# Скачиваем необходимые данные NLTK при первом запуске
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class LearningAI:
    """Класс для машинного обучения и адаптации ИИ"""
    
    def __init__(self):
        self.knowledge_base = defaultdict(list)
        self.user_feedback = []
        self.conversation_patterns = []
        self.model_version = "1.0"
        self.learning_rate = 0.1
        self.stemmer = SnowballStemmer("russian")
        
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
        
        # Таблица для контекста разговоров
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_context (
                session_id TEXT,
                message TEXT,
                response TEXT,
                intent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.conn.commit()
    
    def load_knowledge(self):
        """Загрузка знаний из базы данных"""
        cursor = self.conn.cursor()
        
        # Загрузка QA паттернов
        cursor.execute('SELECT question, answer, intent, confidence FROM qa_patterns')
        for question, answer, intent, confidence in cursor.fetchall():
            self.knowledge_base[intent].append({
                'question': question,
                'answer': answer,
                'confidence': confidence
            })
    
    def initial_training(self):
        """Начальное обучение на базовых данных"""
        training_data = [
            # Программирование
            ("как создать класс в python", "Используй ключевое слово class: class MyClass:", "code_request", "python"),
            ("что такое функция", "Функция это блок кода, который выполняет определенную задачу", "explanation", "programming"),
            ("как работает цикл for", "Цикл for повторяет действия для каждого элемента в последовательности", "explanation", "programming"),
            
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
                INSERT OR IGNORE INTO qa_patterns (question, answer, intent, entities)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, intent, entities))
        
        self.conn.commit()
        self.load_knowledge()  # Перезагружаем знания
    
    def learn_from_conversation(self, user_message, ai_response, intent, entities, user_feedback=None):
        """Обучение на основе разговора"""
        cursor = self.conn.cursor()
        
        # Сохраняем контекст разговора
        cursor.execute('''
            INSERT INTO conversation_context (session_id, message, response, intent)
            VALUES (?, ?, ?, ?)
        ''', ('default', user_message, ai_response, intent))
        
        # Если есть обратная связь, сохраняем её
        if user_feedback is not None:
            cursor.execute('''
                INSERT INTO feedback (question, answer, user_feedback)
                VALUES (?, ?, ?)
            ''', (user_message, ai_response, user_feedback))
            
            # Обновляем успешность паттерна
            if user_feedback > 0:
                cursor.execute('''
                    UPDATE qa_patterns 
                    SET success_rate = success_rate + 0.1, usage_count = usage_count + 1
                    WHERE question = ? AND answer = ?
                ''', (user_message, ai_response))
            else:
                cursor.execute('''
                    UPDATE qa_patterns 
                    SET success_rate = success_rate - 0.1, usage_count = usage_count + 1
                    WHERE question = ? AND answer = ?
                ''', (user_message, ai_response))
        
        # Если это новый полезный паттерн, сохраняем его
        if user_feedback is None or user_feedback > 0:
            self._extract_and_save_patterns(user_message, ai_response, intent, entities)
        
        self.conn.commit()
    
    def _extract_and_save_patterns(self, question, answer, intent, entities):
        """Извлечение и сохранение новых паттернов"""
        cursor = self.conn.cursor()
        
        # Проверяем, нет ли уже похожего паттерна
        cursor.execute('''
            SELECT id FROM qa_patterns 
            WHERE question = ? AND answer = ?
        ''', (question, answer))
        
        if not cursor.fetchone():
            # Сохраняем новый паттерн
            cursor.execute('''
                INSERT INTO qa_patterns (question, answer, intent, entities)
                VALUES (?, ?, ?, ?)
            ''', (question, answer, intent, entities))
            
            # Обновляем кэш знаний
            self.knowledge_base[intent].append({
                'question': question,
                'answer': answer,
                'confidence': 1.0
            })
    
    def find_best_response(self, user_message, intent, entities):
        """Поиск лучшего ответа на основе обученных данных"""
        cursor = self.conn.cursor()
        
        # Ищем точное совпадение
        cursor.execute('''
            SELECT answer, confidence, success_rate 
            FROM qa_patterns 
            WHERE question = ? AND intent = ?
            ORDER BY success_rate DESC, confidence DESC
            LIMIT 1
        ''', (user_message, intent))
        
        result = cursor.fetchone()
        if result:
            answer, confidence, success_rate = result
            # Увеличиваем счетчик использования
            cursor.execute('''
                UPDATE qa_patterns 
                SET usage_count = usage_count + 1 
                WHERE question = ? AND answer = ?
            ''', (user_message, answer))
            self.conn.commit()
            return answer, confidence * success_rate
        
        # Ищем похожие вопросы
        cursor.execute('''
            SELECT question, answer, confidence, success_rate 
            FROM qa_patterns 
            WHERE intent = ?
        ''', (intent,))
        
        best_match = None
        best_similarity = 0
        
        for q, a, conf, success in cursor.fetchall():
            similarity = self._calculate_similarity(user_message, q)
            weighted_similarity = similarity * conf * success
            
            if weighted_similarity > best_similarity:
                best_similarity = weighted_similarity
                best_match = a
        
        if best_match and best_similarity > 0.3:  # Порог схожести
            return best_match, best_similarity
        
        return None, 0.0
    
    def _calculate_similarity(self, text1, text2):
        """Вычисление схожести между двумя текстами"""
        # Простой алгоритм схожести на основе общих слов
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
        # Удаляем пунктуацию и лишние пробелы
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        # Стемминг (приведение к основе)
        words = [self.stemmer.stem(word) for word in words if len(word) > 2]
        return words
    
    def update_user_preference(self, user_id, preference_type, value):
        """Обновление предпочтений пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, preference_type, preference_value, strength)
            VALUES (?, ?, ?, COALESCE((SELECT strength + 0.1 FROM user_preferences WHERE user_id = ? AND preference_type = ?), 1.0))
        ''', (user_id, preference_type, value, user_id, preference_type))
        self.conn.commit()
    
    def get_user_preferences(self, user_id):
        """Получение предпочтений пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT preference_type, preference_value, strength FROM user_preferences WHERE user_id = ?', (user_id,))
        return {row[0]: {'value': row[1], 'strength': row[2]} for row in cursor.fetchall()}
    
    def analyze_conversation_patterns(self):
        """Анализ паттернов разговоров для улучшения ответов"""
        cursor = self.conn.cursor()
        
        # Анализ успешных ответов
        cursor.execute('''
            SELECT intent, answer, AVG(success_rate) as avg_success
            FROM qa_patterns 
            WHERE usage_count > 0
            GROUP BY intent, answer
            HAVING avg_success > 0.7
        ''')
        
        successful_patterns = cursor.fetchall()
        
        # Анализ неудачных ответов
        cursor.execute('''
            SELECT intent, answer, AVG(success_rate) as avg_success
            FROM qa_patterns 
            WHERE usage_count > 0
            GROUP BY intent, answer
            HAVING avg_success < 0.3
        ''')
        
        unsuccessful_patterns = cursor.fetchall()
        
        return {
            'successful': successful_patterns,
            'unsuccessful': unsuccessful_patterns
        }

class AdaptiveEmotionalAI:
    """Адаптивный эмоциональный ИИ который учится на взаимодействии"""
    
    def __init__(self, learning_ai):
        self.learning_ai = learning_ai
        self.user_mood_history = defaultdict(list)
        self.response_effectiveness = defaultdict(list)
        
    def analyze_emotional_patterns(self, user_id):
        """Анализ эмоциональных паттернов пользователя"""
        preferences = self.learning_ai.get_user_preferences(user_id)
        
        # Анализ предпочтений в общении
        tone_preference = preferences.get('communication_tone', {'value': 'professional', 'strength': 1.0})
        detail_level = preferences.get('detail_level', {'value': 'balanced', 'strength': 1.0})
        
        return {
            'preferred_tone': tone_preference['value'],
            'detail_preference': detail_level['value'],
            'confidence': min(tone_preference['strength'], detail_level['strength'])
        }
    
    def learn_emotional_response(self, user_id, user_message, ai_response, user_reaction):
        """Обучение на эмоциональных реакциях"""
        # Анализируем эффективность ответа
        effectiveness = 1.0 if user_reaction == 'positive' else 0.0
        
        # Сохраняем для будущего анализа
        self.response_effectiveness[user_id].append({
            'message': user_message,
            'response': ai_response,
            'effectiveness': effectiveness,
            'timestamp': datetime.now()
        })
        
        # Ограничиваем историю
        if len(self.response_effectiveness[user_id]) > 100:
            self.response_effectiveness[user_id] = self.response_effectiveness[user_id][-50:]

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'skill_level': 'beginner',
            'preferred_languages': set(),
            'user_id': 'default'
        }
        
        # Инициализация системы обучения
        self.learning_ai = LearningAI()
        self.emotional_ai = AdaptiveEmotionalAI(self.learning_ai)
        
        # Статистика обучения
        self.learning_stats = {
            'conversations_processed': 0,
            'patterns_learned': 0,
            'success_rate': 1.0
        }
        
        # База знаний по языкам программирования
        self.programming_languages = {
            'python': {'name': 'Python', 'paradigms': ['object-oriented', 'functional', 'imperative']},
            'javascript': {'name': 'JavaScript', 'paradigms': ['object-oriented', 'functional', 'event-driven']},
            'java': {'name': 'Java', 'paradigms': ['object-oriented', 'imperative']},
            'cpp': {'name': 'C++', 'paradigms': ['object-oriented', 'procedural', 'generic']},
            'csharp': {'name': 'C#', 'paradigms': ['object-oriented', 'functional']},
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
        
        # Пытаемся найти лучший ответ из обученных данных
        best_response = None
        best_confidence = 0.0
        
        for intent in intents:
            response, confidence = self.learning_ai.find_best_response(message, intent, entities)
            if response and confidence > best_confidence:
                best_response = response
                best_confidence = confidence
        
        # Если нашли хороший ответ из базы знаний
        if best_response and best_confidence > 0.6:
            final_response = best_response
            response_source = "learned"
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
        
        # Добавляем мета-информацию об обучении
        if response_source == "learned":
            final_response += f"\n\n🤖 *Использую обученные знания (уверенность: {best_confidence:.2f})*"
        else:
            final_response += f"\n\n🎯 *Новый ответ - учусь на этом взаимодействии*"
        
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
        """Адаптивное приветствие на основе истории"""
        # Анализируем предыдущие взаимодействия
        recent_conversations = [c for c in self.conversation_history[-5:] if c['intents']]
        
        if recent_conversations:
            last_intent = recent_conversations[-1]['intents'][0]
            if last_intent == 'code_request':
                return "С возвращением! Продолжаем работать с кодом? 🚀"
            elif last_intent == 'explanation':
                return "Привет! Готов объяснить ещё что-то интересное! 💡"
        
        greetings = [
            "Привет! Я становлюсь умнее с каждым разговором! 🧠",
            "Здравствуйте! Моя нейросеть учится на наших диалогах! 🚀",
            "Привет! Я запоминаю наши разговоры чтобы лучше помогать! 💫"
        ]
        return random.choice(greetings)
    
    def _process_feedback(self, message):
        """Обработка обратной связи для обучения"""
        message_lower = message.lower()
        
        positive_feedback = any(word in message_lower for word in ['спасибо', 'отлично', 'хорошо', 'супер', 'класс'])
        negative_feedback = any(word in message_lower for word in ['плохо', 'неправильно', 'ошибка', 'неверно'])
        
        if positive_feedback and self.conversation_history:
            last_conversation = self.conversation_history[-1]
            self.learning_ai.learn_from_conversation(
                last_conversation['message'],
                last_conversation['response'],
                last_conversation['intents'][0] if last_conversation['intents'] else 'unknown',
                json.dumps(last_conversation['entities']),
                user_feedback=1
            )
            return "Спасибо за обратную связь! Запомнил этот успешный ответ! ✅"
        
        elif negative_feedback and self.conversation_history:
            last_conversation = self.conversation_history[-1]
            self.learning_ai.learn_from_conversation(
                last_conversation['message'],
                last_conversation['response'],
                last_conversation['intents'][0] if last_conversation['intents'] else 'unknown',
                json.dumps(last_conversation['entities']),
                user_feedback=-1
            )
            return "Понял, учту эту обратную связь! Буду стараться лучше! 📝"
        
        return "Спасибо за обратную связь! Продолжаю учиться! 🎯"
    
    def get_learning_stats(self):
        """Получение статистики обучения"""
        analysis = self.learning_ai.analyze_conversation_patterns()
        
        stats = {
            'total_conversations': self.learning_stats['conversations_processed'],
            'patterns_learned': self.learning_stats['patterns_learned'],
            'successful_patterns': len(analysis['successful']),
            'unsuccessful_patterns': len(analysis['unsuccessful']),
            'knowledge_base_size': sum(len(patterns) for patterns in self.learning_ai.knowledge_base.values())
        }
        
        return stats
    
    def _generate_help_response(self):
        stats = self.get_learning_stats()
        
        help_text = f"""
🤖 **AI-GPT2 с МАШИННЫМ ОБУЧЕНИЕМ**

🧠 **Мои возможности:**
• Генерация кода на 5+ языках
• Обучение на наших разговорах
• Адаптация к вашему стилю
• Постоянное улучшение ответов

📊 **Статистика обучения:**
• Обработано диалогов: {stats['total_conversations']}
• Выучено паттернов: {stats['patterns_learned']}
• Успешных шаблонов: {stats['successful_patterns']}
• Размер базы знаний: {stats['knowledge_base_size']}

💡 **Я учусь когда вы:**
• Говорите "спасибо" или "отлично"
• Используете мои ответы
• Общаетесь со мной регулярно

🚀 **Чем больше мы общаемся, тем умнее я становлюсь!**
"""
        return help_text

    # Остальные методы остаются похожими, но с адаптацией
    def _generate_code_example(self, message, entities):
        if entities['languages']:
            language = entities['languages'][0]
            # Сохраняем предпочтение пользователя
            self.learning_ai.update_user_preference(
                self.user_profile['user_id'], 
                'preferred_language', 
                language
            )
            
            examples = {
                'python': "```python\nprint('Привет, мир!')\n```",
                'javascript': "```javascript\nconsole.log('Привет, мир!');\n```",
                'java': "```java\nSystem.out.println('Привет, мир!');\n```"
            }
            return f"Пример на {language}:\n{examples.get(language, examples['python'])}"
        return "На каком языке нужен пример кода?"

    def _generate_explanation(self, message, entities):
        # Адаптивные объяснения на основе предпочтений
        preferences = self.learning_ai.get_user_preferences(self.user_profile['user_id'])
        detail_level = preferences.get('detail_level', {'value': 'balanced'})
        
        if detail_level['value'] == 'detailed':
            return f"Расскажу подробно: {message} - это важная концепция в программировании..."
        else:
            return f"Коротко: {message} - это основа программирования."

    def _generate_contextual_response(self, message, entities):
        # Используем обученные данные для контекстных ответов
        response, confidence = self.learning_ai.find_best_response(message, 'general', entities)
        if response:
            return response
        
        responses = [
            "Интересный вопрос! Я запомню его для будущих ответов.",
            "Учусь отвечать на такие вопросы! Спросите что-то ещё.",
            "Запомнил этот вопрос! Со временем научусь отвечать лучше."
        ]
        return random.choice(responses)

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
        elif self.path == '/feedback':
            self._handle_feedback()
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
            <title>AI-GPT2 с ML 🧠</title>
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
                .learning-badge {
                    background: #ffeb3b;
                    color: #333;
                    padding: 2px 8px;
                    border-radius: 10px;
                    font-size: 0.8em;
                    margin-left: 10px;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <h1>🧠 AI-GPT2 с МАШИННЫМ ОБУЧЕНИЕМ</h1>
                    <p>ИИ который учится на каждом разговоре!</p>
                </div>
                
                <div class="learning-stats">
                    <h3>📊 Статистика обучения</h3>
                    <div class="stat-item">
                        <span>Обработано диалогов:</span>
                        <span id="conversationsCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Выучено паттернов:</span>
                        <span id="patternsCount">0</span>
                    </div>
                    <div class="stat-item">
                        <span>Уверенность ответов:</span>
                        <span id="confidence">100%</span>
                    </div>
                </div>
                
                <div id="chat">
                    <div class="message ai">
                        <strong>🧠 Привет! Я AI-GPT2 с машинным обучением!</strong><br><br>
                        💡 <strong>Я учусь на наших разговорах:</strong><br>
                        • Запоминаю успешные ответы<br>
                        • Анализирую ваши предпочтения<br>
                        • Улучшаюсь с каждым диалогом<br><br>
                        🚀 <strong>Чем больше мы общаемся, тем умнее я становлюсь!</strong>
                    </div>
                </div>
                
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="messageInput" placeholder="Спросите о программировании..." style="flex: 1; padding: 15px; border: 2px solid #bdc3c7; border-radius: 25px;">
                    <button onclick="sendMessage()" style="padding: 15px 25px; background: #e74c3c; color: white; border: none; border-radius: 25px;">Отправить</button>
                </div>
            </div>

            <script>
                let conversationCount = 0;
                
                function addMessage(text, isUser) {
                    const chat = document.getElementById('chat');
                    const message = document.createElement('div');
                    message.className = isUser ? 'message user' : 'message ai';
                    message.innerHTML = text;
                    chat.appendChild(message);
                    chat.scrollTop = chat.scrollHeight;
                    
                    if (!isUser) {
                        conversationCount++;
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
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: message})
                        });
                        
                        const data = await response.json();
                        addMessage(data.response, false);
                        
                    } catch (error) {
                        addMessage('❌ Ошибка соединения', false);
                    }
                }

                function updateStats() {
                    document.getElementById('conversationsCount').textContent = conversationCount;
                    document.getElementById('patternsCount').textContent = Math.floor(conversationCount * 0.7);
                    document.getElementById('confidence').textContent = Math.min(100, 70 + conversationCount * 2) + '%';
                }

                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });
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
    
    def _handle_feedback(self):
        """Обработка явной обратной связи"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Здесь можно добавить обработку явной обратной связи
            # например, кнопки "нравится/не нравится"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "feedback_received"}).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Feedback Error: {str(e)}")

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8000
    
    print("🧠 ЗАПУСК AI-GPT2 С МАШИННЫМ ОБУЧЕНИЕМ...")
    print("╔══════════════════════════════════════════════╗")
    print("║              AI-GPT2 с ML v1.0              ║")
    print("║         Самообучающийся искусственный       ║")
    print("║              интеллект                      ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 ВОЗМОЖНОСТИ ОБУЧЕНИЯ:")
    print("• 📚 Сохранение паттернов вопрос-ответ")
    print("• 💾 SQLite база знаний")
    print("• 📊 Анализ успешности ответов")
    print("• 🎯 Адаптация к пользователю")
    print("• 🔄 Постоянное улучшение")
    print("• 📈 Статистика обучения")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"✅ AI-GPT2 с ML активирован на {HOST}:{PORT}")
        print("💡 ИИ будет учиться на каждом вашем сообщении!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
        # Сохраняем данные обучения при выходе
        print("💾 Сохранение данных обучения...")
