from flask import Flask, request, jsonify
import json
from datetime import datetime
import time

app = Flask(__name__)

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
            "ооп": {
                "принципы": "Инкапсуляция - скрытие данных. Наследование - расширение классов. Полиморфизм - разные реализации.",
                "классы": "Класс - шаблон для объектов. Объект - экземпляр класса. Методы - функции в классе."
            },
            "алгоритмы": {
                "сложность": "O(1) - константная, O(n) - линейная, O(log n) - логарифмическая, O(n²) - квадратичная",
                "сортировка": "Быстрая сортировка (O(n log n)), сортировка слиянием, пузырьковая (O(n²))"
            }
        }
    
    def get_answer(self, question):
        question_lower = question.lower()
        
        # Приветствие
        if any(word in question_lower for word in ['привет', 'здравствуй', 'hello', 'hi']):
            return "👋 Привет! Я ИИ помощник по программированию!\n\nЗадавайте вопросы о Python, JavaScript, HTML, алгоритмах или ООП!"
        
        # Помощь
        elif any(word in question_lower for word in ['помощь', 'help', 'что ты умеешь']):
            return "🤖 Я могу объяснить:\n• Python (базовый, веб, данные)\n• JavaScript и веб-разработку\n• HTML и вёрстку\n• Алгоритмы и ООП\n• И многое другое!"
        
        # Поиск в знаниях
        for category, topics in self.knowledge.items():
            if category in question_lower:
                for topic, answer in topics.items():
                    if topic in question_lower:
                        return f"**{category.upper()} - {topic.upper()}:**\n\n{answer}"
        
        # Генерация кода
        if any(word in question_lower for word in ['сгенерируй', 'напиши код', 'пример кода']):
            if 'python' in question_lower:
                return '''```python
# Пример класса Python
class Student:
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Привет, я {self.name}!"

# Использование
student = Student("Анна")
print(student.greet())
```'''
            else:
                return '''```python
# Простой пример Python
numbers = [1, 2, 3, 4, 5]
squares = [x*x for x in numbers]
print(squares)  # [1, 4, 9, 16, 25]
```'''
        
        # Общий ответ
        return "🤔 Интересный вопрос! Попробуйте спросить о:\n• Python или JavaScript\n• HTML или вёрстке\n• Алгоритмах или ООП\n• Или попросите пример кода!"

ai = SimpleAI()

@app.route('/')
def home():
    return '''
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 100%;
            max-width: 400px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            border-radius: 20px 20px 0 0;
            text-align: center;
        }
        .messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
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
            background: #f1f3f4;
            color: #333;
            border-bottom-left-radius: 5px;
        }
        .input-area {
            padding: 15px;
            display: flex;
            gap: 10px;
            border-top: 1px solid #eee;
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
        .typing {
            color: #666;
            font-style: italic;
            padding: 10px;
        }
        .code-block {
            background: #2c3e50;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin: 5px 0;
            font-family: monospace;
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h2>💬 ИИ Чат</h2>
            <p>Помощник по программированию</p>
        </div>
        
        <div class="messages" id="messages">
            <div class="message ai-message">
                👋 Привет! Спроси меня о программировании!
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Введите вопрос...">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>

    <script>
        function addMessage(text, isUser = false) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = isUser ? 'user-message' : 'ai-message';
            
            // Форматируем код
            let formattedText = text;
            if (text.includes('```')) {
                formattedText = text.replace(/```(\w+)?\\n([\\s\\S]*?)```/g, '<div class="code-block">$2</div>');
            }
            formattedText = formattedText.replace(/\n/g, '<br>');
            
            messageDiv.innerHTML = formattedText;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Очищаем поле
            input.value = '';
            
            // Показываем сообщение пользователя
            addMessage(message, true);
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                if (data.response) {
                    addMessage(data.response);
                } else {
                    addMessage('Ошибка: ' + (data.error || 'неизвестная ошибка'));
                }
                
            } catch (error) {
                addMessage('❌ Ошибка соединения');
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

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Пустое сообщение'})
        
        # Получаем ответ от ИИ
        response = ai.get_answer(message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    print("🚀 ИИ Чат запускается...")
    print("📱 Откройте: http://localhost:5000")
    print("💬 Просто введите вопрос и нажмите Отправить!")
    app.run(host='0.0.0.0', port=5000, debug=False)
