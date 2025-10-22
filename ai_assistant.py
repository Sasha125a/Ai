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
    from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
import os
import base64
from datetime import datetime
import mimetypes

class EmotionalAI:
    """11. Эмоциональный интеллект ИИ"""
    
    def __init__(self):
        self.user_mood = 'neutral'
        self.conversation_tone = 'professional'
        self.enthusiasm_level = 1.0
        
    def analyze_mood(self, message):
        """Анализ настроения пользователя по сообщению"""
        message_lower = message.lower()
        
        # Определяем эмоциональную окраску
        positive_words = ['спасибо', 'отлично', 'круто', 'супер', 'хорошо', 'понравилось', 'рад']
        negative_words = ['плохо', 'грустно', 'злой', 'разочарован', 'не нравится', 'устал', 'сложно']
        frustrated_words = ['не работает', 'ошибка', 'помоги', 'срочно', 'не понимаю', 'застрял']
        excited_words = ['вау', 'интересно', 'любопытно', 'хочу узнать', 'увлекательно']
        
        mood_scores = {
            'positive': sum(1 for word in positive_words if word in message_lower),
            'negative': sum(1 for word in negative_words if word in message_lower),
            'frustrated': sum(1 for word in frustrated_words if word in message_lower),
            'excited': sum(1 for word in excited_words if word in message_lower)
        }
        
        # Определяем доминирующее настроение
        max_score = max(mood_scores.values())
        if max_score > 0:
            for mood, score in mood_scores.items():
                if score == max_score:
                    self.user_mood = mood
                    break
        else:
            self.user_mood = 'neutral'
        
        # Обновляем уровень энтузиазма
        self._update_enthusiasm()
        
    def _update_enthusiasm(self):
        """Обновление уровня энтузиазма ИИ на основе настроения пользователя"""
        enthusiasm_map = {
            'positive': 1.3,
            'excited': 1.5,
            'neutral': 1.0,
            'frustrated': 0.8,
            'negative': 0.7
        }
        self.enthusiasm_level = enthusiasm_map.get(self.user_mood, 1.0)
    
    def get_emotional_response(self, base_response):
        """Добавление эмоциональной окраски к ответу"""
        emotional_prefixes = {
            'positive': ['Отлично! ', 'Замечательно! ', 'Прекрасно! ', 'Великолепно! '],
            'excited': ['Вау! ', 'Это интересно! ', 'Увлекательно! ', 'Захватывающе! '],
            'neutral': ['', 'Итак, ', 'Хорошо, ', 'Давайте '],
            'frustrated': ['Понимаю ваше разочарование. ', 'Не переживайте! ', 'Сейчас разберёмся. ', 'Всё исправим! '],
            'negative': ['Понимаю. ', 'Всё наладится. ', 'Давайте решим это. ', 'Не волнуйтесь. ']
        }
        
        emotional_suffixes = {
            'positive': [' 🎉', ' 😊', ' 👍', ' ✨'],
            'excited': [' 🚀', ' 🔥', ' 💫', ' 🌟'],
            'neutral': ['', '.', '!', ' 💡'],
            'frustrated': [' 🤗', ' 💪', ' 🔧', ' 🛠️'],
            'negative': [' 🤝', ' 📚', ' 🎯', ' 💭']
        }
        
        prefix = random.choice(emotional_prefixes.get(self.user_mood, ['']))
        suffix = random.choice(emotional_suffixes.get(self.user_mood, ['']))
        
        # Добавляем энтузиазм через восклицательные знаки
        if self.enthusiasm_level > 1.2 and '!' not in prefix:
            base_response = base_response.replace('.', '!', 1)
        
        return f"{prefix}{base_response}{suffix}"

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'skill_level': 'beginner',
            'preferred_languages': set()
        }
        self.emotional_ai = EmotionalAI()
        
        # 11. Расширенная база знаний по языкам программирования
        self.programming_languages = {
            'python': {
                'name': 'Python',
                'paradigms': ['object-oriented', 'functional', 'imperative'],
                'typing': 'dynamic',
                'use_cases': ['web', 'data science', 'ai', 'automation'],
                'extensions': ['.py', '.pyw']
            },
            'javascript': {
                'name': 'JavaScript', 
                'paradigms': ['object-oriented', 'functional', 'event-driven'],
                'typing': 'dynamic',
                'use_cases': ['web frontend', 'web backend', 'mobile'],
                'extensions': ['.js', '.jsx', '.ts', '.tsx']
            },
            'java': {
                'name': 'Java',
                'paradigms': ['object-oriented', 'imperative'],
                'typing': 'static',
                'use_cases': ['enterprise', 'android', 'web backend'],
                'extensions': ['.java', '.jar']
            },
            'cpp': {
                'name': 'C++',
                'paradigms': ['object-oriented', 'procedural', 'generic'],
                'typing': 'static', 
                'use_cases': ['system', 'game', 'high-performance'],
                'extensions': ['.cpp', '.h', '.hpp']
            },
            'csharp': {
                'name': 'C#',
                'paradigms': ['object-oriented', 'functional'],
                'typing': 'static',
                'use_cases': ['windows', 'game', 'web', 'enterprise'],
                'extensions': ['.cs']
            },
            'go': {
                'name': 'Go',
                'paradigms': ['procedural', 'concurrent'],
                'typing': 'static',
                'use_cases': ['backend', 'system', 'cloud'],
                'extensions': ['.go']
            },
            'rust': {
                'name': 'Rust',
                'paradigms': ['functional', 'object-oriented'],
                'typing': 'static',
                'use_cases': ['system', 'web assembly', 'safety-critical'],
                'extensions': ['.rs']
            },
            'kotlin': {
                'name': 'Kotlin',
                'paradigms': ['object-oriented', 'functional'],
                'typing': 'static',
                'use_cases': ['android', 'backend', 'web'],
                'extensions': ['.kt']
            },
            'swift': {
                'name': 'Swift',
                'paradigms': ['object-oriented', 'functional'],
                'typing': 'static',
                'use_cases': ['ios', 'macos', 'backend'],
                'extensions': ['.swift']
            },
            'php': {
                'name': 'PHP',
                'paradigms': ['object-oriented', 'procedural'],
                'typing': 'dynamic',
                'use_cases': ['web backend'],
                'extensions': ['.php']
            },
            'ruby': {
                'name': 'Ruby',
                'paradigms': ['object-oriented', 'functional'],
                'typing': 'dynamic',
                'use_cases': ['web', 'scripting'],
                'extensions': ['.rb']
            },
            'typescript': {
                'name': 'TypeScript',
                'paradigms': ['object-oriented', 'functional'],
                'typing': 'static',
                'use_cases': ['web frontend', 'web backend'],
                'extensions': ['.ts', '.tsx']
            }
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
            'career': any(word in message_lower for word in ['работа', 'карьера', 'зарплата', 'трудоустройство']),
            'file_operation': any(word in message_lower for word in ['файл', 'загрузи', 'проанализируй', 'открой'])
        }
        
        return [intent for intent, detected in intents.items() if detected]
    
    def extract_entities(self, message):
        entities = {
            'languages': [],
            'technologies': [],
            'concepts': [],
            'level_indicators': []
        }
        
        # Поиск языков программирования
        for lang_key, lang_info in self.programming_languages.items():
            lang_name = lang_info['name'].lower()
            if (lang_key in message.lower() or 
                lang_name in message.lower() or
                any(word in message.lower() for word in [lang_key, lang_name])):
                entities['languages'].append(lang_key)
        
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
        # 11. Анализ настроения пользователя
        self.emotional_ai.analyze_mood(message)
        
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
        
        response = self._craft_response(message, intents, entities)
        
        # 11. Добавляем эмоциональную окраску
        return self.emotional_ai.get_emotional_response(response)
    
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
        
        if 'file_operation' in intents:
            return self._handle_file_operations(message)
        
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
    
    def _generate_code_example(self, message, entities):
        """Генерация кода на запрошенном языке"""
        if entities['languages']:
            target_language = entities['languages'][0]
            return self._generate_specific_code(target_language, message)
        else:
            # Если язык не указан, предлагаем варианты
            return "На каком языке программирования нужен код? Я поддерживаю: Python, JavaScript, Java, C++, C#, Go, Rust, Kotlin, Swift, PHP, Ruby, TypeScript! 💻"
    
    def _generate_specific_code(self, language, context):
        """Генерация кода на конкретном языке"""
        context_lower = context.lower()
        
        # Определяем тип запроса
        if any(word in context_lower for word in ['ооп', 'класс', 'object']):
            return self._generate_oop_example(language)
        elif any(word in context_lower for word in ['функция', 'function', 'метод']):
            return self._generate_function_example(language)
        elif any(word in context_lower for word in ['алгоритм', 'сортировка', 'поиск']):
            return self._generate_algorithm_example(language)
        elif any(word in context_lower for word in ['структура', 'данные', 'data structure']):
            return self._generate_data_structure_example(language)
        else:
            return self._generate_general_example(language)
    
    def _generate_oop_example(self, language):
        """Генерация ООП примера на разных языках"""
        examples = {
            'python': """```python,
# AI-GPT2: Класс для управления банковским счетом
class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance  # Инкапсуляция
    
    def deposit(self, amount: float) -> None:
        """Пополнение счета"""
        if amount > 0:
            self._balance += amount
            print(f"✅ {self.owner}: +{amount} руб. Баланс: {self._balance} руб.")
        else:
            print("❌ Сумма должна быть положительной")
    
    def withdraw(self, amount: float) -> bool:
        """Снятие со счета"""
        if 0 < amount <= self._balance:
            self._balance -= amount
            print(f"✅ {self.owner}: -{amount} руб. Баланс: {self._balance} руб.")
            return True
        else:
            print("❌ Недостаточно средств или неверная сумма")
            return False
    
    def get_balance(self) -> float:
        """Получение баланса"""
        return self._balance

# Наследование
class SavingsAccount(BankAccount):
    def __init__(self, owner: str, balance: float = 0.0, interest_rate: float = 0.05):
        super().__init__(owner, balance)
        self.interest_rate = interest_rate
    
    def add_interest(self) -> None:
        """Начисление процентов"""
        interest = self._balance * self.interest_rate
        self._balance += interest
        print(f"📈 Начислены проценты: +{interest:.2f} руб.")

# Использование
account = SavingsAccount("Иван Иванов", 1000, 0.03)
account.deposit(500)
account.add_interest()
account.withdraw(200)
print(f"💰 Итоговый баланс: {account.get_balance():.2f} руб.")
```""",
            
            'javascript': """```javascript
// AI-GPT2: Класс для управления банковским счетом
class BankAccount {
    constructor(owner, balance = 0.0) {
        this.owner = owner;
        this._balance = balance; // Инкапсуляция
    }
    
    deposit(amount) {
        /** Пополнение счета */
        if (amount > 0) {
            this._balance += amount;
            console.log(`✅ ${this.owner}: +${amount} руб. Баланс: ${this._balance} руб.`);
        } else {
            console.log("❌ Сумма должна быть положительной");
        }
    }
    
    withdraw(amount) {
        /** Снятие со счета */
        if (amount > 0 && amount <= this._balance) {
            this._balance -= amount;
            console.log(`✅ ${this.owner}: -${amount} руб. Баланс: ${this._balance} руб.`);
            return true;
        } else {
            console.log("❌ Недостаточно средств или неверная сумма");
            return false;
        }
    }
    
    getBalance() {
        /** Получение баланса */
        return this._balance;
    }
}

// Наследование
class SavingsAccount extends BankAccount {
    constructor(owner, balance = 0.0, interestRate = 0.05) {
        super(owner, balance);
        this.interestRate = interestRate;
    }
    
    addInterest() {
        /** Начисление процентов */
        const interest = this._balance * this.interestRate;
        this._balance += interest;
        console.log(`📈 Начислены проценты: +${interest.toFixed(2)} руб.`);
    }
}

// Использование
const account = new SavingsAccount("Иван Иванов", 1000, 0.03);
account.deposit(500);
account.addInterest();
account.withdraw(200);
console.log(`💰 Итоговый баланс: ${account.getBalance().toFixed(2)} руб.`);
```""",
            
            'java': """```java
// AI-GPT2: Класс для управления банковским счетом
public class BankAccount {
    private String owner;
    private double balance;
    
    public BankAccount(String owner, double balance) {
        this.owner = owner;
        this.balance = balance;
    }
    
    public BankAccount(String owner) {
        this(owner, 0.0);
    }
    
    public void deposit(double amount) {
        /** Пополнение счета */
        if (amount > 0) {
            this.balance += amount;
            System.out.printf("✅ %s: +%.2f руб. Баланс: %.2f руб.%n", 
                owner, amount, balance);
        } else {
            System.out.println("❌ Сумма должна быть положительной");
        }
    }
    
    public boolean withdraw(double amount) {
        /** Снятие со счета */
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            System.out.printf("✅ %s: -%.2f руб. Баланс: %.2f руб.%n", 
                owner, amount, balance);
            return true;
        } else {
            System.out.println("❌ Недостаточно средств или неверная сумма");
            return false;
        }
    }
    
    public double getBalance() {
        return balance;
    }
    
    public String getOwner() {
        return owner;
    }
}

// Наследование
public class SavingsAccount extends BankAccount {
    private double interestRate;
    
    public SavingsAccount(String owner, double balance, double interestRate) {
        super(owner, balance);
        this.interestRate = interestRate;
    }
    
    public void addInterest() {
        /** Начисление процентов */
        double interest = getBalance() * interestRate;
        deposit(interest);
        System.out.printf("📈 Начислены проценты: +%.2f руб.%n", interest);
    }
}

// Использование
public class Main {
    public static void main(String[] args) {
        SavingsAccount account = new SavingsAccount("Иван Иванов", 1000, 0.03);
        account.deposit(500);
        account.addInterest();
        account.withdraw(200);
        System.out.printf("💰 Итоговый баланс: %.2f руб.%n", account.getBalance());
    }
}
```""",
            
            'cpp': """```cpp
// AI-GPT2: Класс для управления банковским счетом
#include <iostream>
#include <string>

class BankAccount {
private:
    std::string owner;
    double balance;

public:
    BankAccount(const std::string& owner, double balance = 0.0) 
        : owner(owner), balance(balance) {}
    
    void deposit(double amount) {
        /** Пополнение счета */
        if (amount > 0) {
            balance += amount;
            std::cout << "✅ " << owner << ": +" << amount 
                      << " руб. Баланс: " << balance << " руб." << std::endl;
        } else {
            std::cout << "❌ Сумма должна быть положительной" << std::endl;
        }
    }
    
    bool withdraw(double amount) {
        /** Снятие со счета */
        if (amount > 0 && amount <= balance) {
            balance -= amount;
            std::cout << "✅ " << owner << ": -" << amount 
                      << " руб. Баланс: " << balance << " руб." << std::endl;
            return true;
        } else {
            std::cout << "❌ Недостаточно средств или неверная сумма" << std::endl;
            return false;
        }
    }
    
    double getBalance() const {
        return balance;
    }
    
    std::string getOwner() const {
        return owner;
    }
};

// Наследование
class SavingsAccount : public BankAccount {
private:
    double interestRate;

public:
    SavingsAccount(const std::string& owner, double balance, double interestRate)
        : BankAccount(owner, balance), interestRate(interestRate) {}
    
    void addInterest() {
        /** Начисление процентов */
        double interest = getBalance() * interestRate;
        deposit(interest);
        std::cout << "📈 Начислены проценты: +" << interest << " руб." << std::endl;
    }
};

// Использование
int main() {
    SavingsAccount account("Иван Иванов", 1000, 0.03);
    account.deposit(500);
    account.addInterest();
    account.withdraw(200);
    std::cout << "💰 Итоговый баланс: " << account.getBalance() << " руб." << std::endl;
    return 0;
}
```"""
        }
        
        return examples.get(language, f"AI-GPT2: Покажу пример на Python! 🐍\n{examples['python']}")
    
    def _handle_file_operations(self, message):
        """Обработка операций с файлами"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['загрузи', 'upload', 'добавь файл']):
            return "📁 Для загрузки файлов используйте форму ниже! Я могу анализировать:\n• Python файлы (.py)\n• Текстовые файлы (.txt)\n• JSON данные (.json)\n• И другие текстовые форматы!"
        
        elif any(word in message_lower for word in ['проанализируй', 'analyze', 'проверь код']):
            return "🔍 Загрузите файл с кодом, и я проанализирую его на:\n• Синтаксические ошибки\n• Стиль кода (PEP8 для Python)\n• Потенциальные улучшения\n• Best practices"
        
        else:
            return "📂 Я могу работать с файлами! Скажите:\n• 'Загрузи файл' - для загрузки\n• 'Проанализируй код' - для анализа кода\n• Или задайте вопрос о конкретном файле!"
    
    def _generate_help_response(self):
        base_help = """🤖 **AI-GPT2 может:**

