from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

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
            self.wfile.write(HTML.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                if not message:
                    self._send_json_response({'error': 'Пустое сообщение'}, 400)
                    return
                
                # Обрабатываем сообщение сразу
                response = self.ai.get_answer(message)
                self._send_json_response({
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                self._send_json_response({'error': str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

# Упрощенный HTML
HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💬 ИИ Чат</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #f0f2f5;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
        }

        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }

        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .ai-message {
            background: white;
            color: #333;
            border: 1px solid #ddd;
            border-bottom-left-radius: 5px;
        }

        .input-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }

        #messageInput {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }

        #messageInput:focus {
            border-color: #007bff;
        }

        button {
            background: #007bff;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }

        button:hover {
            background: #0056b3;
        }

        .code-block {
            background: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-top: 5px;
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 ИИ Чат по Программированию</h1>
    </div>

    <div class="messages" id="messages">
        <div class="message ai-message">
            Привет! Задайте вопрос о программировании.
        </div>
    </div>

    <div class="input-area">
        <input type="text" id="messageInput" placeholder="Введите ваш вопрос...">
        <button onclick="sendMessage()">Отправить</button>
    </div>

    <script>
        function addMessage(text, isUser = false) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'user-message' : 'ai-message';
            
            // Форматируем код
            let formattedText = text;
            if (text.includes('```')) {
                formattedText = text.replace(/```(\w+)?\\n([\\s\\S]*?)```/g, '$2');
                formattedText = formattedText.replace(/\n/g, '<br>');
                formattedText = formattedText.replace(/(```[\\s\\S]*?```)/g, '<div class="code-block">$1</div>');
            } else {
                formattedText = text.replace(/\n/g, '<br>');
            }
            
            messageDiv.innerHTML = formattedText;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Очищаем поле ввода
            input.value = '';
            
            // Показываем сообщение пользователя сразу
            addMessage(message, true);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    addMessage('Ошибка: ' + data.error);
                } else {
                    addMessage(data.response);
                }
                
            } catch (error) {
                addMessage('Ошибка соединения');
            }
        }

        // Отправка по Enter
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // Фокус на поле ввода
        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
'''

def main():
    port = 8000
    server = HTTPServer(('localhost', port), SimpleAIHandler)
    
    print(f"🚀 ИИ Чат запущен!")
    print(f"📱 Откройте: http://localhost:{port}")
    print("💬 Просто введите вопрос и нажмите Отправить")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")

if __name__ == '__main__':
    main()
