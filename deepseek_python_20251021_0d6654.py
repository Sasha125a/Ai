from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import zipfile
import tempfile
from datetime import datetime
import urllib.parse
import threading

class KnowledgeBase:
    def __init__(self):
        self.knowledge_file = "ai_knowledge.json"
        self.base_knowledge = self._load_base_knowledge()
        self.user_knowledge = self._load_user_knowledge()
    
    def _load_base_knowledge(self):
        return {
            "programming": {
                "python": {
                    "basics": "Переменные: x=5, функции: def name():, классы: class MyClass:",
                    "web": "Flask: микрофреймворк, Django: полноценный фреймворк",
                    "data": "Pandas для данных, NumPy для вычислений, Matplotlib для графиков",
                    "syntax": "Отступы важны! Используйте 4 пробела. PEP8 - стандарт стиля."
                },
                "javascript": {
                    "basics": "let x=5, функции: function name() {}, стрелочные: () => {}",
                    "web": "React, Vue, Angular - популярные фреймворки",
                    "node": "JavaScript на сервере с Node.js"
                },
                "java": {
                    "basics": "public class Main { public static void main(String[] args) {} }",
                    "oop": "Наследование, инкапсуляция, полиморфизм"
                }
            },
            "web_development": {
                "frontend": "HTML (структура), CSS (стили), JavaScript (логика)",
                "backend": "Серверная логика, базы данных, API",
                "tools": "Git, Docker, VS Code, Chrome DevTools"
            },
            "algorithms": {
                "sorting": "Быстрая сортировка, сортировка слиянием, пузырьковая",
                "search": "Бинарный поиск, линейный поиск",
                "structures": "Массивы, списки, деревья, графы, хэш-таблицы"
            },
            "mobile": {
                "android": "Java/Kotlin, Android Studio",
                "ios": "Swift, Xcode", 
                "crossplatform": "Flutter, React Native"
            }
        }
    
    def _load_user_knowledge(self):
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {"interactions": [], "created": datetime.now().isoformat()}
    
    def save_knowledge(self):
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_knowledge, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving knowledge: {e}")
    
    def add_interaction(self, question, answer):
        interaction = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        
        self.user_knowledge["interactions"].append(interaction)
        
        # Сохраняем только последние 100 взаимодействий
        if len(self.user_knowledge["interactions"]) > 100:
            self.user_knowledge["interactions"] = self.user_knowledge["interactions"][-100:]
        
        self.save_knowledge()
    
    def find_knowledge(self, query):
        query_lower = query.lower()
        results = []
        
        # Поиск по базовым знаниям
        for category, subcats in self.base_knowledge.items():
            for subcat, content in subcats.items():
                if isinstance(content, dict):
                    for key, value in content.items():
                        if query_lower in key.lower() or query_lower in str(value).lower():
                            results.append(f"{category}.{subcat}.{key}: {value}")
                elif query_lower in subcat.lower() or query_lower in str(content).lower():
                    results.append(f"{category}.{subcat}: {content}")
        
        return results[:3]
    
    def get_stats(self):
        interactions = self.user_knowledge.get("interactions", [])
        return {
            "total_interactions": len(interactions),
            "knowledge_categories": list(self.base_knowledge.keys()),
            "last_interaction": interactions[-1] if interactions else None
        }

class ProjectManager:
    def analyze_zip(self, file_content):
        try:
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "temp.zip")
            
            # Сохраняем временный файл
            with open(zip_path, 'wb') as f:
                f.write(file_content)
            
            # Распаковываем и анализируем
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            return self.analyze_project(temp_dir)
            
        except Exception as e:
            print(f"Error analyzing ZIP: {e}")
            return None
        finally:
            # Очистка временных файлов
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
    
    def analyze_project(self, project_path):
        structure = {
            'name': os.path.basename(project_path),
            'files': [],
            'file_types': {},
            'total_files': 0,
            'total_size': 0
        }
        
        try:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    file_size = os.path.getsize(file_path)
                    structure['total_size'] += file_size
                    
                    file_info = {
                        'path': rel_path,
                        'size': file_size,
                        'extension': os.path.splitext(file)[1].lower()
                    }
                    
                    structure['files'].append(file_info)
                    ext = file_info['extension']
                    structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                    structure['total_files'] += 1
            
            structure['total_size_mb'] = round(structure['total_size'] / (1024 * 1024), 2)
            return structure
            
        except Exception as e:
            print(f"Error analyzing project: {e}")
            return structure

