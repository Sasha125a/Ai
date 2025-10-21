from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import time

class SimpleAI:
    def __init__(self):
        self.knowledge = {
            "python": {
                "базовый": "Python - интерпретируемый язык с динамической типизацией. Простой синтаксис, мощные возможности.",
                "веб": "Для веба используйте Flask (простой) или Django (полноценный). FastAPI - современный фреймворк для API.",
                "данные": "Pandas для таблиц, NumPy для вычислений, Matplotlib для графиков. Идеален для анализа данных.",
                "синтаксис": "Отступы важны! 4 пробела. Функции: def, классы: class, условия: if/elif/else, циклы: for/while."
            },
            "javascript": {
                "базовый": "JavaScript - язык для веб-страниц. Запускается в браузере. Динамическая типизация.",
                "синтаксис": "Переменные: let/const, функции: function или стрелочные =>, объекты: {ключ: значение}",
                "веб": "React, Vue, Angular - популярные фреймворки. Node.js - JavaScript на сервере.",
                "асинхронность": "async/await для асинхронных операций. Промисы (Promise) для обработки асинхронности."
            },
            "html": {
                "базовый": "HTML - структура страницы. Теги: <div>, <p>, <h1>-<h6>, <a>, <img>, <form>",
                "семантика": "<header>, <nav>, <main>, <section>, <article>, <footer> - семантические теги",
                "формы": "<input>, <textarea>, <select>, <button> - элементы форм"
            },
            "css": {
                "базовый": "CSS - стилизация. Селекторы: .class, #id, tag. Свойства: color, font-size, margin, padding",
                "flexbox": "display: flex для гибких布局. justify-content, align-items, flex-direction",
                "grid": "display: grid для сеток. grid-template-columns, grid-gap, grid-area"
            },
            "ооп": {
                "принципы": "Инкапсуляция - скрытие данных. Наследование - расширение классов. Полиморфизм - разные реализации.",
                "классы": "Класс - шаблон для объектов. Объект - экземпляр класса. Методы - функции в классе.",
                "паттерны": "Singleton, Factory, Observer - популярные паттерны проектирования."
            },
            "алгоритмы": {
                "сложность": "O(1) - константная, O(n) - линейная, O(log n) - логарифмическая, O(n²) - квадратичная",
                "сортировка": "Быстрая сортировка (O(n log n)), сортировка слиянием, пузырьковая (O(n²))",
                "поиск": "Линейный поиск (O(n)), бинарный поиск (O(log n)) в отсортированном массиве"
            },
            "базы данных": {
                "sql": "Реляционные БД: MySQL, PostgreSQL. SQL запросы: SELECT, INSERT, UPDATE, DELETE, JOIN",
                "nosql": "Документные: MongoDB, ключ-значение: Redis, графовые: Neo4j",
                "нормализация": "Устранение избыточности данных. 1NF, 2NF, 3NF - нормальные формы"
            },
            "веб": {
                "frontend": "HTML + CSS + JavaScript. Фреймворки: React, Vue, Angular. Инструменты: Webpack, Vite",
                "backend": "Серверная логика. Python: Django, Flask. JavaScript: Node.js, Express. Java: Spring",
                "api": "REST API - стандартный подход. GraphQL - гибкие запросы. JSON - формат данных"
            },
            "мобильный": {
                "android": "Kotlin/Java, Android Studio. Архитектура: MVVM, Clean Architecture",
                "ios": "Swift, Xcode. Архитектура: MVC, MVVM, VIPER",
                "кроссплатформенный": "Flutter (Dart), React Native (JavaScript). Единая кодовая база для iOS и Android"
            },
            "git": {
                "базовый": "git init, git add, git commit, git push, git pull - основные команды",
                "ветвление": "git branch, git checkout, git merge - работа с ветками",
                "совместная": "git clone, git fetch, git rebase - для командной работы"
            }
        }
    
    def get_answer(self, question):
        question_lower = question.lower()
        
        # Ищем точное совпадение по ключевым словам
        for category, topics in self.knowledge.items():
            if category in question_lower:
                # Если нашли категорию, ищем подтему
                for topic, answer in topics.items():
                    if topic in question_lower:
                        return f"**{category.upper()} - {topic.upper()}:**\n\n{answer}"
                # Если не нашли подтему, возвращаем первую тему из категории
                first_topic = next(iter(topics.items()))
                return f"**{category.upper()}:**\n\n{first_topic[1]}"
        
        # Умные ответы на общие вопросы
        if any(word in question_lower for word in ['привет', 'здравствуй', 'hello', 'hi']):
            return "👋 Привет! Я ИИ помощник по программированию!\n\nЯ могу объяснить:\n• Python, JavaScript, HTML/CSS\n• Алгоритмы и структуры данных\n• Базы данных (SQL, NoSQL)\n• Веб и мобильную разработку\n• Git и инструменты разработки\n\nСпроси меня о чём угодно из мира программирования! 🚀"
        
        elif any(word in question_lower for word in ['помощь', 'help', 'что ты умеешь']):
            categories = "\n".join([f"• {cat}" for cat in self.knowledge.keys()])
            return f"🤖 **Что я умею:**\n\n{categories}\n\nПросто спроси о любой из этих тем, и я дам подробное объяснение!"
        
        elif any(word in question_lower for word in ['сгенерируй', 'напиши код', 'пример кода']):
            return self._generate_code(question)
        
        elif any(word in question_lower for word in ['спасибо', 'благодарю']):
            return "Пожалуйста! 😊 Рад был помочь. Если есть ещё вопросы - обращайся!"
        
        else:
            # Ищем частичные совпадения
            found_topics = []
            for category, topics in self.knowledge.items():
                if any(word in category for word in question_lower.split()):
                    found_topics.append(category)
                for topic in topics.keys():
                    if any(word in topic for word in question_lower.split()):
                        found_topics.append(f"{category} - {topic}")
            
            if found_topics:
                topics_list = "\n".join([f"• {topic}" for topic in found_topics[:3]])
                return f"💡 По вашему вопросу я могу рассказать:\n\n{topics_list}\n\nУточните, что именно вас интересует?"
            else:
                return "🤔 Интересный вопрос! Я ещё учусь, но могу помочь с:\n\n• Python, JavaScript, HTML/CSS\n• Алгоритмы и ООП\n• Базы данных\n• Веб и мобильная разработка\n• Git и инструменты\n\nПопробуй задать вопрос более конкретно! 💡"

    def _generate_code(self, question):
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['python', 'пайтон', 'питон']):
            return '''```python
# Пример класса Python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Привет, меня зовут {self.name}, мне {self.age} лет"
    
    def have_birthday(self):
        self.age += 1
        return f"Теперь мне {self.age} лет!"

# Использование
student = Student("Анна", 20)
print(student.greet())  # Привет, меня зовут Анна, мне 20 лет
print(student.have_birthday())  # Теперь мне 21 лет!
```'''
        
        elif any(word in question_lower for word in ['javascript', 'джаваскрипт', 'js']):
            return '''```javascript
// Пример класса JavaScript
class Student {
    constructor(name, age) {
        this.name = name;
        this.age = age;
    }
    
    greet() {
        return `Привет, меня зовут ${this.name}, мне ${this.age} лет`;
    }
    
    haveBirthday() {
        this.age += 1;
        return `Теперь мне ${this.age} лет!`;
    }
}

// Использование
const student = new Student("Анна", 20);
console.log(student.greet());  // Привет, меня зовут Анна, мне 20 лет
console.log(student.haveBirthday());  // Теперь мне 21 лет!
```'''
        
        elif any(word in question_lower for word in ['html', 'веб', 'страниц']):
            return '''```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Моя страница</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Привет, мир!</h1>
        <p>Это простая HTML страница</p>
        <button onclick="alert('Привет!')">Нажми меня</button>
    </div>
    
    <script>
        console.log("Страница загружена!");
    </script>
</body>
</html>
```'''
        
        else:
            return '''```python
# Универсальный пример кода
def process_data(data):
    """
    Обработка данных с проверкой ошибок
    """
    try:
        if not data:
            raise ValueError("Данные не могут быть пустыми")
        
        # Фильтрация и преобразование
        processed = [item * 2 for item in data if item > 0]
        
        # Возврат результата
        return {
            'original_length': len(data),
            'processed_length': len(processed),
            'result': processed,
            'average': sum(processed) / len(processed) if processed else 0
        }
        
    except Exception as e:
        return f"Ошибка обработки: {e}"

# Пример использования
data = [1, 2, 3, 4, 5]
result = process_data(data)
print(result)
```'''

