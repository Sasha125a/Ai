from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class AIHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        print(f"🔍 GET запрос получен: {self.path}")
        
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>ИИ Чат</title>
                <style>
                    body { font-family: Arial; margin: 20px; }
                    .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .user { background: blue; color: white; }
                    .ai { background: gray; color: white; }
                    input, button { padding: 10px; margin: 5px; }
                </style>
            </head>
            <body>
                <h1>💬 Тестовый ИИ Чат</h1>
                <div id="chat"></div>
                <input type="text" id="message" placeholder="Введите сообщение">
                <button onclick="sendMessage()">ОТПРАВИТЬ</button>
                
                <script>
                    function sendMessage() {
                        const input = document.getElementById('message');
                        const message = input.value;
                        console.log('📤 Отправляю сообщение:', message);
                        
                        // Показываем сообщение сразу
                        const chat = document.getElementById('chat');
                        chat.innerHTML += '<div class="message user">Вы: ' + message + '</div>';
                        input.value = '';
                        
                        // Отправляем на сервер
                        fetch('/chat', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({message: message})
                        })
                        .then(response => {
                            console.log('📨 Ответ получен, статус:', response.status);
                            return response.json();
                        })
                        .then(data => {
                            console.log('📝 Данные ответа:', data);
                            chat.innerHTML += '<div class="message ai">ИИ: ' + data.response + '</div>';
                        })
                        .catch(error => {
                            console.error('❌ Ошибка:', error);
                            chat.innerHTML += '<div class="message ai">Ошибка соединения</div>';
                        });
                    }
                    
                    // Отправка по Enter
                    document.getElementById('message').addEventListener('keypress', function(e) {
                        if (e.key === 'Enter') sendMessage();
                    });
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        print(f"📨 POST запрос получен: {self.path}")
        
        if self.path == '/chat':
            try:
                # Читаем данные
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())
                message = data.get('message', '')
                
                print(f"💬 Получено сообщение: '{message}'")
                
                # Простой ответ
                response_text = f"Привет! Вы написали: '{message}'. Я работаю!"
                
                # Отправляем ответ
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = json.dumps({"response": response_text})
                print(f"📤 Отправляю ответ: {response_data}")
                self.wfile.write(response_data.encode())
                
            except Exception as e:
                print(f"❌ Ошибка обработки: {e}")
                self.send_error(500, "Internal Server Error")
        else:
            self.send_error(404, "Not Found")
    
    def log_message(self, format, *args):
        # Отключаем стандартное логирование
        pass

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), AIHandler)
    print(f"🚀 Сервер запущен на http://localhost:{port}")
    print("🔍 Откройте эту ссылку в браузере")
    print("💬 Введите сообщение и нажмите ОТПРАВИТЬ")
    print("📊 В консоли Python будут видны все запросы")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
