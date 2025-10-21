from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime
import threading

class SimpleAI:
    def __init__(self):
        self.knowledge = {
            "python": "Python - простой и мощный язык. Используйте его для веб-разработки, анализа данных и автоматизации.",
            "javascript": "JavaScript - язык для веб-страниц. Работает в браузере и на сервере (Node.js).",
            "html": "HTML - структура страницы. CSS - стили. JavaScript - поведение.",
            "ооп": "ООП - Объектно-Ориентированное Программирование. Основные принципы: инкапсуляция, наследование, полиморфизм.",
            "алгоритм": "Алгоритм - последовательность шагов для решения задачи. Важна эффективность (сложность O(n)).",
            "база данных": "Базы данных хранят информацию. SQL - реляционные (MySQL, PostgreSQL), NoSQL - документные (MongoDB).",
            "веб": "Веб-разработка: frontend (интерфейс) и backend (логика). Популярные технологии: React, Vue, Django, Flask.",
            "мобильный": "Мобильная разработка: нативная (Kotlin/Java для Android, Swift для iOS) и кроссплатформенная (Flutter, React Native)."
        }
    
    def get_answer(self, question):
        question_lower = question.lower()
        
        # Поиск по ключевым словам
        for keyword, answer in self.knowledge.items():
            if keyword in question_lower:
                return answer
        
        # Умные ответы на общие вопросы
        if any(word in question_lower for word in ['привет', 'здравствуй', 'hello']):
            return "Привет! Я простой ИИ помощник по программированию. Спроси меня о Python, JavaScript, веб-разработке или других темах! 🚀"
        
        elif any(word in question_lower for word in ['помощь', 'help', 'что ты умеешь']):
            return "Я могу объяснить:\n• Основы программирования\n• Языки (Python, JavaScript)\n• Веб-разработку\n• Базы данных\n• Алгоритмы\n\nПросто спроси о чём-нибудь!"
        
        elif any(word in question_lower for word in ['сгенерируй', 'напиши код']):
            return self._generate_code(question)
        
        else:
            return "Интересный вопрос! Я ещё учусь, но могу помочь с темами: Python, JavaScript, веб-разработка, базы данных, алгоритмы. Попробуй задать вопрос по-другому! 💡"

    def _generate_code(self, question):
        if 'python' in question.lower():
            return '''```python
# Простой пример Python
def greet(name):
    return f"Привет, {name}!"

# Использование
result = greet("Мир")
print(result)  # Вывод: Привет, Мир!
```'''
        elif 'javascript' in question.lower():
            return '''```javascript
// Простой пример JavaScript
function greet(name) {
    return `Привет, ${name}!`;
}

// Использование
const result = greet("Мир");
console.log(result);  // Вывод: Привет, Мир!
```'''
        else:
            return '''```python
# Пример кода на Python
numbers = [1, 2, 3, 4, 5]

# Удвоить каждое число
doubled = [x * 2 for x in numbers]
print(doubled)  # [2, 4, 6, 8, 10]

# Фильтровать чётные
even = [x for x in numbers if x % 2 == 0]
print(even)  # [2, 4]
```'''