class SimpleAIHandler(BaseHTTPRequestHandler):
    ai = SimpleAI()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            self._handle_chat()
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_chat(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            if not message:
                self._send_json_response({'error': 'Пустое сообщение'}, 400)
                return
            
            # Имитируем небольшую задержку для реалистичности
            time.sleep(0.5)
            
            # Получаем ответ от ИИ
            response = self.ai.get_answer(message)
            
            self._send_json_response({
                'response': response,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# Красивый HTML интерфейс
HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 ИИ Чат по Программированию</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 0;
        }

        .app {
            max-width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }

        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 25px 20px;
            text-align: center;
            box-shadow: 0 2px 20px rgba(0,0,0,0.2);
        }

        .header h1 {
            font-size: 1.6em;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .header p {
            opacity: 0.9;
            font-size: 1em;
            font-weight: 300;
        }

        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            background: #f8f9fa;
        }

        .message {
            max-width: 85%;
            padding: 16px 20px;
            border-radius: 20px;
            word-wrap: break-word;
            animation: fadeIn 0.4s ease;
            line-height: 1.5;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        @keyframes fadeIn {
            from { 
                opacity: 0; 
                transform: translateY(15px) scale(0.95); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0) scale(1); 
            }
        }

        .user-message {
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 8px;
        }

        .ai-message {
            background: white;
            color: #2c3e50;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 8px;
        }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 12px;
            align-items: flex-end;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        }

        .input-container {
            flex: 1;
            position: relative;
        }

        .input-area textarea {
            width: 100%;
            padding: 16px 60px 16px 20px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            resize: none;
            font-family: inherit;
            font-size: 16px;
            background: #f8f9fa;
            transition: all 0.3s;
            max-height: 120px;
            min-height: 60px;
            line-height: 1.4;
        }

        .input-area textarea:focus {
            outline: none;
            border-color: #007bff;
            background: white;
            box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
        }

        .send-btn {
            position: absolute;
            right: 8px;
            bottom: 8px;
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            border: none;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s;
            box-shadow: 0 2px 8px rgba(0,123,255,0.3);
        }

        .send-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,123,255,0.4);
        }

        .send-btn:active {
            transform: translateY(0);
        }

        .send-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 16px;
            border-radius: 10px;
            margin: 12px 0;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.4;
            overflow-x: auto;
            border-left: 4px solid #3498db;
        }

        .typing-indicator {
            display: none;
            padding: 16px 20px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 20px;
            border-bottom-left-radius: 8px;
            color: #666;
            font-style: italic;
            max-width: 85%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .typing-dots {
            display: inline-block;
        }

        .typing-dots::after {
            content: '...';
            animation: typing 1.5s infinite;
        }

        @keyframes typing {
            0%, 20% { content: '.'; }
            40% { content: '..'; }
            60%, 100% { content: '...'; }
        }

        .timestamp {
            font-size: 0.8em;
            opacity: 0.6;
            margin-top: 8px;
            text-align: right;
        }

        /* Мобильная оптимизация */
        @media (max-width: 480px) {
            .header {
                padding: 20px 15px;
            }
            
            .header h1 {
                font-size: 1.4em;
            }
            
            .messages {
                padding: 15px;
                gap: 12px;
            }
            
            .message {
                max-width: 90%;
                padding: 14px 18px;
                font-size: 15px;
            }
            
            .input-area {
                padding: 15px;
            }
            
            .input-area textarea {
                padding: 14px 55px 14px 18px;
                font-size: 15px;
            }
            
            .send-btn {
                width: 40px;
                height: 40px;
            }
        }

        /* Темная тема */
        @media (prefers-color-scheme: dark) {
            .app {
                background: #1a1a1a;
                color: white;
            }
            
            .messages {
                background: #2d2d2d;
            }
            
            .ai-message {
                background: #333;
                color: white;
                border-color: #444;
            }
            
            .input-area {
                background: #1a1a1a;
                border-color: #333;
            }
            
            .input-area textarea {
                background: #333;
                color: white;
                border-color: #444;
            }
            
            .input-area textarea:focus {
                background: #444;
                border-color: #007bff;
            }
            
            .code-block {
                background: #0d1117;
                border-left-color: #58a6ff;
            }
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <h1>💬 ИИ Чат по Программированию</h1>
            <p>Умный помощник для разработчиков</p>
        </div>

        <div class="messages" id="messages">
            <div class="message ai-message">
                <strong>👋 Привет, я твой ИИ помощник!</strong><br><br>
                Я знаю всё о:<br>
                • Python, JavaScript, HTML/CSS<br>
                • Алгоритмах и ООП<br>
                • Базах данных (SQL/NoSQL)<br>
                • Веб и мобильной разработке<br>
                • Git и инструментах<br><br>
                Просто спроси о чём угодно! 🚀
            </div>
        </div>

        <div class="input-area">
            <div class="input-container">
                <textarea id="messageInput" placeholder="Задайте вопрос о программировании..." rows="1"></textarea>
                <button class="send-btn" id="sendButton" onclick="sendMessage()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            ИИ думает над ответом<span class="typing-dots"></span>
        </div>
    </div>

    <script>
        let isProcessing = false;

        function addMessage(text, isUser = false) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            
            // Форматируем код блоки
            let formattedText = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<div class="code-block">$2</div>');
            
            // Форматируем переносы строк и жирный текст
            formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            formattedText = formattedText.replace(/\n/g, '<br>');
            
            // Добавляем timestamp для пользовательских сообщений
            if (isUser) {
                const timestamp = new Date().toLocaleTimeString('ru-RU', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                });
                formattedText += `<div class="timestamp">${timestamp}</div>`;
            }
            
            messageDiv.innerHTML = formattedText;
            messagesDiv.appendChild(messageDiv);
            
            // Плавная прокрутка вниз
            messagesDiv.scrollTo({
                top: messagesDiv.scrollHeight,
                behavior: 'smooth'
            });
        }

        function showTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            indicator.style.display = 'block';
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }

        function hideTypingIndicator() {
            document.getElementById('typingIndicator').style.display = 'none';
        }

        async function sendMessage() {
            if (isProcessing) return;
            
            const input = document.getElementById('messageInput');
            const button = document.getElementById('sendButton');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Блокируем кнопку и поле ввода
            isProcessing = true;
            button.disabled = true;
            input.disabled = true;
            
            // Очищаем поле ввода
            input.value = '';
            resetTextarea();
            
            // Добавляем сообщение пользователя
            addMessage(message, true);
            
            // Показываем индикатор набора
            showTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                hideTypingIndicator();
                
                if (data.error) {
                    addMessage(`❌ Ошибка: ${data.error}`);
                } else {
                    addMessage(data.response);
                }
                
            } catch (error) {
                hideTypingIndicator();
                addMessage('❌ Ошибка соединения. Проверьте интернет.');
            } finally {
                // Разблокируем кнопку и поле ввода
                isProcessing = false;
                button.disabled = false;
                input.disabled = false;
                input.focus();
            }
        }

        function resetTextarea() {
            const textarea = document.getElementById('messageInput');
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
        }

        // Автоматическое изменение высоты textarea
        document.getElementById('messageInput').addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });

        // Отправка по Enter (Shift+Enter для новой строки)
        document.getElementById('messageInput').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Фокус на поле ввода при загрузке
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
'''

def main():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleAIHandler)
    
    print(f"🚀 ИИ Чат по Программированию запущен!")
    print(f"📍 Откройте в браузере: http://localhost:{port}")
    print(f"📱 Идеально работает на телефонах")
    print("\n💡 Особенности:")
    print("• 🎯 Богатая база знаний по программированию")
    print("• 💬 Красивый и удобный интерфейс")
    print("• 📱 Полная адаптация под мобильные")
    print("• 🚀 Мгновенные ответы")
    print("• 💻 Генерация примеров кода")
    print("\nНажмите Ctrl+C для остановки сервера")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен. До свидания!")

if __name__ == '__main__':
    main()