💻 **Генерация кода на 12+ языках:**
• Python, JavaScript, Java, C++
• C#, Go, Rust, Kotlin  
• Swift, PHP, Ruby, TypeScript

📁 **Работа с файлами:**
• Анализ кода
• Проверка стиля
• Поиск ошибок

🧠 **Эмоциональный интеллект:**
• Понимает ваше настроение
• Подстраивает ответы
• Поддерживает и мотивирует

🎯 **И многое другое:**
• Объяснение концепций
• Решение проблем
• Карьерные советы
• Сравнение технологий

"""
        
        if self.user_profile['preferred_languages']:
            langs = ", ".join([self.programming_languages[lang]['name'] for lang in self.user_profile['preferred_languages']])
            base_help += f"🎯 Вижу твои интересы: {langs}. Могу углубиться в эти темы!"
        
        return base_help

    # Остальные методы остаются аналогичными предыдущей версии
    def _generate_greeting(self):
        greetings = [
            "👋 Привет! Я AI-GPT2 - твой эмоционально интеллектуальный помощник!",
            "🚀 Здравствуй! AI-GPT2 готов к работе с файлами и кодом на 12+ языках!",
            "💻 Приветствую! Загружай файлы, проси код - AI-GPT2 поможет!",
            "🎯 Привет! Готов генерировать код на любом языке программирования!"
        ]
        
        if len(self.conversation_history) > 1:
            last_topic = self._get_last_topic()
            if last_topic:
                lang_name = self.programming_languages.get(last_topic, {}).get('name', last_topic)
                return f"👋 С возвращением! Продолжаем {lang_name}? Или есть новые вопросы?"
        
        return random.choice(greetings)
    
    def _generate_farewell(self):
        farewells = [
            "👋 До свидания! AI-GPT2 будет ждать твоего возвращения!",
            "🚀 Пока! Удачи в программировании с AI-GPT2!",
            "💫 До встречи! Загружай файлы - помогу проанализировать!",
            "🎯 Пока! Помни - AI-GPT2 поддерживает 12+ языков программирования!"
        ]
        return random.choice(farewells)
    
    def _generate_contextual_response(self, message, entities):
        if len(self.conversation_history) > 1:
            last_entities = self.conversation_history[-2].get('entities', {})
            if last_entities.get('languages') or last_entities.get('concepts'):
                return "AI-GPT2: Продолжаем предыдущую тему? Или хочешь поработать с файлами? 💭"
        
        responses = [
            "AI-GPT2: Интересный вопрос! Могу сгенерировать код или проанализировать файл! 🤔",
            "AI-GPT2: Хочешь пример кода на конкретном языке? Или загрузить файл? 💡", 
            "AI-GPT2: Хорошая тема! Выбери язык для примера кода! 🚀",
            "AI-GPT2: Понимаю твой интерес! Готов помочь с кодом или файлами! 📚"
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
        elif self.path == '/upload':
            self._handle_file_upload()
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
                    max-width: 800px; 
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
                .features {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin: 15px 0;
                }
                .feature {
                    background: #f8f9fa;
                    padding: 10px;
                    border-radius: 10px;
                    text-align: center;
                    font-size: 0.9em;
                    border: 1px solid #e9ecef;
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
                .upload-area {
                    border: 2px dashed #3498db;
                    border-radius: 10px;
                    padding: 20px;
                    text-align: center;
                    margin: 10px 0;
                    background: #f8f9fa;
                    cursor: pointer;
                }
                .upload-area:hover {
                    background: #e9ecef;
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
                    <p>Эмоционально интеллектуальный помощник с поддержкой 12+ языков</p>
                    <div class="features">
                        <div class="feature">🧠 Эмоциональный ИИ</div>
                        <div class="feature">💻 12+ языков кода</div>
                        <div class="feature">📁 Работа с файлами</div>
                        <div class="feature">🎯 Умные ответы</div>
                    </div>
                </div>
                
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <h3>📁 Загрузить файл для анализа</h3>
                    <p>Кликните для выбора файла (.py, .js, .java, .txt, .json)</p>
                    <input type="file" id="fileInput" style="display: none;" onchange="handleFileUpload(this.files)">
                </div>
                
                <div id="chat">
                    <div class="message ai">
                        <div class="ai-label">🧠 AI-GPT2</div>
                        Привет! Я AI-GPT2 с эмоциональным интеллектом! 🧠<br><br>
                        🔥 <strong>Новые возможности:</strong><br>
                        • Генерация кода на 12+ языках<br>
                        • Эмоциональные ответы<br>
                        • Работа с файлами<br>
                        • Анализ настроения<br><br>
                        Проси код на любом языке или загружай файлы! 🚀
                    </div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Спроси о коде на любом языке или работе с файлами...">
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

                async function handleFileUpload(files) {
                    if (!files.length) return;
                    
                    const file = files[0];
                    const reader = new FileReader();
                    
                    reader.onload = async function(e) {
                        const content = e.target.result;
                        addMessage(`📁 Загружен файл: ${file.name} (${file.size} байт)`, true);
                        
                        try {
                            const response = await fetch('/upload', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({
                                    filename: file.name,
                                    content: content,
                                    size: file.size
                                })
                            });
                            
                            const data = await response.json();
                            addMessage(data.response, false);
                            
                        } catch (error) {
                            addMessage('❌ Ошибка загрузки файла', false);
                        }
                    };
                    
                    reader.readAsText(file);
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
    
    def _handle_file_upload(self):
        """Обработка загрузки файлов"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            filename = data.get('filename', 'unknown')
            content = data.get('content', '')
            size = data.get('size', 0)
            
            # Анализ файла
            analysis = self._analyze_file(filename, content)
            
            response = f"📊 **Анализ файла {filename}:**\n\n{analysis}"
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps({"response": response}, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Upload Error: {str(e)}")
    
    def _analyze_file(self, filename, content):
        """Анализ загруженного файла"""
        file_ext = os.path.splitext(filename)[1].lower()
        
        analysis = []
        analysis.append(f"📁 **Файл:** {filename}")
        analysis.append(f"📏 **Размер:** {len(content)} символов")
        
        # Определяем тип файла
        file_types = {
            '.py': 'Python файл',
            '.js': 'JavaScript файл', 
            '.java': 'Java файл',
            '.cpp': 'C++ файл',
            '.cs': 'C# файл',
            '.go': 'Go файл',
            '.rs': 'Rust файл',
            '.kt': 'Kotlin файл',
            '.swift': 'Swift файл',
            '.php': 'PHP файл',
            '.rb': 'Ruby файл',
            '.ts': 'TypeScript файл',
            '.txt': 'Текстовый файл',
            '.json': 'JSON файл'
        }
        
        file_type = file_types.get(file_ext, 'Неизвестный тип файла')
        analysis.append(f"🔧 **Тип:** {file_type}")
        
        # Базовый анализ содержимого
        lines = content.split('\n')
        analysis.append(f"📝 **Строк кода:** {len(lines)}")
        
        # Поиск потенциальных проблем
        issues = []
        
        if file_ext == '.py':
            # Анализ Python кода
            if 'import *' in content:
                issues.append("⚠️ Избегайте 'import *' - импортируйте только нужные модули")
            if 'eval(' in content or 'exec(' in content:
                issues.append("⚠️ Осторожно с eval()/exec() - возможны уязвимости безопасности")
            if len(content) > 1000:
                issues.append("💡 Файл довольно большой - рассмотрите разбиение на модули")
                
        elif file_ext == '.js':
            # Анализ JavaScript кода
            if 'eval(' in content:
                issues.append("⚠️ Осторожно с eval() - возможны уязвимости безопасности")
            if 'var ' in content:
                issues.append("💡 Используйте let/const вместо var для лучшей области видимости")
                
        elif file_ext == '.java':
            # Анализ Java кода
            if 'public static void main' in content:
                issues.append("🎯 Обнаружена точка входа Java приложения")
                
        if issues:
            analysis.append("\n🔍 **Рекомендации:**")
            analysis.extend(issues)
        else:
            analysis.append("\n✅ **Код выглядит хорошо!**")
        
        analysis.append(f"\n🧠 **AI-GPT2:** Могу помочь улучшить этот код! Просто спросите!")
        
        return '\n'.join(analysis)
    
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
    
    print("🚀 ЗАПУСК AI-GPT2 С РАСШИРЕННЫМИ ВОЗМОЖНОСТЯМИ...")
    print("╔══════════════════════════════════════════════╗")
    print("║                 AI-GPT2 2.0                 ║")
    print("║  Эмоциональный ИИ + 12 языков + файлы       ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 НОВЫЕ ВОЗМОЖНОСТИ:")
    print("• 🧠 Эмоциональный интеллект")
    print("• 💻 12+ языков программирования") 
    print("• 📁 Работа с файлами")
    print("• 🎯 Генерация кода по запросу")
    print("• 🔍 Анализ загруженного кода")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"✅ AI-GPT2 2.0 активирован на {HOST}:{PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
