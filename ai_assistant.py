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
    """Упрощенная реализация текстовой схожести"""
    
    def __init__(self):
        pass
    
    def similarity(self, text1, text2):
        """Простая схожесть на основе общих слов"""
        words1 = set(self._preprocess(text1))
        words2 = set(self._preprocess(text2))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _preprocess(self, text):
        """Предобработка текста"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return [word for word in words if len(word) > 2]

class SimpleClassifier:
    """Простой классификатор на основе ключевых слов"""
    
    def __init__(self):
        self.patterns = {
            'greeting': ['привет', 'здравствуй', 'hello', 'hi', 'добрый'],
            'farewell': ['пока', 'до свидания', 'bye', 'прощай'],
            'help': ['помощь', 'help', 'что ты умеешь'],
            'explanation': ['объясни', 'расскажи', 'что такое', 'как работает'],
            'code_request': ['код', 'пример', 'напиши', 'покажи код'],
        }
    
    def predict(self, text):
        """Предсказание intent'а"""
        text_lower = text.lower()
        intents = []
        
        for intent, keywords in self.patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                intents.append(intent)
        
        return intents if intents else ['unknown']

class WebSearch:
    """Упрощенный веб-поиск"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_internet(self, query, max_results=2):
        """Поиск информации в интернете"""
        try:
            # DuckDuckGo API
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
            
            # Основной ответ
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'Ответ'),
                    'snippet': data.get('AbstractText'),
                    'source': 'DuckDuckGo'
                })
            
            return results[:max_results]
            
        except Exception as e:
            print(f"Ошибка поиска: {e}")
            return []

class LearningAI:
    """Упрощенная система обучения"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.similarity_engine = SimpleTextSimilarity()
        self.classifier = SimpleClassifier()
        self.web_search = WebSearch()
        
        self.init_knowledge_db()
        self.initial_training()
    
    def init_knowledge_db(self):
        """Инициализация простой базы знаний"""
        self.conn = sqlite3.connect(':memory:', check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qa_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                answer TEXT,
                intent TEXT
            )
        ''')
        self.conn.commit()
    
    def initial_training(self):
        """Начальное обучение"""
        training_data = [
            ("привет", "Привет! Я AI-помощник. Чем могу помочь?", "greeting"),
            ("пока", "До свидания! Возвращайтесь с вопросами.", "farewell"),
            ("помощь", "Я помогаю с программированием. Могу генерировать код и объяснять концепции.", "help"),
            ("что такое python", "Python - это язык программирования высокого уровня.", "explanation"),
        ]
        
        cursor = self.conn.cursor()
        for question, answer, intent in training_data:
            cursor.execute('INSERT INTO qa_patterns (question, answer, intent) VALUES (?, ?, ?)', 
                         (question, answer, intent))
        self.conn.commit()
    
    def find_best_response(self, user_message, use_web_search=True):
        """Поиск лучшего ответа"""
        cursor = self.conn.cursor()
        
        # Ищем точное совпадение
        cursor.execute('SELECT answer FROM qa_patterns WHERE question = ?', (user_message,))
        result = cursor.fetchone()
        if result:
            return result[0], 1.0, "database"
        
        # Ищем по intent'у
        intents = self.classifier.predict(user_message)
        if intents and intents[0] != 'unknown':
            cursor.execute('SELECT answer FROM qa_patterns WHERE intent = ? LIMIT 1', (intents[0],))
            result = cursor.fetchone()
            if result:
                return result[0], 0.8, "intent"
        
        # Веб-поиск
        if use_web_search:
            results = self.web_search.search_internet(user_message)
            if results:
                answer = f"🌐 {results[0]['title']}\n\n{results[0]['snippet']}\n\n📚 Источник: {results[0]['source']}"
                # Сохраняем в базу
                cursor.execute('INSERT INTO qa_patterns (question, answer, intent) VALUES (?, ?, ?)',
                             (user_message, answer, "web_search"))
                self.conn.commit()
                return answer, 0.7, "web_search"
        
        return "Извините, я пока не знаю ответ на этот вопрос. Попробуйте задать его по-другому.", 0.0, "unknown"

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.learning_ai = LearningAI()
    
    def generate_smart_response(self, message):
        """Генерация ответа"""
        response, confidence, source = self.learning_ai.find_best_response(message)
        
        # Добавляем информацию об источнике
        source_info = {
            "database": "💾 Из базы знаний",
            "intent": "🎯 На основе категории", 
            "web_search": "🌐 Найдено в интернете",
            "unknown": "🤖 Стандартный ответ"
        }
        
        final_response = f"{response}\n\n{source_info.get(source, '')}"
        
        # Сохраняем в историю
        self.conversation_history.append({
            'message': message,
            'response': final_response,
            'timestamp': datetime.now()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-10:]
        
        return final_response

class AIHandler(BaseHTTPRequestHandler):
    ai = SmartAI()
    
    def do_GET(self):
        if self.path == '/':
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
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px;
                        background: #f5f5f5;
                    }
                    .chat-container {
                        background: white;
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }
                    #chat {
                        height: 400px;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 10px;
                        overflow-y: auto;
                    }
                    .message {
                        margin: 10px 0;
                        padding: 10px;
                        border-radius: 5px;
                    }
                    .user {
                        background: #007bff;
                        color: white;
                        margin-left: 20%;
                    }
                    .ai {
                        background: #e9ecef;
                        margin-right: 20%;
                    }
                    input, button {
                        padding: 10px;
                        margin: 5px 0;
                    }
                    input {
                        width: 70%;
                        border: 1px solid #ddd;
                        border-radius: 5px;
                    }
                    button {
                        background: #28a745;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                </style>
            </head>
            <body>
                <div class="chat-container">
                    <h1>🧠 AI Assistant</h1>
                    <div id="chat">
                        <div class="message ai">
                            <strong>Привет! Я AI-помощник.</strong><br>
                            Задайте вопрос о программировании, и я постараюсь помочь!
                        </div>
                    </div>
                    <div>
                        <input type="text" id="messageInput" placeholder="Введите ваш вопрос...">
                        <button onclick="sendMessage()">Отправить</button>
                    </div>
                </div>

                <script>
                    function addMessage(text, isUser) {
                        const chat = document.getElementById('chat');
                        const message = document.createElement('div');
                        message.className = isUser ? 'message user' : 'message ai';
                        message.innerHTML = text;
                        chat.appendChild(message);
                        chat.scrollTop = chat.scrollHeight;
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
                            addMessage('Ошибка соединения', false);
                        }
                    }

                    document.getElementById('messageInput').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') sendMessage();
                    });
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/chat':
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
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        print(f"AI Assistant: {format % args}")

def main():
    PORT = int(os.environ.get('PORT', 8000))
    
    print(f"🚀 Запуск AI Assistant на порту {PORT}...")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), AIHandler)
        print(f"✅ AI Assistant запущен и готов к работе!")
        print(f"📍 Откройте http://localhost:{PORT} в браузере")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
