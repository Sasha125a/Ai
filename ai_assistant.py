from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
from datetime import datetime

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'skill_level': 'beginner',
            'preferred_languages': set()
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
            'career': any(word in message_lower for word in ['работа', 'карьера', 'зарплата', 'трудоустройство'])
        }
        
        return [intent for intent, detected in intents.items() if detected]
    
    def extract_entities(self, message):
        entities = {
            'languages': [],
            'technologies': [],
            'concepts': [],
            'level_indicators': []
        }
        
        languages = {
            'python': ['python', 'питон', 'пайтон'],
            'javascript': ['javascript', 'js', 'джаваскрипт'],
            'java': ['java', 'джава'],
            'html': ['html', 'хтмл'],
            'css': ['css', 'цсс'],
            'sql': ['sql', 'ес кью эл'],
            'typescript': ['typescript', 'тсайпскрипт']
        }
        
        for lang, keywords in languages.items():
            if any(keyword in message.lower() for keyword in keywords):
                entities['languages'].append(lang)
        
        technologies = {
            'react': ['react', 'реакт'],
            'vue': ['vue', 'вью'],
            'django': ['django', 'джанго'],
            'flask': ['flask', 'фласк'],
            'node': ['node', 'нод'],
            'docker': ['docker', 'докер'],
            'git': ['git', 'гит']
        }
        
        for tech, keywords in technologies.items():
            if any(keyword in message.lower() for keyword in keywords):
                entities['technologies'].append(tech)
        
        concepts = {
            'ооп': ['ооп', 'объектно-ориентированное', 'object-oriented'],
            'алгоритмы': ['алгоритм', 'алгоритмы', 'algorithm'],
            'базы данных': ['база данных', 'бд', 'database'],
            'веб': ['веб', 'web', 'сайт', 'браузер'],
            'мобильная': ['мобильный', 'mobile', 'android', 'ios'],
            'искусственный интеллект': ['ии', 'ai', 'нейросеть', 'машинное обучение']
        }
        
        for concept, keywords in concepts.items():
            if any(keyword in message.lower() for keyword in keywords):
                entities['concepts'].append(concept)
        
        return entities
    
    def update_user_profile(self, message, entities):
        if entities['languages']:
            self.user_profile['preferred_languages'].update(entities['languages'])
        
        level_indicators = {
            'beginner': ['начинаю', 'новичок', 'только начал', 'с нуля', 'не понимаю'],
            'advanced': ['опытный', 'senior', 'профессионал', 'эксперт', 'глубоко понимаю']
        }
        
        message_lower = message.lower()
        for level, indicators in level_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                self.user_profile['skill_level'] = level
    
    def generate_smart_response(self, message):
        intents = self.analyze_intent(message)
        entities = self.extract_entities(message)
        self.update_user_profile(message, entities)
        
        self.conversation_history.append({
            'message': message,
            'intents': intents,
            'entities': entities,
            'timestamp': datetime.now()
        })
        
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return self._craft_response(message, intents, entities)
    
    def _craft_response(self, message, intents, entities):
        if 'greeting' in intents:
            return self._generate_greeting()
        
        if 'farewell' in intents:
            return self._generate_farewell()
        
        if 'help' in intents:
            return self._generate_help_response()
        
        if 'explanation' in intents:
            return self._generate_explanation(message, entities)
        
        if 'code_request' in intents:
            return self._generate_code_example(message, entities)
        
        if 'comparison' in intents:
            return self._generate_comparison(message, entities)
        
        if 'problem' in intents:
            return self._generate_problem_solution(message, entities)
        
        if 'opinion' in intents:
            return self._generate_opinion(message, entities)
        
        if 'learning_path' in intents:
            return self._generate_learning_path(entities)
        
        if 'career' in intents:
            return self._generate_career_advice(entities)
        
        return self._generate_contextual_response(message, entities)
    
    def _generate_greeting(self):
        greetings = [
            "👋 Привет! Я AI-GPT2 - твой умный помощник в программировании!",
            "🚀 Здравствуй! AI-GPT2 готов к работе! Что хочешь узнать сегодня?",
            "💻 Приветствую! AI-GPT2 активирован. Задавай вопросы!",
            "🎯 Привет! AI-GPT2 онлайн. Готов обсудить программирование!"
        ]
        
        if len(self.conversation_history) > 1:
            last_topic = self._get_last_topic()
            if last_topic:
                return f"👋 С возвращением! Продолжаем тему {last_topic}? Или есть новые вопросы?"
        
        return random.choice(greetings)
    
    def _generate_farewell(self):
        farewells = [
            "👋 До свидания! AI-GPT2 будет ждать твоего возвращения!",
            "🚀 Пока! Удачи в программировании от AI-GPT2!",
            "💫 До встречи! AI-GPT2 всегда готов помочь!",
            "🎯 Пока! Помни - AI-GPT2 твой верный помощник в коде!"
        ]
        return random.choice(farewells)
    
    def _generate_help_response(self):
        base_help = "🤖 **AI-GPT2 может:**\n• Объяснять концепции программирования\n• Генерировать примеры кода\n• Сравнивать технологии\n• Помогать с карьерой\n• Решать проблемы\n\n"
        
        if self.user_profile['preferred_languages']:
            langs = ", ".join(self.user_profile['preferred_languages'])
            base_help += f"🎯 Вижу твои интересы: {langs}. Могу углубиться в эти темы!"
        
        return base_help
    
    def _generate_explanation(self, message, entities):
        if entities['concepts']:
            concept = entities['concepts'][0]
            return self._explain_concept(concept)
        elif entities['languages']:
            language = entities['languages'][0]
            return self._explain_language(language)
        else:
            return "🤔 AI-GPT2: Что именно тебе нужно объяснить? Конкретную технологию или концепцию?"
    
    def _explain_concept(self, concept):
        explanations = {
            'ооп': {
                'beginner': """🎯 **ООП от AI-GPT2:**

Представь, что создаешь игру:
• **Класс** = Чертеж персонажа
• **Объект** = Конкретный персонаж  
• **Свойства** = Характеристики
• **Методы** = Действия

```python
class Hero:
    def __init__(self, name):
        self.name = name
        self.health = 100
    
    def attack(self):
        print(f"{self.name} атакует!")

hero = Hero("Артур")
hero.attack()  # Артур атакует!
```""",
                'intermediate': """⚡ **ООП принципы от AI-GPT2:**

1. **Инкапсуляция** - скрытие деталей
2. **Наследование** - расширение классов
3. **Полиморфизм** - разные поведения
4. **Абстракция** - работа с концепциями

```python
class Animal:
    def speak(self): pass

class Dog(Animal):
    def speak(self): return "Гав!"

class Cat(Animal):  
    def speak(self): return "Мяу!"

# Полиморфизм
for animal in [Dog(), Cat()]:
    print(animal.speak())
```"""
            }
        }
        
        if concept in explanations:
            level = self.user_profile['skill_level']
            return explanations[concept].get(level, explanations[concept]['beginner'])
        
        return f"AI-GPT2: Концепция '{concept}' интересная! Что именно хочешь узнать?"
    
    def _generate_code_example(self, message, entities):
        if entities['languages']:
            language = entities['languages'][0]
            return self._get_smart_code_example(language, message)
        return "AI-GPT2: Для какого языка нужен пример кода?"
    
    def _get_smart_code_example(self, language, context):
        context_lower = context.lower()
        
        if 'ооп' in context_lower:
            examples = {
                'python': """```python
# AI-GPT2: Современный Python класс
from typing import List

class SmartCart:
    def __init__(self):
        self.items: List[str] = []
    
    def add_item(self, item: str) -> None:
        self.items.append(item)
        print(f"AI-GPT2: Добавлен {item}")
    
    def show_items(self) -> None:
        print("AI-GPT2: В корзине:", self.items)

cart = SmartCart()
cart.add_item("Python Book")
cart.add_item("Coffee")
cart.show_items()
```""",
                'javascript': """```javascript
// AI-GPT2: Современный JavaScript класс
class SmartCart {
    constructor() {
        this.items = [];
    }
    
    addItem(item) {
        this.items.push(item);
        console.log(`AI-GPT2: Добавлен ${item}`);
    }
    
    showItems() {
        console.log("AI-GPT2: В корзине:", this.items);
    }
}

const cart = new SmartCart();
cart.addItem("JavaScript Book");
cart.addItem("Coffee");
cart.showItems();
```"""
            }
            return examples.get(language, examples['python'])
        
        # Общий пример
        examples = {
            'python': """```python
# AI-GPT2: Умная обработка данных
def smart_data_processor(data):
    \"\"\"AI-GPT2: Обрабатывает данные интеллектуально\"\"\"
    if not data:
        return "AI-GPT2: Данные пустые!"
    
    processed = [
        f"Элемент {i}: {item}" 
        for i, item in enumerate(data, 1)
    ]
    return processed

# Использование
data = ["Python", "AI", "Programming"]
result = smart_data_processor(data)
for item in result:
    print(item)
```""",
            'javascript': """```javascript
// AI-GPT2: Умный обработчик данных
function smartDataProcessor(data) {
    if (!data || data.length === 0) {
        return "AI-GPT2: Данные пустые!";
    }
    
    return data.map((item, index) => 
        `AI-GPT2: Элемент ${index + 1}: ${item}`
    );
}

// Использование
const data = ["JavaScript", "AI", "Coding"];
const result = smartDataProcessor(data);
result.forEach(item => console.log(item));
```"""
        }
        return examples.get(language, "AI-GPT2: Вот пример на Python!\n" + examples['python'])
    
    def _generate_contextual_response(self, message, entities):
        if len(self.conversation_history) > 1:
            last_entities = self.conversation_history[-2].get('entities', {})
            if last_entities.get('languages') or last_entities.get('concepts'):
                return "AI-GPT2: Продолжаем предыдущую тему? Или есть новый вопрос? 💭"
        
        responses = [
            "AI-GPT2: Интересный вопрос! Давай разберём его вместе. 🤔",
            "AI-GPT2: Хочешь, чтобы я объяснил это подробно? 💡", 
            "AI-GPT2: Хорошая тема! Что конкретно интересует? 🚀",
            "AI-GPT2: Понимаю твой интерес! Помогу разобраться. 📚"
        ]
        
        return random.choice(responses)
    
    def _get_last_topic(self):
        if len(self.conversation_history) < 2:
            return None
        
        last_entry = self.conversation_history[-2]
        entities = last_entry.get('entities', {})
        
        if entities.get('languages'):
            return entities['languages'][0]
        elif entities.get('concepts'):
            return entities['concepts'][0]
        
        return None