class AIAssistant:
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.project_manager = ProjectManager()
    
    def process_message(self, message, context=None):
        # Пытаемся найти в выученных ответах
        learned_response = self._get_learned_response(message)
        if learned_response:
            response = f"💡 [Из памяти]\n{learned_response}"
        else:
            # Генерируем новый ответ
            response = self._generate_response(message, context)
        
        # Сохраняем взаимодействие
        self.knowledge_base.add_interaction(message, response)
        
        return response
    
    def _get_learned_response(self, message):
        interactions = self.knowledge_base.user_knowledge.get("interactions", [])
        message_lower = message.lower()
        
        for interaction in interactions[-20:]:
            question_lower = interaction["question"].lower()
            # Простой поиск совпадений по словам
            message_words = set(message_lower.split())
            question_words = set(question_lower.split())
            common_words = message_words.intersection(question_words)
            
            if len(common_words) >= 2:  # Если есть 2+ общих слова
                return interaction["answer"]
        
        return None
    
    def _generate_response(self, message, context):
        message_lower = message.lower()
        
        # Приветствие
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hello', 'hi', 'start']):
            return "Привет! Я ИИ помощник для программирования. 🚀\n\nЗадавайте вопросы о коде, технологиях или загружайте ZIP с проектами для анализа!"
        
        # Помощь
        if any(word in message_lower for word in ['помощь', 'help', 'команды', 'что ты умеешь']):
            return self._get_help_message()
        
        # Поиск в знаниях
        knowledge = self.knowledge_base.find_knowledge(message)
        if knowledge:
            response = "🧠 **Найдено в знаниях:**\n" + "\n".join(knowledge)
            response += "\n\n💡 Нужна более конкретная информация? Задайте уточняющий вопрос!"
            return response
        
        # Генерация кода
        if any(word in message_lower for word in ['сгенерируй', 'напиши код', 'создай код', 'пример кода']):
            return self._generate_code(message)
        
        # О проектах
        if any(word in message_lower for word in ['проект', 'zip', 'архив', 'файл']):
            return "📁 Для анализа проекта загрузите ZIP архив через интерфейс. Я проанализирую структуру и состав файлов."
        
        # Статистика
        if any(word in message_lower for word in ['статистика', 'статус', 'инфо']):
            return self._get_stats_message()
        
        # Общий ответ
        return self._get_general_response(message)
    
    def _get_help_message(self):
        return """
🤖 **ИИ Помощник для Программирования**

**Я могу помочь с:**
• 💬 Вопросами о программировании
• 📁 Анализом проектов (ZIP архивы)
• 💻 Генерацией примеров кода
• 🔍 Поиском информации в базе знаний

**Поддерживаемые технологии:**
• Python, JavaScript, Java, SQL
• Веб-разработка (frontend/backend)
• Мобильная разработка
• Алгоритмы и структуры данных

**Просто спросите о:**
- Синтаксисе языка
- Best practices
- Архитектуре приложений
- Решении конкретных проблем

И я обучусь на ваших вопросах! 🎯
"""
    
    def _generate_code(self, message):
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['веб', 'сервер', 'flask', 'django']):
            return '''```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Hello World!", "status": "success"})

@app.route('/api/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'POST':
        data = request.get_json()
        return jsonify({"received": data})
    else:
        return jsonify({"data": [1, 2, 3, 4, 5]})

if __name__ == '__main__':
    app.run(debug=True)
```'''
        
        elif any(word in message_lower for word in ['данн', 'анализ', 'pandas', 'csv']):
            return '''```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def analyze_data(file_path):
    """Анализ данных из CSV файла"""
    try:
        df = pd.read_csv(file_path)
        
        analysis = {
            'rows': len(df),
            'columns': df.columns.tolist(),
            'missing_values': df.isnull().sum().to_dict(),
            'statistics': df.describe().to_dict()
        }
        
        # Создание простого графика
        plt.figure(figsize=(10, 6))
        df.hist()
        plt.savefig('data_analysis.png')
        plt.close()
        
        return analysis
        
    except Exception as e:
        return f"Ошибка анализа: {e}"

# Использование
if __name__ == "__main__":
    result = analyze_data("data.csv")
    print(result)
```'''
        
        elif any(word in message_lower for word in ['класс', 'объект', 'oop']):
            return '''```python
class Student:
    """Класс для представления студента"""
    
    def __init__(self, name, age, grades=None):
        self.name = name
        self.age = age
        self.grades = grades or []
    
    def add_grade(self, grade):
        """Добавление оценки"""
        self.grades.append(grade)
    
    def get_average(self):
        """Расчет среднего балла"""
        if not self.grades:
            return 0
        return sum(self.grades) / len(self.grades)
    
    def __str__(self):
        return f"Student(name={self.name}, age={self.age}, avg_grade={self.get_average()})"

# Пример использования
student = Student("Иван", 20)
student.add_grade(5)
student.add_grade(4)
student.add_grade(5)

print(student)  # Student(name=Иван, age=20, avg_grade=4.666666666666667)
```'''
        
        else:
            return f'''```python
# Решение для: {message}

def main():
    """Основная функция"""
    print("Реализуйте вашу логику здесь!")
    
    # Пример обработки данных
    data = [1, 2, 3, 4, 5]
    result = sum(x * 2 for x in data if x % 2 == 0)
    
    print(f"Результат: {{result}}")
    return result

if __name__ == "__main__":
    main()
```'''
    
    def _get_stats_message(self):
        stats = self.knowledge_base.get_stats()
        response = [
            "📊 **Статистика ИИ:**",
            f"• Всего взаимодействий: {stats['total_interactions']}",
            f"• Категории знаний: {', '.join(stats['knowledge_categories'])}",
            "",
            "🎯 **База знаний включает:**",
            "• Python, JavaScript, Java",
            "• Веб и мобильную разработку", 
            "• Алгоритмы и структуры данных",
            "• Best practices и инструменты",
            "",
            "💡 Я учусь на каждом вашем вопросе!"
        ]
        return "\n".join(response)
    
    def _get_general_response(self, message):
        responses = [
            "Интересный вопрос! На основе моих знаний о программировании...",
            "В контексте разработки программного обеспечения...",
            "Учитывая современные практики программирования, я бы рекомендовал...",
            "Исходя из моего опыта работы с кодом...",
            "На основе лучших практик в индустрии..."
        ]
        base_response = responses[len(message) % len(responses)]
        
        # Добавляем обучающий момент
        stats = self.knowledge_base.get_stats()
        base_response += f"\n\n📚 Я уже помог с {stats['total_interactions']} вопросами и продолжаю учиться!"
        
        return base_response

