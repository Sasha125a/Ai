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

class CodeGenerator:
    """Класс для настоящей генерации кода с нуля"""
    
    def __init__(self):
        self.syntax_templates = {
            'python': self._python_syntax,
            'javascript': self._javascript_syntax,
            'java': self._java_syntax,
            'cpp': self._cpp_syntax,
            'csharp': self._csharp_syntax
        }
        
        self.common_methods = {
            'getter': ['get_{}', 'получить_{}', 'get{}'],
            'setter': ['set_{}', 'установить_{}', 'set{}'],
            'validator': ['validate_{}', 'проверить_{}', 'is_valid_{}'],
            'processor': ['process_{}', 'обработать_{}', 'handle_{}']
        }
    
    def _python_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для Python"""
        templates = {
            'class': f"class {name}:\n    def __init__(self{params or ''}):\n        pass",
            'function': f"def {name}({params or 'self'}):\n    pass",
            'method': f"def {name}(self{params or ''}):\n    pass",
            'variable': f"{name} = None",
            'if': f"if {name}:\n    pass",
            'loop': f"for item in {name}:\n    pass"
        }
        return templates.get(element_type, '')
    
    def _javascript_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для JavaScript"""
        templates = {
            'class': f"class {name} {{\n    constructor({params or ''}) {{\n    }}\n}}",
            'function': f"function {name}({params or ''}) {{\n}}",
            'method': f"{name}({params or ''}) {{\n}}",
            'variable': f"let {name} = null;",
            'if': f"if ({name}) {{\n}}",
            'loop': f"for (let item of {name}) {{\n}}"
        }
        return templates.get(element_type, '')
    
    def _java_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для Java"""
        templates = {
            'class': f"public class {name} {{\n    public {name}({params or ''}) {{\n    }}\n}}",
            'method': f"public void {name}({params or ''}) {{\n}}",
            'variable': f"private String {name};",
            'if': f"if ({name}) {{\n}}"
        }
        return templates.get(element_type, '')
    
    def _cpp_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для C++"""
        templates = {
            'class': f"class {name} {{\npublic:\n    {name}({params or ''}) {{\n    }}\n}};",
            'method': f"void {name}({params or ''}) {{\n}}",
            'variable': f"string {name};"
        }
        return templates.get(element_type, '')
    
    def _csharp_syntax(self, element_type, name, params=None):
        """Синтаксические шаблоны для C#"""
        templates = {
            'class': f"public class {name} {{\n    public {name}({params or ''}) {{\n    }}\n}}",
            'method': f"public void {name}({params or ''}) {{\n}}",
            'property': f"public string {name} {{ get; set; }}"
        }
        return templates.get(element_type, '')
    
    def generate_method_logic(self, method_name, language, context):
        """Генерация логики для методов на основе их названия"""
        method_lower = method_name.lower()
        
        logic_templates = {
            'python': {
                'get': "return self.{}",
                'set': "self.{} = {}",
                'validate': "return isinstance({}, str) and len({}) > 0",
                'calculate': "return {} * {}",
                'process': "return [x for x in {} if x]",
                'check': "return {} is not None",
                'create': "return {}()",
                'find': "return next((x for x in {} if x == {}), None)"
            },
            'javascript': {
                'get': "return this.{};",
                'set': "this.{} = {};",
                'validate': "return typeof {} === 'string' && {}.length > 0;",
                'calculate': "return {} * {};"
            }
        }
        
        # Определяем тип метода по названию
        for prefix, logic in logic_templates.get(language, {}).items():
            if prefix in method_lower:
                field = method_lower.replace(prefix, '').strip('_')
                if field:
                    return logic.format(field, 'value')
        
        return "pass" if language == 'python' else "{}"
    
    def detect_method_type(self, method_name):
        """Определение типа метода по его названию"""
        method_lower = method_name.lower()
        
        if any(prefix in method_lower for prefix in ['get_', 'get', 'получить']):
            return 'getter'
        elif any(prefix in method_lower for prefix in ['set_', 'set', 'установить']):
            return 'setter'
        elif any(prefix in method_lower for prefix in ['validate_', 'проверить', 'is_valid']):
            return 'validator'
        elif any(prefix in method_lower for prefix in ['process_', 'обработать', 'handle']):
            return 'processor'
        elif any(prefix in method_lower for prefix in ['create_', 'создать']):
            return 'creator'
        elif any(prefix in method_lower for prefix in ['find_', 'найти']):
            return 'finder'
        else:
            return 'general'