class AIHandler(BaseHTTPRequestHandler):
    ai = SmartAI()
    
    def do_GET(self):
        if self.path == '/':
            self._serve_html()
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
            <title>AI-GPT2 🚀</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                    max-width: 600px; 
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
                .header h1 {
                    margin: 0;
                    font-size: 2.2em;
                    font-weight: 700;
                }
                .header p {
                    margin: 5px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
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
                    animation: fadeIn 0.3s ease;
                }
                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .user {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    margin-left: auto;
                    text-align: right;
                    border-bottom-right-radius: 5px;
                }
                .ai {
                    background: white;
                    color: #2c3e50;
                    border: 2px solid #3498db;
                    border-bottom-left-radius: 5px;
                    box-shadow: 0 2px 10px rgba(52, 152, 219, 0.2);
                }
                .input-area {
                    display: flex;
                    gap: 12px;
                    align-items: center;
                }
                #messageInput {
                    flex: 1;
                    padding: 15px 20px;
                    border: 2px solid #bdc3c7;
                    border-radius: 25px;
                    font-size: 16px;
                    outline: none;
                    transition: all 0.3s;
                    background: white;
                }
                #messageInput:focus {
                    border-color: #3498db;
                    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
                }
                button {
                    padding: 15px 25px;
                    background: linear-gradient(135deg, #e74c3c, #c0392b);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    transition: all 0.3s;
                    box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
                }
                button:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(231, 76, 60, 0.4);
                }
                .code-block {
                    background: #2c3e50;
                    color: #ecf0f1;
                    padding: 15px;
                    border-radius: 10px;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    overflow-x: auto;
                    border-left: 4px solid #e74c3c;
                }
                .ai-label {
                    font-weight: 600;
                    color: #3498db;
                    margin-bottom: 5px;
                }
                .user-label {
                    font-weight: 600;
                    color: white;
                    margin-bottom: 5px;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <h1>🚀 AI-GPT2</h1>
                    <p>Умный помощник для программирования</p>
                </div>
                
                <div id="chat">
                    <div class="message ai">
                        <div class="ai-label">🧠 AI-GPT2</div>
                        Привет! Я AI-GPT2 - твой интеллектуальный помощник в мире программирования. 
                        Готов отвечать на вопросы, генерировать код и помогать с обучением! 🚀
                    </div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Спроси AI-GPT2 о программировании...">
                    <button onclick="sendMessage()">Отправить</button>
                </div>
            </div>

            <script>
                function addMessage(text, isUser) {
                    const chat = document.getElementById('chat');
                    const message = document.createElement('div');
                    message.className = isUser ? 'message user' : 'message ai';
                    
                    let formattedText = text;
                    if (text.includes('```')) {
                        formattedText = text.replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, '<div class="code-block">$2</div>');
                    }
                    formattedText = formattedText.replace(/\\n/g, '<br>');
                    
                    if (isUser) {
                        message.innerHTML = '<div class="user-label">👤 Вы</div>' + formattedText;
                    } else {
                        message.innerHTML = '<div class="ai-label">🧠 AI-GPT2</div>' + formattedText;
                    }
                    
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
                        addMessage('❌ AI-GPT2: Ошибка соединения', false);
                    }
                }

                document.getElementById('messageInput').addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') sendMessage();
                });

                document.getElementById('messageInput').focus();
            </script>
        </body>
        </html>
        '''
        self.wfile.write(html.encode('utf-8'))
    
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
            
            self.wfile.write(json.dumps({"response": response}, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Error: {str(e)}")
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        print(f"🚀 AI-GPT2: {format % args}")

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8000
    
    print("🚀 ЗАПУСК AI-GPT2...")
    print("╔══════════════════════════════════════╗")
    print("║             AI-GPT2 1.0             ║")
    print("║    Умный помощник программиста      ║")
    print("╚══════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("🎯 Готов к интеллектуальному общению!")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"✅ AI-GPT2 активирован на {HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
