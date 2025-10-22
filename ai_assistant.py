from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

class AIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"🔍 GET запрос получен: {self.path}")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>ИИ Чат</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 600px; 
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
                        background: #fafafa;
                    }
                    .message {
                        margin: 10px 0;
                        padding: 10px;
                        border-radius: 10px;
                        max-width: 80%;
                    }
                    .user {
                        background: #007bff;
                        color: white;
                        margin-left: auto;
                        text-align: right;
                    }
                    .ai {
                        background: #e9ecef;
                        color: black;
                    }
                    .input-area {
                        display: flex;
                        gap: 10px;
                    }
                    #messageInput {
                        flex: 1;
                        padding: 12px;
                        border: 2px solid #ddd;
                        border-radius: 25px;
                        font-size: 16px;
                    }
                    #messageInput:focus {
                        outline: none;
                        border-color: #007bff;
                    }
                    button {
                        padding: 12px 24px;
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 25px;
                        cursor: pointer;
                        font-size: 16px;
                    }
                    button:hover {
                        background: #0056b3;
                    }
                    .status {
                        margin-top: 10px;
                        padding: 10px;
                        border-radius: 5px;
                        text-align: center;
                    }
                    .success { background: #d4edda; color: #155724; }
                    .error { background: #f8d7da; color: #721c24; }
                </style>
            </head>
            <body>
                <div class="chat-container">
                    <h1>💬 ИИ Чат по Программированию</h1>
                    
                    <div id="chat">
                        <div class="message ai">
                            <strong>🤖 ИИ помощник:</strong><br>
                            Привет! Я готов отвечать на вопросы о программировании.
                            Просто введите сообщение и нажмите Отправить!
                        </div>
                    </div>
                    
                    <div class="input-area">
                        <input type="text" id="messageInput" placeholder="Введите ваш вопрос...">
                        <button onclick="sendMessage()">Отправить</button>
                    </div>
                    
                    <div id="status"></div>
                </div>

                <script>
                    function showStatus(message, type) {
                        const status = document.getElementById('status');
                        status.innerHTML = '<div class="status ' + type + '">' + message + '</div>';
                        setTimeout(() => status.innerHTML = '', 3000);
                    }

                    function addMessage(text, isUser) {
                        const chat = document.getElementById('chat');
                        const message = document.createElement('div');
                        message.className = isUser ? 'message user' : 'message ai';
                        
                        if (isUser) {
                            message.innerHTML = '<strong>👤 Вы:</strong><br>' + text;
                        } else {
                            message.innerHTML = '<strong>🤖 ИИ:</strong><br>' + text;
                        }
                        
                        chat.appendChild(message);
                        chat.scrollTop = chat.scrollHeight;
                    }

                    async function sendMessage() {
                        const input = document.getElementById('messageInput');
                        const message = input.value.trim();
                        
                        if (!message) {
                            showStatus('Введите сообщение!', 'error');
                            return;
                        }
                        
                        // Очищаем поле ввода
                        input.value = '';
                        
                        // Показываем сообщение пользователя сразу
                        addMessage(message, true);
                        showStatus('Отправка сообщения...', 'success');
                        
                        try {
                            console.log('📤 Отправляю POST запрос на /chat');
                            
                            const response = await fetch('/chat', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({message: message})
                            });
                            
                            console.log('📨 Ответ получен, статус:', response.status);
                            
                            if (!response.ok) {
                                throw new Error('HTTP error ' + response.status);
                            }
                            
                            const data = await response.json();
                            console.log('📝 Данные ответа:', data);
                            
                            addMessage(data.response, false);
                            showStatus('Ответ получен!', 'success');
                            
                        } catch (error) {
                            console.error('❌ Ошибка:', error);
                            addMessage('❌ Ошибка соединения с сервером', false);
                            showStatus('Ошибка соединения', 'error');
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
                    
                    console.log('✅ Страница загружена, скрипт работает');
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        print(f"📨 POST запрос получен на: {self.path}")
        print(f"📋 Заголовки: {dict(self.headers)}")
        
        if self.path == '/chat':
            try:
                # Читаем данные
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                print(f"📊 Получено данных: {content_length} байт")
                
                data = json.loads(post_data.decode('utf-8'))
                message = data.get('message', '')
                
                print(f"💬 Получено сообщение: '{message}'")
                
                # Генерируем ответ
                response_text = self.generate_response(message)
                
                # Отправляем ответ
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                
                response_data = json.dumps({"response": response_text}, ensure_ascii=False)
                print(f"📤 Отправляю ответ: {response_data}")
                self.wfile.write(response_data.encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")
                self.send_error(500, f"Internal Server Error: {str(e)}")
        else:
            print(f"❌ Неизвестный путь: {self.path}")
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def generate_response(self, message):
        """Генерация ответа ИИ"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hello']):
            return "Привет! 👋 Я ИИ помощник по программированию. Спроси меня о Python, JavaScript, HTML, алгоритмах или других темах!"
        
        elif any(word in message_lower for word in ['python', 'питон']):
            return "Python - отличный язык для начинающих! 🐍\n• Простой синтаксис\n• Много библиотек\n• Подходит для веба, данных, AI\n• Отличное сообщество"
        
        elif any(word in message_lower for word in ['javascript', 'js']):
            return "JavaScript - язык для веб-страниц! 📜\n• Работает в браузере\n• Много фреймворков (React, Vue)\n• Можно использовать на сервере (Node.js)"
        
        elif any(word in message_lower for word in ['html']):
            return "HTML - структура веб-страниц! 🌐\n• Теги: <div>, <p>, <h1>\n• Семантика важна\n• Основа веб-разработки"
        
        elif any(word in message_lower for word in ['помощь', 'help']):
            return "Я могу помочь с:\n• Python, JavaScript, HTML/CSS\n• Алгоритмы и структуры данных\n• Веб-разработка\n• Инструменты разработчика\n\nПросто спроси о конкретной теме! 💡"
        
        else:
            return f"Вы спросили: '{message}'\n\nЯ ещё учусь, но могу рассказать о:\n• Языках программирования\n• Веб-разработке\n• Алгоритмах\n• Инструментах\n\nПопробуйте задать вопрос по-другому! 🚀"
    
    def log_message(self, format, *args):
        """Кастомное логирование"""
        print(f"🌐 {format % args}")

if __name__ == '__main__':
    HOST = '0.0.0.0'  # Теперь слушаем все интерфейсы
    PORT = 8000
    
    print("🚀 Запуск ИИ Чата...")
    print(f"📍 Сервер будет доступен по адресам:")
    print(f"   • http://localhost:{PORT}")
    print(f"   • http://127.0.0.1:{PORT}")
    print(f"   • http://ваш-ip-адрес:{PORT}")
    print("\n📋 Инструкция:")
    print("1. Откройте любой браузер")
    print("2. Введите адрес: http://localhost:8000")
    print("3. Введите сообщение и нажмите 'Отправить'")
    print("4. Смотрите логи в этой консоли")
    print("\"Нажмите Ctrl+C для остановки\"")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"\n✅ Сервер запущен на {HOST}:{PORT}")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        print("Возможно, порт 8000 уже занят. Попробуйте другой порт:")
        print("python app.py 8080")
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