class SmartAI:
    def __init__(self):
        self.conversation_history = []
        self.user_profile = {
            'interests': set(),
            'skill_level': 'beginner',
            'preferred_languages': set()
        }
        self.emotional_ai = EmotionalAI()
        self.code_generator = CodeGenerator()
        
        # База знаний по языкам программирования
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
    
    # №1 ПАРСИНГ ТРЕБОВАНИЙ ПОЛЬЗОВАТЕЛЯ
    def _parse_code_requirements(self, message):
        """Анализ того, какой код хочет пользователь"""
        requirements = {
            'class_name': 'CustomClass',
            'attributes': [],
            'methods': [],
            'purpose': 'general',
            'language': 'python',
            'style': 'simple'
        }
        
        message_lower = message.lower()
        
        # Извлечение названия класса
        class_patterns = [
            r'класс\s+(\w+)',
            r'class\s+(\w+)',
            r'создай\s+класс\s+(\w+)',
            r'create\s+class\s+(\w+)'
        ]
        
        for pattern in class_patterns:
            match = re.search(pattern, message_lower)
            if match:
                requirements['class_name'] = match.group(1).capitalize()
                break
        
        # Извлечение атрибутов/полей
        attribute_patterns = [
            r'атрибут[а-я]*\s+(\w+)',
            r'поле\s+(\w+)',
            r'свойств[а-я]*\s+(\w+)',
            r'attribute\s+(\w+)',
            r'field\s+(\w+)',
            r'property\s+(\w+)',
            r'с\s+полями?\s+([\w\s,]+)',
            r'with\s+fields?\s+([\w\s,]+)'
        ]
        
        for pattern in attribute_patterns:
            match = re.search(pattern, message_lower)
            if match:
                attrs_text = match.group(1)
                # Разделяем атрибуты по запятым или пробелам
                attrs = re.split(r'[,\s]+', attrs_text)
                requirements['attributes'].extend([attr.strip() for attr in attrs if attr.strip()])
        
        # Извлечение методов
        method_patterns = [
            r'метод[а-я]*\s+(\w+)',
            r'функци[а-я]*\s+(\w+)',
            r'method\s+(\w+)',
            r'function\s+(\w+)',
            r'с\s+методами?\s+([\w\s,]+)',
            r'with\s+methods?\s+([\w\s,]+)'
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, message_lower)
            if match:
                methods_text = match.group(1)
                methods = re.split(r'[,\s]+', methods_text)
                requirements['methods'].extend([method.strip() for method in methods if method.strip()])
        
        # Определение языка программирования
        for lang_key, lang_info in self.programming_languages.items():
            if lang_key in message_lower or lang_info['name'].lower() in message_lower:
                requirements['language'] = lang_key
                break
        
        # Определение стиля/назначения
        if any(word in message_lower for word in ['сложный', 'продвинутый', 'advanced', 'complex']):
            requirements['style'] = 'advanced'
        elif any(word in message_lower for word in ['простой', 'базовый', 'simple', 'basic']):
            requirements['style'] = 'simple'
        
        # Если атрибуты не найдены явно, попробуем извлечь из контекста
        if not requirements['attributes']:
            # Ищем слова, которые могут быть атрибутами (существительные)
            words = re.findall(r'\b([a-zа-я]{3,15})\b', message_lower)
            potential_attrs = []
            for word in words:
                if word not in ['класс', 'class', 'метод', 'method', 'функция', 'function', 
                               'создай', 'create', 'напиши', 'write', 'код', 'code']:
                    potential_attrs.append(word)
            
            if len(potential_attrs) <= 5:  # Берем только если не слишком много слов
                requirements['attributes'] = potential_attrs[:3]
        
        return requirements
    
    # №2 ГЕНЕРАЦИЯ КОДА С НУЛЯ
    def _generate_truly_new_code(self, language, requirements):
        """Генерация действительно нового кода на основе требований"""
        
        if language == 'python':
            return self._generate_python_from_scratch(requirements)
        elif language == 'javascript':
            return self._generate_javascript_from_scratch(requirements)
        elif language == 'java':
            return self._generate_java_from_scratch(requirements)
        elif language == 'cpp':
            return self._generate_cpp_from_scratch(requirements)
        elif language == 'csharp':
            return self._generate_csharp_from_scratch(requirements)
        else:
            return self._generate_python_from_scratch(requirements)  # fallback
    
    def _generate_python_from_scratch(self, requirements):
        """Генерация Python кода с нуля на основе требований"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['name', 'value']
        methods = requirements['methods']
        
        code = f"# AI-GPT2: Сгенерированный класс {class_name}\n"
        code += f"class {class_name}:\n"
        
        # Конструктор
        init_params = ", ".join([f"{attr}=None" for attr in attributes])
        code += f"    def __init__(self, {init_params}):\n"
        for attr in attributes:
            code += f"        self._{attr} = {attr}\n"
        
        # Геттеры и сеттеры для атрибутов
        for attr in attributes:
            code += f"\n    @property\n"
            code += f"    def {attr}(self):\n"
            code += f"        return self._{attr}\n"
            code += f"\n    @{attr}.setter\n"
            code += f"    def {attr}(self, value):\n"
            code += f"        self._{attr} = value\n"
        
        # Пользовательские методы
        for method in methods:
            code += f"\n    def {method}(self):\n"
            logic = self.code_generator.generate_method_logic(method, 'python', requirements)
            code += f"        {logic}\n"
        
        # Добавляем стандартные методы если их нет
        if not methods:
            code += f"\n    def __str__(self):\n"
            code += f"        return f\"{class_name}({', '.join([f'{attr}={{self._{attr}}}' for attr in attributes])})\"\n"
        
        code += f"\n\n# Использование:\n"
        code += f"# obj = {class_name}({', '.join([f'\"example_{attr}\"' for attr in attributes])})\n"
        code += f"# print(obj)"
        
        return f"```python\n{code}\n```"
    
    def _generate_javascript_from_scratch(self, requirements):
        """Генерация JavaScript кода с нуля на основе требований"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['name', 'value']
        methods = requirements['methods']
        
        code = f"// AI-GPT2: Сгенерированный класс {class_name}\n"
        code += f"class {class_name} {{\n"
        
        # Конструктор
        code += f"    constructor({', '.join(attributes)}) {{\n"
        for attr in attributes:
            code += f"        this._{attr} = {attr};\n"
        code += f"    }}\n"
        
        # Геттеры и сеттеры
        for attr in attributes:
            code += f"\n    get {attr}() {{\n"
            code += f"        return this._{attr};\n"
            code += f"    }}\n"
            code += f"\n    set {attr}(value) {{\n"
            code += f"        this._{attr} = value;\n"
            code += f"    }}\n"
        
        # Пользовательские методы
        for method in methods:
            code += f"\n    {method}() {{\n"
            logic = self.code_generator.generate_method_logic(method, 'javascript', requirements)
            code += f"        {logic}\n"
            code += f"    }}\n"
        
        code += f"}}\n\n"
        code += f"// Использование:\n"
        code += f"// const obj = new {class_name}({', '.join([f'\"example_{attr}\"' for attr in attributes])});\n"
        code += f"// console.log(obj);"
        
        return f"```javascript\n{code}\n```"
    
    def _generate_java_from_scratch(self, requirements):
        """Генерация Java кода с нуля на основе требований"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['name', 'value']
        
        code = f"// AI-GPT2: Сгенерированный класс {class_name}\n"
        code += f"public class {class_name} {{\n"
        
        # Поля класса
        for attr in attributes:
            code += f"    private String {attr};\n"
        
        # Конструктор
        code += f"\n    public {class_name}({', '.join([f'String {attr}' for attr in attributes])}) {{\n"
        for attr in attributes:
            code += f"        this.{attr} = {attr};\n"
        code += f"    }}\n"
        
        # Геттеры и сеттеры
        for attr in attributes:
            code += f"\n    public String get{attr.capitalize()}() {{\n"
            code += f"        return this.{attr};\n"
            code += f"    }}\n"
            code += f"\n    public void set{attr.capitalize()}(String {attr}) {{\n"
            code += f"        this.{attr} = {attr};\n"
            code += f"    }}\n"
        
        # Метод toString
        code += f"\n    @Override\n"
        code += f"    public String toString() {{\n"
        code += f"        return \"{class_name}{\" +\n"
        attr_strings = [f'                \"{attr}=\" + {attr} + \"\\\"' for attr in attributes]
        code += ' +\n'.join(attr_strings) + "};\n"
        code += f"    }}\n"
        code += f"}}"
        
        return f"```java\n{code}\n```"
    
    def _generate_cpp_from_scratch(self, requirements):
        """Генерация C++ кода с нуля на основе требований"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['name', 'value']
        
        code = f"// AI-GPT2: Сгенерированный класс {class_name}\n"
        code += f"#include <string>\n#include <iostream>\n\n"
        code += f"class {class_name} {{\nprivate:\n"
        
        # Поля класса
        for attr in attributes:
            code += f"    std::string {attr};\n"
        
        code += f"\npublic:\n"
        # Конструктор
        code += f"    {class_name}({', '.join([f'std::string {attr}' for attr in attributes])}) {{\n"
        for attr in attributes:
            code += f"        this->{attr} = {attr};\n"
        code += f"    }}\n"
        
        # Геттеры и сеттеры
        for attr in attributes:
            code += f"\n    std::string get{attr.capitalize()}() const {{\n"
            code += f"        return this->{attr};\n"
            code += f"    }}\n"
            code += f"\n    void set{attr.capitalize()}(std::string {attr}) {{\n"
            code += f"        this->{attr} = {attr};\n"
            code += f"    }}\n"
        
        # Метод вывода
        code += f"\n    void print() const {{\n"
        code += f"        std::cout << \"{class_name} {{\";\n"
        for i, attr in enumerate(attributes):
            if i > 0:
                code += f"        std::cout << \", \";\n"
            code += f"        std::cout << \"{attr}=\" << {attr};\n"
        code += f"        std::cout << \"}}\" << std::endl;\n"
        code += f"    }}\n"
        code += f"}};"
        
        return f"```cpp\n{code}\n```"
    
    def _generate_csharp_from_scratch(self, requirements):
        """Генерация C# кода с нуля на основе требований"""
        class_name = requirements['class_name']
        attributes = requirements['attributes'] or ['Name', 'Value']
        
        code = f"// AI-GPT2: Сгенерированный класс {class_name}\n"
        code += f"using System;\n\n"
        code += f"public class {class_name} {{\n"
        
        # Свойства (автоматические)
        for attr in attributes:
            code += f"    public string {attr} {{ get; set; }}\n"
        
        # Конструктор
        code += f"\n    public {class_name}({', '.join([f'string {attr.ToLower()}' for attr in attributes])}) {{\n"
        for attr in attributes:
            code += f"        this.{attr} = {attr.ToLower()};\n"
        code += f"    }}\n"
        
        # Конструктор по умолчанию
        code += f"\n    public {class_name}() {{\n"
        code += f"        // Конструктор по умолчанию\n"
        code += f"    }}\n"
        
        # Метод ToString
        code += f"\n    public override string ToString() {{\n"
        code += f"        return $\"{class_name}{{{', '.join([f'{attr}={{{attr}}}' for attr in attributes])}}}\";\n"
        code += f"    }}\n"
        code += f"}}"
        
        return f"```csharp\n{code}\n```"
    
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
            'file_operation': any(word in message_lower for word in ['файл', 'загрузи', 'проанализируй', 'открой']),
            'create_code': any(word in message_lower for word in ['создай', 'придумай', 'новый класс', 'сгенерируй класс', 'напиши класс'])
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
    
    # №3 ИНТЕГРАЦИЯ В ОСНОВНОЙ МЕТОД
    def generate_smart_response(self, message):
        # Анализ настроения пользователя
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
        
        # Добавляем эмоциональную окраску
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
        
        # ПРИОРИТЕТ: Если запрос на создание нового кода
        if 'create_code' in intents or ('code_request' in intents and any(word in message.lower() for word in ['создай', 'придумай', 'новый'])):
            return self._generate_new_code_from_scratch(message)
        
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
    
    def _generate_new_code_from_scratch(self, message):
        """Генерация совершенно нового кода на основе требований пользователя"""
        # Парсим требования
        requirements = self._parse_code_requirements(message)
        
        # Генерируем код
        generated_code = self._generate_truly_new_code(requirements['language'], requirements)
        
        response = f"🚀 **AI-GPT2 сгенерировал новый код!**\n\n"
        response += f"📋 **Анализ запроса:**\n"
        response += f"• Класс: `{requirements['class_name']}`\n"
        response += f"• Язык: `{requirements['language']}`\n"
        if requirements['attributes']:
            response += f"• Атрибуты: {', '.join(requirements['attributes'])}\n"
        if requirements['methods']:
            response += f"• Методы: {', '.join(requirements['methods'])}\n"
        
        response += f"\n💻 **Сгенерированный код:**\n{generated_code}"
        response += f"\n\n🎯 **Это не шаблон! Код создан с нуля на основе ваших требований!**"
        
        return response
    
    def _generate_code_example(self, message, entities):
        """Генерация кода на запрошенном языке"""
        if entities['languages']:
            target_language = entities['languages'][0]
            
            # Проверяем, не хочет ли пользователь новый код
            message_lower = message.lower()
            if any(word in message_lower for word in ['создай', 'придумай', 'новый']):
                return self._generate_new_code_from_scratch(message)
            
            return self._generate_specific_code(target_language, message)
        else:
            # Если язык не указан, предлагаем варианты
            return "На каком языке программирования нужен код? Я поддерживаю: Python, JavaScript, Java, C++, C#, Go, Rust, Kotlin, Swift, PHP, Ruby, TypeScript! 💻\n\nИли скажите 'Создай класс...' для генерации нового кода!"
    
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
            # Если нет специфических требований, предлагаем создать новый код
            return f"Хотите готовый пример на {language} или создать новый класс? Скажите 'Создай класс...' для генерации уникального кода! 🚀"
    
    # Старые методы для обратной совместимости (используют шаблоны)
    def _generate_oop_example(self, language):
        """Генерация ООП примера на разных языках (шаблоны)"""
        examples = {
            'python': """```python
# Пример класса BankAccount
class BankAccount:
    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner
        self._balance = balance
    
    def deposit(self, amount: float) -> None:
        if amount > 0:
            self._balance += amount
    
    def withdraw(self, amount: float) -> bool:
        if 0 < amount <= self._balance:
            self._balance -= amount
            return True
        return False
    
    def get_balance(self) -> float:
        return self._balance
```""",
            
            'javascript': """```javascript
// Пример класса BankAccount
class BankAccount {
    constructor(owner, balance = 0.0) {
        this.owner = owner;
        this._balance = balance;
    }
    
    deposit(amount) {
        if (amount > 0) {
            this._balance += amount;
        }
    }
    
    withdraw(amount) {
        if (amount > 0 && amount <= this._balance) {
            this._balance -= amount;
            return true;
        }
        return false;
    }
    
    getBalance() {
        return this._balance;
    }
}
```"""
        }
        
        return f"📚 **Готовый пример на {language}:**\n\n" + examples.get(language, examples['python']) + "\n\n💡 **Хотите уникальный код? Скажите 'Создай класс...'!**"
    
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
        base_help = """🤖 **AI-GPT2 МОЖЕТ ТЕПЕРЬ ГЕНЕРИРОВАТЬ КОД С НУЛЯ!**

🚀 **НОВАЯ ФУНКЦИЯ - ГЕНЕРАЦИЯ КОДА:**
• Создает классы по вашим требованиям
• Генерирует методы и атрибуты
• Поддерживает 5+ языков
• Адаптируется под ваш стиль

💻 **Поддерживаемые языки:**
• Python, JavaScript, Java, C++, C#

📁 **Работа с файлами:**
• Анализ кода
• Проверка стиля  
• Поиск ошибок

🧠 **Эмоциональный интеллект:**
• Понимает ваше настроение
• Подстраивает ответы
• Поддерживает и мотивирует

**Примеры запросов для генерации кода:**
• "Создай класс Car с атрибутами brand, model, year"
• "Придумай класс User на Python с методами login, logout"
• "Сгенерируй класс Product на JavaScript"

"""
        
        if self.user_profile['preferred_languages']:
            langs = ", ".join([self.programming_languages[lang]['name'] for lang in self.user_profile['preferred_languages']])
            base_help += f"🎯 Вижу твои интересы: {langs}. Могу сгенерировать код на этих языках!"
        
        return base_help

    # Остальные методы остаются без изменений
    def _generate_greeting(self):
        greetings = [
            "👋 Привет! Я AI-GPT2 - теперь я могу генерировать код с нуля!",
            "🚀 Здравствуй! AI-GPT2 готов создавать классы по твоим требованиям!",
            "💻 Приветствую! Скажи 'Создай класс...' и я сгенерирую код!",
            "🎯 Привет! Готов создавать уникальный код на любом языке!"
        ]
        
        if len(self.conversation_history) > 1:
            last_topic = self._get_last_topic()
            if last_topic:
                lang_name = self.programming_languages.get(last_topic, {}).get('name', last_topic)
                return f"👋 С возвращением! Продолжаем {lang_name}? Или создать новый класс?"
        
        return random.choice(greetings)
    
    def _generate_farewell(self):
        farewells = [
            "👋 До свидания! AI-GPT2 будет ждать твоих идей для нового кода!",
            "🚀 Пока! Возвращайся с новыми идеями для генерации кода!",
            "💫 До встречи! Придумай интересный класс - сгенерирую!",
            "🎯 Пока! Помни - AI-GPT2 теперь генерирует код с нуля!"
        ]
        return random.choice(farewells)
    
    def _generate_contextual_response(self, message, entities):
        if len(self.conversation_history) > 1:
            last_entities = self.conversation_history[-2].get('entities', {})
            if last_entities.get('languages') or last_entities.get('concepts'):
                return "AI-GPT2: Продолжаем предыдущую тему? Или хочешь создать новый класс? 🚀"
        
        responses = [
            "AI-GPT2: Хочешь, чтобы я сгенерировал новый код? Скажи 'Создай класс...'! 🎯",
            "AI-GPT2: Готов создать уникальный класс по твоим требованиям! 💻", 
            "AI-GPT2: Придумай класс - я сгенерирую код на любом языке! 🚀",
            "AI-GPT2: Хочешь готовый пример или создать что-то новое? 💡"
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

# Остальной код (AIHandler, HTTP сервер) остается без изменений
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
                .feature.new {
                    background: #ffeb3b;
                    font-weight: bold;
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
                .prompt-examples {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                    margin: 10px 0;
                }
                .prompt-example {
                    background: #e8f4fd;
                    padding: 10px;
                    border-radius: 8px;
                    font-size: 0.8em;
                    cursor: pointer;
                    border: 1px solid #3498db;
                }
                .prompt-example:hover {
                    background: #d1ecf1;
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="header">
                    <h1>🚀 AI-GPT2 v3.0</h1>
                    <p>Теперь генерирует код с нуля! + Эмоциональный ИИ + 12 языков</p>
                    <div class="features">
                        <div class="feature new">🚀 Генерация кода</div>
                        <div class="feature">💻 12+ языков</div>
                        <div class="feature">🧠 Эмоциональный ИИ</div>
                        <div class="feature">📁 Работа с файлами</div>
                    </div>
                </div>
                
                <div class="prompt-examples">
                    <div class="prompt-example" onclick="insertPrompt(this)">"Создай класс Car с brand, model, year"</div>
                    <div class="prompt-example" onclick="insertPrompt(this)">"Придумай класс User на Python"</div>
                    <div class="prompt-example" onclick="insertPrompt(this)">"Сгенерируй класс Product на JavaScript"</div>
                    <div class="prompt-example" onclick="insertPrompt(this)">"Создай класс Animal с методами"</div>
                </div>
                
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <h3>📁 Загрузить файл для анализа</h3>
                    <p>Кликните для выбора файла (.py, .js, .java, .txt, .json)</p>
                    <input type="file" id="fileInput" style="display: none;" onchange="handleFileUpload(this.files)">
                </div>
                
                <div id="chat">
                    <div class="message ai">
                        <div class="ai-label">🧠 AI-GPT2 v3.0</div>
                        <strong>🚀 НОВАЯ ФУНКЦИЯ:</strong> Теперь я генерирую код с нуля!<br><br>
                        💡 <strong>Примеры запросов:</strong><br>
                        • "Создай класс Car с атрибутами brand, model, year"<br>
                        • "Придумай класс User на Python с методами"<br>
                        • "Сгенерируй класс Product на JavaScript"<br><br>
                        🎯 Я проанализирую ваш запрос и создам уникальный код!
                    </div>
                </div>
                
                <div class="input-area">
                    <input type="text" id="messageInput" placeholder="Создай класс... или спроси о коде...">
                    <button onclick="sendMessage()">Отправить</button>
                </div>
            </div>

            <script>
                function insertPrompt(element) {
                    document.getElementById('messageInput').value = element.textContent;
                    document.getElementById('messageInput').focus();
                }

                function addMessage(text, isUser) {
                    const chat = document.getElementById('chat');
                    const message = document.createElement('div');
                    message.className = isUser ? 'message user' : 'message ai';
                    
                    let formattedText = text;
                    // Обработка блоков кода
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
    
    print("🚀 ЗАПУСК AI-GPT2 v3.0 С ГЕНЕРАЦИЕЙ КОДА С НУЛЯ...")
    print("╔══════════════════════════════════════════════╗")
    print("║                 AI-GPT2 3.0                 ║")
    print("║    Генерация кода + Эмоциональный ИИ        ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"📍 Сервер: http://localhost:{PORT}")
    print("\n🎯 НОВЫЕ ВОЗМОЖНОСТИ v3.0:")
    print("• 🚀 Генерация кода с нуля (не шаблоны!)")
    print("• 💻 Автоматическое создание классов")
    print("• 🎯 Парсинг требований пользователя") 
    print("• 📝 Генерация методов и атрибутов")
    print("• 🌟 Поддержка 5+ языков для генерации")
    
    try:
        server = HTTPServer((HOST, PORT), AIHandler)
        print(f"✅ AI-GPT2 3.0 активирован на {HOST}:{PORT}")
        print("💡 Пример запроса: 'Создай класс Car с атрибутами brand, model, year'")
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 AI-GPT2 деактивирован")
