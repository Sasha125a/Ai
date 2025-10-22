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
            'skill_level': 'beginner',  # beginner, intermediate, advanced
            'preferred_languages': set()
        }
        
    def analyze_intent(self, message):
        """Анализ намерения пользователя"""
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
        """Извлечение сущностей из сообщения"""
        entities = {
            'languages': [],
            'technologies': [],
            'concepts': [],
            'level_indicators': []
        }
        
        # Языки программирования
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
        
        # Технологии и фреймворки
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
        
        # Концепции
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
        """Обновление профиля пользователя на основе его сообщений"""
        if entities['languages']:
            self.user_profile['preferred_languages'].update(entities['languages'])
        
        # Определяем уровень навыков
        level_indicators = {
            'beginner': ['начинаю', 'новичок', 'только начал', 'с нуля', 'не понимаю'],
            'advanced': ['опытный', 'senior', 'профессионал', 'эксперт', 'глубоко понимаю']
        }
        
        message_lower = message.lower()
        for level, indicators in level_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                self.user_profile['skill_level'] = level
    
    def generate_smart_response(self, message):
        """Генерация умного ответа с пониманием контекста"""
        # Анализируем сообщение
        intents = self.analyze_intent(message)
        entities = self.extract_entities(message)
        self.update_user_profile(message, entities)
        
        # Сохраняем в историю
        self.conversation_history.append({
            'message': message,
            'intents': intents,
            'entities': entities,
            'timestamp': datetime.now()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Генерируем ответ на основе анализа
        return self._craft_response(message, intents, entities)
    
    def _craft_response(self, message, intents, entities):
        """Создание осмысленного ответа"""
        
        # Приветствие
        if 'greeting' in intents:
            return self._generate_greeting()
        
        # Прощание
        if 'farewell' in intents:
            return self._generate_farewell()
        
        # Помощь
        if 'help' in intents:
            return self._generate_help_response()
        
        # Запрос объяснения
        if 'explanation' in intents:
            return self._generate_explanation(message, entities)
        
        # Запрос кода
        if 'code_request' in intents:
            return self._generate_code_example(message, entities)
        
        # Сравнение
        if 'comparison' in intents:
            return self._generate_comparison(message, entities)
        
        # Проблема
        if 'problem' in intents:
            return self._generate_problem_solution(message, entities)
        
        # Мнение
        if 'opinion' in intents:
            return self._generate_opinion(message, entities)
        
        # Путь обучения
        if 'learning_path' in intents:
            return self._generate_learning_path(entities)
        
        # Карьера
        if 'career' in intents:
            return self._generate_career_advice(entities)
        
        # Общий ответ с учетом контекста
        return self._generate_contextual_response(message, entities)
    
    def _generate_greeting(self):
        """Генерация приветствия с учетом истории"""
        greetings = [
            "Привет! Рад тебя видеть! Готов обсудить программирование! 🚀",
            "Здравствуй! Как твои успехи в программировании? 💻",
            "Приветствую! Что нового хочешь узнать сегодня? 📚",
            "Привет! Готов к новым знаниям? Задавай вопросы! 🔥"
        ]
        
        # Если у нас есть история, персонализируем приветствие
        if len(self.conversation_history) > 1:
            last_topic = self._get_last_topic()
            if last_topic:
                return f"Привет! Продолжаем обсуждать {last_topic}? И есть новые вопросы? 💭"
        
        return random.choice(greetings)
    
    def _generate_farewell(self):
        """Генерация прощания"""
        farewells = [
            "До свидания! Буду рад помочь снова! 👋",
            "Пока! Удачи в программировании! 🍀",
            "До встречи! Не стесняйся обращаться! 😊",
            "Пока! Помни - практика ключ к успеху! 💪"
        ]
        return random.choice(farewells)
    
    def _generate_help_response(self):
        """Умная помощь с учетом профиля пользователя"""
        base_help = "Я могу:\n• Объяснять концепции программирования\n• Помогать с кодом и примерами\n• Сравнивать технологии\n• Советовать пути обучения\n• Решать проблемы\n\n"
        
        if self.user_profile['preferred_languages']:
            langs = ", ".join(self.user_profile['preferred_languages'])
            base_help += f"Вижу, тебя интересуют: {langs}. Могу углубиться в эти темы! 🎯"
        
        return base_help
    
    def _generate_explanation(self, message, entities):
        """Умное объяснение с учетом уровня пользователя"""
        if entities['concepts']:
            concept = entities['concepts'][0]
            return self._explain_concept(concept)
        elif entities['languages']:
            language = entities['languages'][0]
            return self._explain_language(language)
        else:
            return "Расскажи, что именно тебе нужно объяснить? Конкретную технологию, концепцию или что-то другое? 🤔"
    
    def _explain_concept(self, concept):
        """Объяснение концепций с учетом уровня пользователя"""
        explanations = {
            'ооп': {
                'beginner': """🎯 **ООП для начинающих:**

Объектно-Ориентированное Программирование - это подход, где программа состоит из "объектов".

Представь, что разрабатываешь игру:
• **Класс** = Чертеж персонажа (например, "Игрок")
• **Объект** = Конкретный персонаж (например, "Герой 1")
• **Свойства** = Характеристики (имя, здоровье, уровень)
• **Методы** = Действия (атаковать, лечиться, двигаться)

Простой пример в Python:
```python
class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
    
    def attack(self):
        print(f"{self.name} атакует!")
    
    def take_damage(self, damage):
        self.health -= damage
        print(f"Здоровье: {self.health}")

# Создаем объект
hero = Player("Артур")
hero.attack()  # Артур атакует!
```""",
                'intermediate': """⚡ **ООП: Основные принципы:**

1. **Инкапсуляция** - скрытие внутренней реализации
2. **Наследование** - создание новых классов на основе существующих  
3. **Полиморфизм** - разные реализации одного интерфейса
4. **Абстракция** - работа на уровне концепций, а не деталей

Пример наследования:
```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Гав!"

class Cat(Animal):
    def speak(self):
        return "Мяу!"

# Полиморфизм в действии
animals = [Dog(), Cat()]
for animal in animals:
    print(animal.speak())  # Разное поведение!
```"""
            },
            'алгоритмы': {
                'beginner': """🔍 **Алгоритмы - это пошаговые инструкции**

Представь, что ищешь книгу в библиотеке:
• **Линейный поиск** - проверяешь каждую полку по порядку
• **Бинарный поиск** - открываешь посередине, отбрасываешь половину

Пример поиска в Python:
```python
# Линейный поиск (простой)
def linear_search(items, target):
    for i, item in enumerate(items):
        if item == target:
            return i
    return -1

# Бинарный поиск (эффективный для отсортированных данных)
def binary_search(items, target):
    low, high = 0, len(items)-1
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        elif items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
```""",
                'intermediate': """⚡ **Сложность алгоритмов (Big O)**

• **O(1)** - Константная (доступ к элементу массива)
• **O(log n)** - Логарифмическая (бинарный поиск)
• **O(n)** - Линейная (линейный поиск)
• **O(n²)** - Квадратичная (пузырьковая сортировка)

Сравнение сортировок:
```python
# Пузырьковая O(n²) - медленная, но простая
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

# Быстрая сортировка O(n log n) - эффективная
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```"""
            }
        }
        
        if concept in explanations:
            level = self.user_profile['skill_level']
            if level in explanations[concept]:
                return explanations[concept][level]
            return explanations[concept]['beginner']
        
        return f"Концепция '{concept}' интересная! Расскажи, что именно хочешь узнать о ней? 🤔"
    
    def _explain_language(self, language):
        """Объяснение языков программирования"""
        languages_explanation = {
            'python': """🐍 **Python - язык для всего!**

**Сильные стороны:**
• Простой и читаемый синтаксис
• Отлично для начинающих
• Мощные библиотеки для Data Science
• Веб-фреймворки: Django, Flask
• Автоматизация и скрипты

**Идеален для:**
• Начинающих программистов
• Data Science и AI
• Веб-разработки
• Автоматизации задач

**Пример:**
```python
# Простой и понятный код
numbers = [1, 2, 3, 4, 5]
squares = [x**2 for x in numbers]
even_squares = [x for x in squares if x % 2 == 0]
print(even_squares)  # [4, 16]
```""",
            
            'javascript': """📜 **JavaScript - язык веба**

**Сильные стороны:**
• Работает в браузере
• Универсальный (frontend + backend)
• Огромная экосистема
• Постоянно развивается

**Идеален для:**
• Веб-разработки
• Интерактивных интерфейсов
• Full-stack разработки

**Пример:**
```javascript
// Современный JavaScript
const users = [
    { name: 'Alice', age: 25 },
    { name: 'Bob', age: 30 }
];

// Функциональный подход
const adultUsers = users
    .filter(user => user.age >= 18)
    .map(user => user.name);

console.log(adultUsers); // ['Alice', 'Bob']
```"""
        }
        
        return languages_explanation.get(language, f"Язык {language} интересный! Что конкретно хочешь узнать? 💭")
    
    def _generate_code_example(self, message, entities):
        """Умная генерация примеров кода"""
        if entities['languages']:
            language = entities['languages'][0]
            return self._get_smart_code_example(language, message)
        
        # Если язык не указан, предлагаем варианты
        return "Для какого языка нужен пример кода? Python, JavaScript, или может другой? 💻"
    
    def _get_smart_code_example(self, language, context):
        """Умные примеры кода с учетом контекста"""
        context_lower = context.lower()
        
        if 'ооп' in context_lower or 'класс' in context_lower:
            return self._generate_oop_example(language)
        elif 'функция' in context_lower or 'метод' in context_lower:
            return self._generate_function_example(language)
        elif 'обработка' in context_lower or 'данные' in context_lower:
            return self._generate_data_processing_example(language)
        else:
            return self._generate_general_example(language)
    
    def _generate_oop_example(self, language):
        """Пример ООП для разных языков"""
        examples = {
            'python': """```python
# Современный Python класс с type hints
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    category: str
    
    def apply_discount(self, percent: float) -> float:
        """Применяет скидку к товару"""
        discount = self.price * (percent / 100)
        return self.price - discount

class ShoppingCart:
    def __init__(self):
        self.items: List[Product] = []
    
    def add_product(self, product: Product) -> None:
        self.items.append(product)
    
    def total_price(self) -> float:
        return sum(item.price for item in self.items)
    
    def get_products_by_category(self, category: str) -> List[Product]:
        return [item for item in self.items if item.category == category]

# Использование
laptop = Product("MacBook", 1500.0, "electronics")
phone = Product("iPhone", 800.0, "electronics")

cart = ShoppingCart()
cart.add_product(laptop)
cart.add_product(phone)

print(f"Общая стоимость: ${cart.total_price():.2f}")
print(f"Электроника в корзине: {len(cart.get_products_by_category('electronics'))}")
```""",
            
            'javascript': """```javascript
// Современный JavaScript с классами
class Product {
    constructor(name, price, category) {
        this.name = name;
        this.price = price;
        this.category = category;
    }
    
    applyDiscount(percent) {
        const discount = this.price * (percent / 100);
        return this.price - discount;
    }
}

class ShoppingCart {
    constructor() {
        this.items = [];
    }
    
    addProduct(product) {
        this.items.push(product);
    }
    
    totalPrice() {
        return this.items.reduce((total, item) => total + item.price, 0);
    }
    
    getProductsByCategory(category) {
        return this.items.filter(item => item.category === category);
    }
}

// Использование с современным синтаксисом
const laptop = new Product("MacBook", 1500, "electronics");
const phone = new Product("iPhone", 800, "electronics");

const cart = new ShoppingCart();
cart.addProduct(laptop);
cart.addProduct(phone);

console.log(`Общая стоимость: $${cart.totalPrice()}`);
console.log(`Электроника в корзине: ${cart.getProductsByCategory("electronics").length}`);
```"""
        }
        
        return examples.get(language, "Покажу пример ООП на Python! 🐍\n" + examples['python'])
    
    def _generate_contextual_response(self, message, entities):
        """Контекстный ответ, когда намерение не ясно"""
        # Анализируем историю для понимания контекста
        if len(self.conversation_history) > 1:
            last_intent = self.conversation_history[-2].get('intents', [])
            last_entities = self.conversation_history[-2].get('entities', {})
            
            # Продолжаем предыдущую тему
            if last_entities.get('languages') or last_entities.get('concepts'):
                return "Продолжаем предыдущий разговор? Или есть новый вопрос? 💭"
        
        # Персонализированный ответ на основе профиля
        if self.user_profile['preferred_languages']:
            langs = ", ".join(self.user_profile['preferred_languages'])
            return f"Вижу, тебе интересны {langs}. Хочешь углубиться в эти темы или спросишь о чём-то новом? 🎯"
        
        # Общий умный ответ
        thoughtful_responses = [
            "Интересный вопрос! Давай разберёмся вместе. Что именно тебя интересует? 🤔",
            "Хочешь, чтобы я объяснил это подробно? Или может быть есть другие вопросы? 💡",
            "Это хорошая тема для обсуждения! Расскажи, что конкретно хочешь узнать? 🚀",
            "Понимаю твой интерес! Давай я помогу разобраться в этом вопросе. 📚"
        ]
        
        return random.choice(thoughtful_responses)
    
    def _get_last_topic(self):
        """Получение последней темы из истории"""
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
            <title>🧠 Умный ИИ Чат</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: #f0f2f5;
                }
                .chat-container {
                    background: white;
                    border-radius: 15px;
                    padding: 20px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                }
                #chat {
                    height: 400px;
                    border: 1px solid #e1e5e9;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    overflow-y: auto;
                    background: #fafbfc;
                }
                .message {
                    margin: 12px 0;
                    padding: 12px 16px;
                    border-radius: 12px;
                    max-width: 85%;
                    line-height: 1.5;
                }
                .user {
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    margin-left: auto;
                    text-align: right;
                }
                .ai {
                    background: #ffffff;
                    color: #1a1a1a;
                    border: 1px solid #e1e5e9;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .input-area {
                    display: flex;
                    gap: 10px;
                }
                #messageInput {
                    flex: 1;
                    padding: 12px 16px;
                    border: 2px solid #e1e5e9;
                    border-radius: 25px;
                    font-size: 16px;
                    outline: none;
                    transition: border-color 0.3s;
                }
                #messageInput:focus {
                    border-color: #007bff;
                }
                button {
                    padding: 12px 24px;
                    background: linear-gradient(135deg, #007bff, #0056b3);
                    color: white;
                    border: none;
                    border-radius: 25px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: 600;
                    transition: transform 0.2s;
                }
                button:hover {
                    transform: translateY(-1px);
                }
                .code-block {
                    background: #1e1e1e;
                    color: #d4d4d4;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 10px 0;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    overflow-x: auto;
                    border-left: 4px solid #007bff;
                }
                .typing {
                    color: #666;
                    font-style: italic;
                    padding: 10px;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <h1>🧠 Умный ИИ Чат</h1>
                <p><em>ИИ, который понимает контекст и учится на беседе</em></p>
                
                <div id="chat">
                    <div class="message ai">
                        <strong>🧠 Умный ИИ:</strong><br>
                        Привет! Я не просто отвечаю на вопросы - я понимаю контекст, запоминаю твои интересы и подстраиваюсь под твой уровень. Начнём общение! 🚀
                    </div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Спроси о чём угодно в программировании...">
                    <button onclick="sendMessage()">Отправить</button>
                </div>
            </div>

            <script>
                function addMessage(text, isUser) {
                    const chat = document.getElementById('chat');
                    const message = document.createElement('div');
                    message.className = isUser ? 'message user' : 'message ai';
                    
                    // Форматируем код блоки
                    let formattedText = text;
                    if (text.includes('```')) {
                        formattedText = text.replace(/```(\\w+)?\\n([\\s\\S]*?)```/g, '<div class="code-block">$2</div>');
                    }
                    formattedText = formattedText.replace(/\\n/g, '<br>');
                    
                    if (isUser) {
                        message.innerHTML = '<strong>👤 Вы:</strong><br>' + formattedText;
                    } else {
                        message.innerHTML = '<strong>🧠 ИИ:</strong><br>' + formattedText;
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
                        addMessage('❌ Ошибка соединения', false);
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
            
            # Умный ответ от ИИ
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
        print(f"🌐 {format % args}")

if __name__ == '__main__':
    HOST = '0.0.0.0'
    PORT = 8000
    
    print("🧠 Запуск УМНОГО ИИ Чата...")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 ОСОБЕННОСТИ УМНОГО ИИ:")
    print("• 📝 Понимает намерения и контекст")
    print("• 🧠 Запоминает интересы пользователя") 
    print("• 🎯 Подстраивается под уровень знаний")
    print("• 💭 Анализирует историю диалога")
    print("• 🔄 Учится в процессе общения")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"\n✅ Умный ИИ запущен на {HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен")