class AIRequestHandler(BaseHTTPRequestHandler):
    ai_assistant = AIAssistant()
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_INTERFACE.encode('utf-8'))
        elif self.path == '/api/stats':
            self._handle_api_stats()
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == '/api/chat':
            self._handle_chat(post_data)
        elif self.path == '/api/upload':
            self._handle_upload(post_data)
        elif self.path == '/api/clear':
            self._handle_clear()
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_api_stats(self):
        stats = self.ai_assistant.knowledge_base.get_stats()
        self._send_json_response(stats)
    
    def _handle_chat(self, post_data):
        try:
            data = json.loads(post_data.decode('utf-8'))
            message = data.get('message', '')
            
            if not message:
                self._send_json_response({'error': 'Empty message'}, 400)
                return
            
            # Обрабатываем сообщение в отдельном потоке для избежания блокировки
            def process_message():
                response = self.ai_assistant.process_message(message)
                self._send_json_response({
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                })
            
            thread = threading.Thread(target=process_message)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _handle_upload(self, post_data):
        try:
            # Простой парсинг multipart form data
            content_type = self.headers.get('Content-Type', '')
            if 'multipart/form-data' not in content_type:
                self._send_json_response({'error': 'Invalid content type'}, 400)
                return
            
            # Извлекаем файл из multipart данных
            boundary = content_type.split('boundary=')[1]
            parts = post_data.split(b'--' + boundary.encode())
            
            for part in parts:
                if b'filename="' in part:
                    # Нашли файл, извлекаем содержимое
                    file_content = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                    
                    project_info = self.ai_assistant.project_manager.analyze_zip(file_content)
                    
                    if project_info:
                        self._send_json_response({
                            'success': True,
                            'project_info': project_info,
                            'message': 'Проект успешно проанализирован'
                        })
                    else:
                        self._send_json_response({'error': 'Failed to analyze project'}, 500)
                    return
            
            self._send_json_response({'error': 'No file found'}, 400)
            
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _handle_clear(self):
        try:
            self.ai_assistant.knowledge_base.user_knowledge["interactions"] = []
            self.ai_assistant.knowledge_base.save_knowledge()
            self._send_json_response({'success': True, 'message': 'History cleared'})
        except Exception as e:
            self._send_json_response({'error': str(e)}, 500)
    
    def _send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

