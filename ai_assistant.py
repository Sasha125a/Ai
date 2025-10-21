import http.server
import socketserver
import json
import urllib.parse

class SimpleAI:
    def get_answer(self, question):
        question = question.lower()
        
        if "привет" in question:
            return "Привет! Я ИИ помощник. Спроси меня о программировании!"
        elif "python" in question:
            return "Python - отличный язык для начинающих! Простой синтаксис, много возможностей."
        elif "javascript" in question:
            return "JavaScript - язык для веб-страниц. Работает в браузере."
        elif "html" in question:
            return "HTML - структура страницы. CSS - стили. JavaScript - поведение."
        else:
            return "Интересный вопрос! Я могу рассказать о Python, JavaScript, HTML, CSS и многом другом."

class AIHandler(http.server.SimpleHTTPRequestHandler):
    ai = SimpleAI()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            response = self.ai.get_answer(message)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps({'response': response}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ИИ Чат</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f0f0f0;
        }
        .chat-container {
            max-width: 400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .messages {
            height: 300px;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 10px;
            margin-bottom: 10px;
            overflow-y: auto;
        }
        .message {
            margin: 5px 0;
            padding: 8px;
            border-radius: 5px;
        }
        .user-message {
            background: #007bff;
            color: white;
            text-align: right;
        }
        .ai-message {
            background: #f8f9fa;
            color: black;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2>💬 ИИ Чат</h2>
        <div class="messages" id="messages">
            <div class="message ai-message">Привет! Спроси меня о программировании.</div>
        </div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Введите сообщение...">
            <button onclick="sendMessage()">Отправить</button>
        </div>
    </div>

    <script>
        function addMessage(text, isUser) {
            const messages = document.getElementById('messages');
            const message = document.createElement('div');
            message.className = isUser ? 'message user-message' : 'message ai-message';
            message.textContent = text;
            messages.appendChild(message);
            messages.scrollTop = messages.scrollHeight;
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
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({message: message})
                });
                
                const data = await response.json();
                addMessage(data.response, false);
                
            } catch (error) {
                addMessage('Ошибка отправки', false);
            }
        }

        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        document.getElementById('messageInput').focus();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = 8000
    with socketserver.TCPServer(("", port), AIHandler) as httpd:
        print(f"🚀 Сервер запущен на http://localhost:{port}")
        print("💬 Откройте эту ссылку в браузере")
        print("📝 Введите сообщение и нажмите Отправить")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