class SimpleAIHandler(BaseHTTPRequestHandler):
    ai = SimpleAI()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(SIMPLE_HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self._handle_chat(post_data)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_chat(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            if not message:
                self._send_json_response({'error': 'Пустое сообщение'}, 400)
                return
            
            # Обрабатываем в отдельном потоке
            def process_message():
                response = self.ai.get_answer(message)
                self._send_json_response({
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
            
            thread = threading.Thread(target=process_message)
            thread.daemon = True
            thread.start()
            
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

# Простой и чистый HTML интерфейс
SIMPLE_HTML = '''
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
        }

        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .header h1 {
            font-size: 1.4em;
            margin-bottom: 5px;
        }

        .header p {
            opacity: 0.8;
            font-size: 0.9em;
        }

        .messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: #f8f9fa;
        }

        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 6px;
        }

        .ai-message {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 6px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .input-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
            align-items: flex-end;
        }

        .input-container {
            flex: 1;
            position: relative;
        }

        .input-area textarea {
            width: 100%;
            padding: 12px 50px 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            resize: none;
            font-family: inherit;
            font-size: 16px;
            background: #f8f9fa;
            transition: border-color 0.3s;
            max-height: 120px;
            min-height: 50px;
        }

        .input-area textarea:focus {
            outline: none;
            border-color: #007bff;
            background: white;
        }

        .send-btn {
            position: absolute;
            right: 8px;
            bottom: 8px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.3s;
        }

        .send-btn:hover {
            background: #0056b3;
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 12px;
            border-radius: 8px;
            margin-top: 8px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            font-size: 14px;
            line-height: 1.4;
            overflow-x: auto;
        }

        .quick-questions {
            padding: 15px;
            background: #f8f9fa;
            border-top: 1px solid #e0e0e0;
        }

        .quick-questions h3 {
            margin-bottom: 10px;
            font-size: 0.9em;
            color: #666;
            text-align: center;
        }

        .quick-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }

        .quick-btn {
            background: white;
            color: #007bff;
            border: 1px solid #007bff;
            padding: 10px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
            text-align: center;
        }

        .quick-btn:hover {
            background: #007bff;
            color: white;
        }

        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            border-bottom-left-radius: 6px;
            color: #666;
            font-style: italic;
            max-width: 85%;
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

        /* Мобильная оптимизация */
        @media (max-width: 480px) {
            .header {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 1.2em;
            }
            
            .messages {
                padding: 10px;
                gap: 10px;
            }
            
            .message {
                max-width: 90%;
                padding: 10px 14px;
                font-size: 14px;
            }
            
            .input-area {
                padding: 10px;
            }
            
            .quick-questions {
                padding: 10px;
            }
            
            .quick-buttons {
                grid-template-columns: 1fr;
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
            
            .input-area textarea {
                background: #333;
                color: white;
                border-color: #444;
            }
            
            .input-area textarea:focus {
                background: #444;
            }
            
            .quick-questions {
                background: #2d2d2d;
            }
            
            .quick-btn {
                background: #333;
                color: #4dabf7;
                border-color: #4dabf7;
            }
            
            .quick-btn:hover {
                background: #4dabf7;
                color: white;
            }
        }
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <h1>💬 ИИ Чат по Программированию</h1>
            <p>Простой помощник для вопросов о коде</p>
        </div>

        <div class="messages" id="messages">
            <div class="message ai-message">
                Привет! 👋 Я простой ИИ помощник по программированию.<br><br>
                Могу объяснить основы Python, JavaScript, веб-разработки, алгоритмов и многое другое.<br><br>
                Просто спроси или нажми на быстрые вопросы ниже!
            </div>
        </div>

        <div class="quick-questions">
            <h3>Быстрые вопросы:</h3>
            <div class="quick-buttons">
                <button class="quick-btn" onclick="askQuestion('Что такое Python?')">🐍 Про Python</button>
                <button class="quick-btn" onclick="askQuestion('Объясни ООП')">🎯 Про ООП</button>
                <button class="quick-btn" onclick="askQuestion('Что такое JavaScript?')">📜 Про JavaScript</button>
                <button class="quick-btn" onclick="askQuestion('Сгенерируй пример кода')">💻 Пример кода</button>
            </div>
        </div>

        <div class="input-area">
            <div class="input-container">
                <textarea id="messageInput" placeholder="Задайте вопрос о программировании..." rows="1"></textarea>
                <button class="send-btn" onclick="sendMessage()">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                    </svg>
                </button>
            </div>
        </div>

        <div class="typing-indicator" id="typingIndicator">
            ИИ печатает<span class="typing-dots"></span>
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
            formattedText = formattedText.replace(/\n/g, '<br>');
            
            messageDiv.innerHTML = formattedText;
            messagesDiv.appendChild(messageDiv);
            
            // Прокрутка вниз
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
            const message = input.value.trim();
            
            if (!message) return;
            
            // Очищаем поле ввода
            input.value = '';
            resetTextarea();
            
            // Добавляем сообщение пользователя
            addMessage(message, true);
            
            // Показываем индикатор набора
            showTypingIndicator();
            isProcessing = true;
            
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
                isProcessing = false;
                
                if (data.error) {
                    addMessage(`❌ Ошибка: ${data.error}`);
                } else {
                    addMessage(data.response);
                }
                
            } catch (error) {
                hideTypingIndicator();
                isProcessing = false;
                addMessage('❌ Ошибка соединения. Проверьте интернет.');
            }
        }

        function askQuestion(question) {
            document.getElementById('messageInput').value = question;
            sendMessage();
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

        // Обработка свайпов (для мобильных)
        let startY;
        const messagesDiv = document.getElementById('messages');

        messagesDiv.addEventListener('touchstart', (e) => {
            startY = e.touches[0].clientY;
        });

        messagesDiv.addEventListener('touchmove', (e) => {
            const currentY = e.touches[0].clientY;
            if (startY - currentY > 50) { // Свайп вверх
                document.getElementById('messageInput').focus();
            }
        });
    </script>
</body>
</html>
'''

def main():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), SimpleAIHandler)
    
    print(f"💬 Простой ИИ Чат запущен!")
    print(f"📍 Откройте в браузере: http://localhost:{port}")
    print(f"📱 Оптимизирован для мобильных устройств")
    print("\n⚡ Особенности:")
    print("• 🎯 Простой и понятный интерфейс")
    print("• 📱 Идеально для телефонов")
    print("• 💬 Умные ответы о программировании")
    print("• 🚀 Быстрая работа")
    print("\nНажмите Ctrl+C для остановки")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Чат остановлен. До свидания!")

if __name__ == '__main__':
    main()