# HTML интерфейс
HTML_INTERFACE = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 ИИ Помощник для Программирования</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }

        .header {
            background: #2c3e50;
            color: white;
            padding: 25px;
            text-align: center;
        }

        .header h1 {
            margin-bottom: 10px;
            font-size: 2.2em;
        }

        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }

        .main-content {
            display: flex;
            min-height: 70vh;
        }

        @media (max-width: 768px) {
            .main-content {
                flex-direction: column;
            }
        }

        .sidebar {
            width: 300px;
            background: #34495e;
            color: white;
            padding: 20px;
        }

        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #ecf0f1;
        }

        .messages {
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            max-height: 60vh;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .message {
            padding: 18px;
            border-radius: 18px;
            max-width: 85%;
            word-wrap: break-word;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            background: #3498db;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }

        .ai-message {
            background: white;
            color: #2c3e50;
            border: 1px solid #bdc3c7;
            border-bottom-left-radius: 5px;
        }

        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #bdc3c7;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }

        .input-area textarea {
            flex: 1;
            padding: 15px;
            border: 2px solid #bdc3c7;
            border-radius: 12px;
            resize: none;
            font-family: inherit;
            font-size: 16px;
            transition: border-color 0.3s;
        }

        .input-area textarea:focus {
            outline: none;
            border-color: #3498db;
        }

        .input-area button {
            padding: 15px 25px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .input-area button:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }

        .upload-area {
            border: 3px dashed #3498db;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            margin-bottom: 20px;
            cursor: pointer;
            transition: all 0.3s;
        }

        .upload-area:hover {
            background: #f8f9fa;
            border-color: #2980b9;
        }

        .file-input {
            display: none;
        }

        .project-info {
            background: #2c3e50;
            border-radius: 8px;
            padding: 18px;
            margin-top: 15px;
            font-size: 14px;
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 18px;
            border-radius: 8px;
            margin-top: 12px;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.4;
        }

        .tab-buttons {
            display: flex;
            background: #34495e;
            border-bottom: 2px solid #2c3e50;
        }

        .tab-button {
            flex: 1;
            padding: 18px;
            text-align: center;
            background: #2c3e50;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: background 0.3s;
        }

        .tab-button:hover {
            background: #3c5570;
        }

        .tab-button.active {
            background: #3498db;
        }

        .tab-content {
            display: none;
            padding: 25px;
        }

        .tab-content.active {
            display: block;
        }

        .stats-item {
            background: white;
            padding: 18px;
            margin: 12px 0;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .loading {
            text-align: center;
            color: #7f8c8d;
            font-style: italic;
            padding: 20px;
        }

        .copy-btn {
            background: #27ae60;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 6px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 14px;
            transition: background 0.3s;
        }

        .copy-btn:hover {
            background: #219653;
        }

        .clear-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 15px;
            width: 100%;
            font-size: 16px;
            transition: background 0.3s;
        }

        .clear-btn:hover {
            background: #c0392b;
        }

        .quick-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .quick-btn {
            background: #3498db;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }

        .quick-btn:hover {
            background: #2980b9;
            transform: translateY(-2px);
        }

        @media (max-width: 480px) {
            .container {
                margin: 10px;
                border-radius: 12px;
            }
            
            .message {
                max-width: 95%;
                padding: 15px;
            }
            
            .input-area {
                flex-direction: column;
                gap: 10px;
            }
            
            .input-area button {
                width: 100%;
            }
            
            .quick-actions {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ИИ Помощник для Программирования</h1>
            <p>Умный помощник для вопросов о коде, анализа проектов и генерации примеров</p>
        </div>

        <div class="tab-buttons">
            <button class="tab-button active" onclick="openTab('chat')">💬 Чат с ИИ</button>
            <button class="tab-button" onclick="openTab('project')">📁 Анализ проекта</button>
            <button class="tab-button" onclick="openTab('stats')">📊 Статистика</button>
        </div>

        <div class="main-content">
            <!-- Вкладка чата -->
            <div id="chat" class="tab-content active">
                <div class="messages" id="messages">
                    <div class="message ai-message">
                        <strong>🤖 ИИ помощник:</strong><br><br>
                        Привет! Я ваш умный помощник для программирования. 🚀<br><br>
                        Я могу:<br>
                        • Отвечать на вопросы о коде и технологиях<br>
                        • Анализировать структуру проектов (ZIP архивы)<br>
                        • Генерировать примеры кода<br>
                        • Помогать с лучшими практиками<br><br>
                        Просто задайте вопрос или загрузите проект!
                    </div>
                </div>
                
                <div class="input-area">
                    <textarea id="messageInput" placeholder="Задайте вопрос о программировании, например: 'Как работает Python класс?' или 'Сгенерируй пример веб-сервера'..." rows="3"></textarea>
                    <button onclick="sendMessage()">📨 Отправить</button>
                </div>

                <div class="quick-actions">
                    <button class="quick-btn" onclick="quickQuestion('Сгенерируй пример Flask сервера')">🌐 Веб-сервер</button>
                    <button class="quick-btn" onclick="quickQuestion('Покажи пример класса Python')">🐍 Класс Python</button>
                    <button class="quick-btn" onclick="quickQuestion('Как работать с pandas?')">📊 Анализ данных</button>
                    <button class="quick-btn" onclick="quickQuestion('Что такое ООП?')">🎯 ООП</button>
                </div>
            </div>

            <!-- Вкладка проекта -->
            <div id="project" class="tab-content">
                <div class="sidebar">
                    <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                        <h3>📁 Загрузить ZIP проект</h3>
                        <p>Кликните для выбора или перетащите файл</p>
                        <p style="font-size: 12px; opacity: 0.8; margin-top: 10px;">Поддерживаются архивы до 500MB</p>
                        <input type="file" id="fileInput" class="file-input" accept=".zip">
                    </div>
                    
                    <div id="projectInfo" style="display: none;">
                        <h4>📊 Информация о проекте</h4>
                        <div class="project-info" id="projectDetails"></div>
                    </div>
                </div>
            </div>

            <!-- Вкладка статистики -->
            <div id="stats" class="tab-content">
                <div class="sidebar">
                    <h4>📈 Статистика ИИ</h4>
                    <div class="stats-item">
                        <strong>Всего взаимодействий:</strong>
                        <span id="interactionsCount">0</span>
                    </div>
                    <div class="stats-item">
                        <strong>Категории знаний:</strong>
                        <div id="knowledgeCategories">Загрузка...</div>
                    </div>
                    <button class="clear-btn" onclick="clearHistory()">🧹 Очистить историю обучения</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentProject = null;

        function openTab(tabName) {
            // Скрываем все вкладки
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Убираем активный класс у всех кнопок
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Показываем выбранную вкладку
            document.getElementById(tabName).classList.add('active');
            event.currentTarget.classList.add('active');

            // Загружаем статистику при открытии вкладки
            if (tabName === 'stats') {
                loadStats();
            }
        }

        function addMessage(sender, message, isUser = false) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
            
            // Форматируем код если есть
            let formattedMessage = formatMessage(message);
            
            messageDiv.innerHTML = formattedMessage;
            
            // Добавляем кнопку копирования для сообщений ИИ
            if (!isUser) {
                const copyBtn = document.createElement('button');
                copyBtn.className = 'copy-btn';
                copyBtn.textContent = '📋 Копировать ответ';
                copyBtn.onclick = () => copyToClipboard(message);
                messageDiv.appendChild(copyBtn);
            }
            
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function formatMessage(text) {
            // Форматируем код блоки
            let formatted = text.replace(/```(\w+)?\n([\s\S]*?)```/g, '<div class="code-block">$2</div>');
            
            // Жирный текст
            formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            
            // Эмодзи и переносы строк
            formatted = formatted.replace(/\n/g, '<br>');
            
            return formatted;
        }

        function copyToClipboard(text) {
            // Убираем форматирование Markdown для чистого текста
            const cleanText = text.replace(/```\w?\n?/g, '').replace(/```/g, '');
            navigator.clipboard.writeText(cleanText).then(() => {
                alert('Текст скопирован в буфер обмена! 📋');
            });
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            addMessage('Вы', message, true);
            input.value = '';
            
            // Показываем индикатор загрузки
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message ai-message loading';
            loadingDiv.textContent = 'ИИ думает над ответом...';
            document.getElementById('messages').appendChild(loadingDiv);
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                
                // Убираем индикатор загрузки
                loadingDiv.remove();
                
                if (data.error) {
                    addMessage('ИИ', `❌ Ошибка: ${data.error}`);
                } else {
                    addMessage('ИИ', data.response);
                }
                
            } catch (error) {
                loadingDiv.remove();
                addMessage('ИИ', `❌ Ошибка соединения: ${error.message}`);
            }
        }

        function quickQuestion(question) {
            document.getElementById('messageInput').value = question;
            sendMessage();
        }

        // Обработка загрузки файлов
        document.getElementById('fileInput').addEventListener('change', handleFileUpload);

        function handleFileUpload(event) {
            const file = event.target.files[0];
            if (!file) return;
            
            if (!file.name.endsWith('.zip')) {
                alert('Пожалуйста, выберите ZIP файл');
                return;
            }
            
            uploadProject(file);
        }

        async function uploadProject(file) {
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(`Ошибка: ${data.error}`);
                } else {
                    currentProject = data.project_info;
                    showProjectInfo(data.project_info);
                    addMessage('ИИ', `✅ Проект "${file.name}" успешно загружен!\\n📊 Файлов: ${data.project_info.total_files}\\n💾 Размер: ${data.project_info.total_size_mb}MB`);
                    openTab('chat');
                }
                
            } catch (error) {
                alert(`Ошибка загрузки: ${error.message}`);
            }
        }

        function showProjectInfo(projectInfo) {
            const projectDetails = document.getElementById('projectDetails');
            const projectInfoDiv = document.getElementById('projectInfo');
            
            let html = `
                <div style="margin-bottom: 10px;">
                    <strong>📁 Название:</strong> ${projectInfo.name}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>📊 Файлов:</strong> ${projectInfo.total_files}
                </div>
                <div style="margin-bottom: 10px;">
                    <strong>💾 Размер:</strong> ${projectInfo.total_size_mb} MB
                </div>
                <div>
                    <strong>📋 Типы файлов:</strong><br>
            `;
            
            for (const [ext, count] of Object.entries(projectInfo.file_types)) {
                if (count > 0 && ext) {
                    html += `  • ${ext}: ${count} файлов<br>`;
                }
            }
            
            html += '</div>';
            
            projectDetails.innerHTML = html;
            projectInfoDiv.style.display = 'block';
        }

        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                document.getElementById('interactionsCount').textContent = data.total_interactions;
                
                const categoriesDiv = document.getElementById('knowledgeCategories');
                categoriesDiv.innerHTML = data.knowledge_categories.map(cat => 
                    `<div style="margin: 5px 0;">• ${cat}</div>`
                ).join('');
                
            } catch (error) {
                console.error('Error loading stats:', error);
                document.getElementById('knowledgeCategories').innerHTML = 'Ошибка загрузки';
            }
        }

        async function clearHistory() {
            if (!confirm('Вы уверены что хотите очистить всю историю обучения ИИ?')) return;
            
            try {
                const response = await fetch('/api/clear', {
                    method: 'POST'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('История обучения очищена!');
                    loadStats();
                } else {
                    alert(`Ошибка: ${data.error}`);
                }
                
            } catch (error) {
                alert(`Ошибка: ${error.message}`);
            }
        }

        // Отправка сообщения по Enter (Shift+Enter для новой строки)
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Drag and drop для файлов
        const uploadArea = document.querySelector('.upload-area');
        if (uploadArea) {
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.background = '#f8f9fa';
                uploadArea.style.borderColor = '#27ae60';
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.background = '';
                uploadArea.style.borderColor = '#3498db';
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.background = '';
                uploadArea.style.borderColor = '#3498db';
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    document.getElementById('fileInput').files = files;
                    handleFileUpload({ target: { files: files } });
                }
            });
        }

        // Автофокус на поле ввода
        document.getElementById('messageInput').focus();

        // Загружаем статистику при загрузке страницы
        window.addEventListener('load', loadStats);
    </script>
</body>
</html>
'''

def main():
    port = int(os.environ.get('PORT', 8000))
    server = HTTPServer(('0.0.0.0', port), AIRequestHandler)
    
    print(f"🤖 ИИ Помощник для Программирования запущен!")
    print(f"📍 Сервер доступен по адресу: http://localhost:{port}")
    print(f"📍 Или по адресу: http://0.0.0.0:{port}")
    print("\n⚡ Особенности:")
    print("• 💬 Умный чат с обучением")
    print("• 📁 Анализ ZIP проектов") 
    print("• 💻 Генерация кода")
    print("• 📊 Статистика и мониторинг")
    print("• 🎯 Адаптивный интерфейс")
    print("\nНажмите Ctrl+C для остановки сервера")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен. До свидания!")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == '__main__':
    main()