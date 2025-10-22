def min_max(numbers):
    return min(numbers), max(numbers)

minimum, maximum = min_max([3, 1, 4, 1, 5, 9, 2])
print(f"Min: {minimum}, Max: {maximum}")
```"""

    def _provide_problem_solving_advice(self, user_message, keywords):
        """Советы по решению проблем"""
        advice = [
            "**Шаги решения проблемы:**\n1. Четко определите проблему\n2. Разбейте на меньшие части\n3. Ищите похожие решения\n4. Тестируйте постепенно\n5. Анализируйте ошибки",
            
            "**При отладке кода:**\n• Используйте print() для отслеживания значений\n• Проверяйте типы данных переменных\n• Убедитесь в правильности условий\n• Тестируйте边界 случаи (edge cases)",
            
            "**Распространенные причины ошибок:**\n• Опечатки в именах переменных\n• Неправильные отступы (в Python)\n• Несоответствие типов данных\n• Выход за границы массивов\n• Бесконечные циклы"
        ]
        
        return random.choice(advice) + "\n\nМожете описать вашу проблему подробнее?"

    def _generate_smart_fallback(self, user_message, intent, entities):
        """Умный fallback вместо простого 'не понял'"""
        
        # Анализируем запрос для более релевантного ответа
        if len(user_message.split()) > 5:  # Длинный запрос - вероятно, сложный вопрос
            responses = [
                "Интересный вопрос! Я пока не сталкивался с таким, но обязательно изучу эту тему. 📚",
                "Сложный вопрос! Я сохраню его для дальнейшего обучения. Можете переформулировать или задать более конкретный вопрос? 💭",
                "Понял ваш запрос! К сожалению, у меня пока недостаточно информации по этой теме. Хотите, чтобы я поискал в интернете? 🔍"
            ]
        else:
            responses = [
                "Хм, не совсем понял вопрос. Можете переформулировать или задать более конкретно? 🤔",
                "Интересно! Можете подробнее описать, что вас интересует? 💡",
                "Я еще учусь отвечать на такие вопросы. Можете задать его по-другому? 🧠"
            ]
        
        # Добавляем предложение помощи
        fallback = random.choice(responses)
        return f"{fallback}\n\nПопробуйте задать вопрос о:\n• Концепциях программирования\n• Примеры кода\n• Решении конкретных проблем\n• Сравнении технологий"

    def _generate_class_name(self, user_message):
        """Генерация имени класса на основе запроса"""
        # Извлекаем существительные из запроса для имени класса
        words = [word for word in user_message.split() if len(word) > 3]
        if words:
            return words[0].capitalize()
        return "MyClass"
    
    def _web_search_and_save(self, user_message, intent, entities):
        """Поиск в интернете и сохранение в базу знаний"""
        try:
            search_results = self.web_search.search_internet(user_message)
            if search_results:
                best_result = search_results[0]
                answer = f"🌐 **{best_result['title']}**\n\n{best_result['snippet']}\n\n📚 *Источник: {best_result['source']}*"
                
                # Сохраняем в базу знаний
                tags = self._extract_tags_from_query(user_message)
                self.knowledge_base.add_entry(
                    category="web_knowledge",
                    question=user_message,
                    answer=answer,
                    intent=intent,
                    tags=tags,
                    confidence=0.8
                )
                
                return answer, "web_search"
        except Exception as e:
            print(f"❌ Ошибка веб-поиска: {e}")
        
        return None, None
    
    def _extract_tags_from_query(self, query):
        """Извлечение тегов из запроса"""
        words = re.findall(r'\b[a-zа-я]{3,}\b', query.lower())
        stop_words = {'это', 'как', 'что', 'для', 'или', 'если', 'так', 'но', 'на', 'в', 'с'}
        return [word for word in words if word not in stop_words]
    
    def get_knowledge_stats(self):
        """Получение статистики знаний"""
        return self.knowledge_base.get_statistics()
    
    def export_knowledge(self):
        """Экспорт базы знаний"""
        return self.knowledge_base.export_to_file()

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.learning_ai = EnhancedLearningAI()
        self.learning_stats = {
            'conversations_processed': 0,
            'knowledge_base_entries': 0,
            'web_searches': 0,
        }
    
    def generate_smart_response(self, message):
        intents = self.learning_ai.classifier.predict(message)
        entities = self.extract_entities(message)
        
        primary_intent = intents[0] if intents else "unknown"
        
        best_response, confidence, source = self.learning_ai.find_best_response(
            message, primary_intent, entities
        )
        
        if best_response:
            final_response = best_response
            if source == "web_search":
                self.learning_stats['web_searches'] += 1
        else:
            final_response = self._generate_fallback_response(message, intents, entities)
            source = "generated"
        
        # Обновляем статистику
        self.learning_stats['conversations_processed'] += 1
        self.learning_stats['knowledge_base_entries'] = (
            self.learning_ai.get_knowledge_stats()["total_entries"]
        )
        
        # Сохраняем в историю
        self.conversation_history.append({
            'message': message,
            'response': final_response,
            'source': source,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-20:]
        
        # Добавляем информацию об источнике
        source_info = {
            "knowledge_base": "💾 Из базы знаний",
            "web_search": "🌐 Найдено в интернете", 
            "generated": "🤖 Сгенерированный ответ"
        }
        
        final_response += f"\n\n{source_info.get(source, '')}"
        
        return final_response
    
    def extract_entities(self, message):
        """Простое извлечение сущностей"""
        entities = {'languages': []}
        languages = ['python', 'javascript', 'java', 'html', 'css']
        for lang in languages:
            if lang in message.lower():
                entities['languages'].append(lang)
        return entities
    
    def _generate_fallback_response(self, message, intents, entities):
        """Генерация ответа, когда не нашли в базе"""
        if 'greeting' in intents:
            return "Привет! Чем могу помочь с программированием? 🤖"
        elif 'farewell' in intents:
            return "До свидания! Возвращайтесь с вопросами! 👋"
        elif 'help' in intents:
            return "Я помогаю с программированием. Могу объяснить концепции, показать примеры кода или найти информацию в интернете. 💡"
        
        # Более осмысленные ответы для неизвестных вопросов
        responses = [
            "Интересный вопрос! Я изучаю новые темы и скоро смогу лучше отвечать на такие вопросы. 🚀",
            "Сохранил ваш вопрос для обучения! А пока могу помочь с другими аспектами программирования. 💫",
            "Отличный вопрос! Я еще расту и изучаю новые темы. Можете задать вопрос по-другому? 🌱"
        ]
        return random.choice(responses)
    
    def get_learning_stats(self):
        """Получение статистики"""
        return {
            'total_conversations': self.learning_stats['conversations_processed'],
            'knowledge_base_entries': self.learning_stats['knowledge_base_entries'],
            'web_searches': self.learning_stats['web_searches'],
        }
    
    def export_knowledge_base(self):
        """Экспорт базы знаний"""
        return self.learning_ai.export_knowledge()

class AIHandler(BaseHTTPRequestHandler):
    ai = SmartAI()
    
    def do_GET(self):
        if self.path == '/':
            self._serve_html()
        elif self.path == '/stats':
            self._serve_stats()
        elif self.path == '/export':
            self._export_knowledge()
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
                        • 💻 Показывать примеры кода<br>
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
    
    def _export_knowledge(self):
        """Экспорт базы знаний"""
        export_file = self.ai.export_knowledge_base()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "export_file": export_file}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
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
    
    print(f"🚀 Запуск AI Assistant с текстовой базой знаний на порту {PORT}...")
    print("╔══════════════════════════════════════════════╗")
    print("║           AI Assistant v3.0                 ║")
    print("║        Текстовая база знаний + Веб-поиск    ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 ВОЗМОЖНОСТИ:")
    print("• 📚 Текстовая база знаний (knowledge_base.json)")
    print("• 🔍 Веб-поиск через DuckDuckGo")
    print("• 💻 Примеры кода на Python")
    print("• 🧠 Авто-обучение на взаимодействиях")
    print("• 📤 Экспорт знаний в текстовый файл")
    print("\n🆕 УЛУЧШЕНИЯ:")
    print("• 🤖 Умная обработка неизвестных вопросов")
    print("• 💭 Генерация контекстных ответов")
    print("• 🔧 Автоматическая генерация примеров кода")
    print("• 🎯 Осмысленные ответы вместо 'не понял'")
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), AIHandler)
        print(f"✅ AI Assistant активирован на порту {PORT}")
        print("💫 База знаний готова к работе!")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI Assistant деактивирован")
        print("💾 Сохранение данных...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
