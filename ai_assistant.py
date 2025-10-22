from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import random
import os
from datetime import datetime
import requests
import urllib.parse
import nltk
import ssl

# Обход SSL для NLTK
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Загрузка данных NLTK
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class SimpleClassifier:
    """Простой классификатор на основе ключевых слов"""
    
    def __init__(self):
        self.patterns = {
            'greeting': ['привет', 'здравствуй', 'hello', 'hi', 'добрый', 'здравствуйте'],
            'farewell': ['пока', 'до свидания', 'bye', 'прощай', 'до встречи'],
            'help': ['помощь', 'help', 'что ты умеешь', 'функции'],
            'explanation': ['объясни', 'расскажи', 'что такое', 'как работает', 'означает'],
            'code_request': ['код', 'пример', 'напиши', 'сгенерируй', 'покажи код'],
            'comparison': ['разница', 'сравни', 'что лучше', 'отличие', 'отличия'],
            'problem': ['проблема', 'ошибка', 'не работает', 'помоги решить', 'исправить'],
            'opinion': ['мнение', 'думаешь', 'считаешь', 'точка зрения'],
            'learning_path': ['с чего начать', 'как учить', 'путь обучения', 'изучение'],
            'feedback': ['отлично', 'плохо', 'спасибо', 'неправильно', 'хорошо'],
            'create_code': ['создай', 'придумай', 'новый класс', 'сгенерируй класс', 'напиши класс']
        }
    
    def predict(self, text):
        """Предсказание intent'а текста"""
        text_lower = text.lower()
        intents = []
        
        for intent, keywords in self.patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                intents.append(intent)
        
        return intents if intents else ['unknown']

class AdvancedWebSearch:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def search_internet(self, query, max_results=3):
        """Умный поиск с несколькими источниками"""
        print(f"🔍 Запускаю улучшенный поиск для: {query}")
        all_results = []
        
        # 1. Пробуем Bing (самый надежный бесплатный вариант)
        try:
            bing_results = self._bing_search(query, max_results)
            all_results.extend(bing_results)
            print(f"✅ Bing найдено: {len(bing_results)} результатов")
        except Exception as e:
            print(f"❌ Bing ошибка: {e}")
        
        # 2. DuckDuckGo как запасной вариант
        if len(all_results) < max_results:
            try:
                ddg_results = self._duckduckgo_search(query, max_results - len(all_results))
                all_results.extend(ddg_results)
                print(f"✅ DuckDuckGo найдено: {len(ddg_results)} результатов")
            except Exception as e:
                print(f"❌ DuckDuckGo ошибка: {e}")
        
        # 3. Wikipedia для энциклопедических справок
        if any(word in query.lower() for word in ['что такое', 'кто такой', 'определение', 'означает']):
            try:
                wiki_result = self._wikipedia_search(query)
                if wiki_result:
                    all_results.append(wiki_result)
                    print(f"✅ Wikipedia найдено: 1 результат")
            except Exception as e:
                print(f"❌ Wikipedia ошибка: {e}")
        
        print(f"🎯 Всего найдено результатов: {len(all_results)}")
        return all_results[:max_results]
    
    def _bing_search(self, query, max_results):
        """Поиск через парсинг Bing - самый надежный метод"""
        try:
            url = "https://www.bing.com/search"
            params = {'q': query, 'count': max_results}
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            results = []
            
            # Улучшенные регулярки для парсинга Bing
            # Ищем блоки с результатами
            pattern = r'<li class="b_algo">(.*?)</li>'
            items = re.findall(pattern, response.text, re.DOTALL)
            
            for item in items[:max_results]:
                try:
                    # Извлекаем заголовок
                    title_match = re.search(r'<h2>\s*<a[^>]*>(.*?)</a>\s*</h2>', item, re.DOTALL)
                    # Извлекаем ссылку
                    url_match = re.search(r'href="([^"]+)"', item)
                    # Извлекаем описание
                    desc_match = re.search(r'<p[^>]*>(.*?)</p>', item, re.DOTALL)
                    
                    if title_match and url_match:
                        title = re.sub(r'<.*?>', '', title_match.group(1)).strip()
                        url = url_match.group(1)
                        
                        # Очищаем описание от HTML тегов
                        snippet = ""
                        if desc_match:
                            snippet = re.sub(r'<.*?>', '', desc_match.group(1)).strip()
                            snippet = re.sub(r'\s+', ' ', snippet)  # Убираем лишние пробелы
                        
                        # Проверяем, что это нормальная ссылка
                        if url.startswith('http'):
                            results.append({
                                'title': title[:100] + '...' if len(title) > 100 else title,
                                'snippet': snippet[:250] + '...' if len(snippet) > 250 else snippet,
                                'source': 'Bing',
                                'url': url
                            })
                except Exception as e:
                    print(f"⚠️ Ошибка парсинга элемента Bing: {e}")
                    continue
            
            return results
        except Exception as e:
            print(f"❌ Ошибка парсинга Bing: {e}")
            return []
    
    def _duckduckgo_search(self, query, max_results):
        """Резервный поиск через DuckDuckGo"""
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            if data.get('AbstractText'):
                results.append({
                    'title': data.get('Heading', 'Информация из интернета'),
                    'snippet': data.get('AbstractText'),
                    'source': 'DuckDuckGo',
                    'url': data.get('AbstractURL', '')
                })
            
            return results
        except Exception as e:
            print(f"❌ Ошибка DuckDuckGo: {e}")
            return []
    
    def _wikipedia_search(self, query):
        """Поиск в Wikipedia для определений"""
        try:
            # Извлекаем ключевое слово после "что такое"
            clean_query = re.sub(r'что такое|кто такой|определение|означает', '', query, flags=re.IGNORECASE).strip()
            clean_query = clean_query.split('?')[0].split('.')[0].strip()  # Убираем знаки вопроса и точки
            
            if len(clean_query) < 2:  # Слишком короткий запрос
                return None
                
            url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                snippet = data.get('extract', '')
                if snippet:
                    return {
                        'title': f"📚 {data.get('title', 'Википедия')}",
                        'snippet': snippet,
                        'source': 'Wikipedia',
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', '')
                    }
        except Exception as e:
            print(f"⚠️ Wikipedia поиск не удался: {e}")
        return None

class TextKnowledgeBase:
    """Простая текстовая база знаний в JSON файле"""
    
    def __init__(self, filename="knowledge_base.json"):
        self.filename = filename
        self.knowledge = self._load_knowledge()
    
    def _load_knowledge(self):
        """Загрузка базы знаний из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, Exception) as e:
                print(f"⚠️ Ошибка загрузки базы знаний: {e}. Создаю новую.")
                return self._create_default_structure()
        else:
            return self._create_default_structure()
    
    def _create_default_structure(self):
        """Создание структуры базы знаний по умолчанию"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "statistics": {
                "total_entries": 0,
                "categories": {},
                "last_updated": datetime.now().isoformat()
            },
            "categories": {
                "programming": [],
                "algorithms": [],
                "web": [],
                "databases": [],
                "concepts": [],
                "code_examples": [],
                "qa_pairs": []
            }
        }
    
    def save_knowledge(self):
        """Сохранение базы знаний в файл"""
        try:
            # Обновляем статистику
            self.knowledge["statistics"]["total_entries"] = sum(
                len(entries) for entries in self.knowledge["categories"].values()
            )
            self.knowledge["statistics"]["last_updated"] = datetime.now().isoformat()
            
            # Сохраняем в файл
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
            
            print(f"💾 База знаний сохранена: {self.filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка сохранения базы знаний: {e}")
            return False
    
    def add_entry(self, category, question, answer, intent=None, tags=None, confidence=1.0):
        """Добавление новой записи в базу знаний"""
        entry = {
            "id": self._generate_id(),
            "question": question,
            "answer": answer,
            "intent": intent or "general",
            "tags": tags or [],
            "confidence": confidence,
            "created_at": datetime.now().isoformat(),
            "usage_count": 0,
            "success_rate": 1.0
        }
        
        # Добавляем в категорию
        if category not in self.knowledge["categories"]:
            self.knowledge["categories"][category] = []
        
        self.knowledge["categories"][category].append(entry)
        
        print(f"✅ Добавлена запись в категорию '{category}': {question[:50]}...")
        self.save_knowledge()
        return entry["id"]
    
    def _generate_id(self):
        """Генерация уникального ID"""
        return f"entry_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
    
    def search(self, query, category=None, min_confidence=0.3, limit=5):
        """Поиск в базе знаний"""
        query_lower = query.lower()
        results = []
        
        categories_to_search = [category] if category else self.knowledge["categories"].keys()
        
        for cat in categories_to_search:
            for entry in self.knowledge["categories"].get(cat, []):
                if entry["confidence"] >= min_confidence:
                    score = self._calculate_similarity(query_lower, entry["question"].lower())
                    if score > 0.3:  # Порог схожести
                        entry['similarity_score'] = score
                        entry['category'] = cat
                        results.append(entry)
        
        # Сортировка по схожести и уверенности
        results.sort(key=lambda x: (x['similarity_score'], x['confidence']), reverse=True)
        return results[:limit]
    
    def _calculate_similarity(self, text1, text2):
        """Вычисление схожести между двумя текстами"""
        words1 = set(self._extract_keywords(text1))
        words2 = set(self._extract_keywords(text2))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _extract_keywords(self, text):
        """Извлечение ключевых слов из текста"""
        words = re.findall(r'\b[a-zа-я]{3,}\b', text.lower())
        stop_words = {'это', 'как', 'что', 'для', 'или', 'если', 'так', 'но', 'на', 'в', 'с'}
        return [word for word in words if word not in stop_words]
    
    def get_categories(self):
        """Получение списка категорий"""
        return list(self.knowledge["categories"].keys())
    
    def get_statistics(self):
        """Получение статистики базы знаний"""
        stats = self.knowledge["statistics"].copy()
        stats["categories_breakdown"] = {
            category: len(entries) 
            for category, entries in self.knowledge["categories"].items()
        }
        return stats
    
    def update_entry_usage(self, entry_id, success=True):
        """Обновление статистики использования записи"""
        for category in self.knowledge["categories"].values():
            for entry in category:
                if entry["id"] == entry_id:
                    entry["usage_count"] += 1
                    if success:
                        entry["success_rate"] = min(1.0, entry.get("success_rate", 1.0) + 0.1)
                    else:
                        entry["success_rate"] = max(0.0, entry.get("success_rate", 1.0) - 0.1)
                    self.save_knowledge()
                    return True
        return False
    
    def export_to_file(self, export_filename=None):
        """Экспорт базы знаний в читаемый текстовый файл"""
        if not export_filename:
            export_filename = f"knowledge_export_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
        
        try:
            with open(export_filename, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("📚 БАЗА ЗНАНИЙ AI ASSISTANT\n")
                f.write("=" * 60 + "\n\n")
                
                # Статистика
                stats = self.get_statistics()
                f.write(f"📊 СТАТИСТИКА:\n")
                f.write(f"• Всего записей: {stats['total_entries']}\n")
                f.write(f"• Последнее обновление: {stats['last_updated']}\n\n")
                
                # Записи по категориям
                for category, entries in self.knowledge["categories"].items():
                    if entries:
                        f.write(f"🎯 КАТЕГОРИЯ: {category.upper()}\n")
                        f.write("-" * 40 + "\n")
                        
                        for i, entry in enumerate(entries, 1):
                            f.write(f"{i}. ВОПРОС: {entry['question']}\n")
                            f.write(f"   ОТВЕТ: {entry['answer'][:100]}{'...' if len(entry['answer']) > 100 else ''}\n")
                            f.write(f"   (Использовано: {entry['usage_count']} раз, Успешность: {entry['success_rate']:.2f})\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("Конец экспорта\n")
                f.write("=" * 60 + "\n")
            
            print(f"📤 База знаний экспортирована в: {export_filename}")
            return export_filename
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            return None

class EnhancedLearningAI:
    """Улучшенная система обучения с веб-поиском как основным источником"""
    
    def __init__(self):
        self.knowledge_base = TextKnowledgeBase()
        self.classifier = SimpleClassifier()
        self.web_search = AdvancedWebSearch()  # ← ЗДЕСЬ ЗАМЕНИТЕ!
        
        # Инициализация начальными знаниями
        self._initialize_with_basic_knowledge()
    
    def _initialize_with_basic_knowledge(self):
        """Инициализация базовыми знаниями"""
        basic_knowledge = [
            # Программирование
            ("programming", "что такое python", 
             "Python - это язык программирования высокого уровня с простым и понятным синтаксисом. Используется для веб-разработки, анализа данных, искусственного интеллекта и автоматизации.", 
             "explanation", ["python", "язык", "программирование"]),
            
            ("programming", "как создать класс в python", 
             "Для создания класса в Python используйте ключевое слово class:\n\n```python\nclass MyClass:\n    def __init__(self, name):\n        self.name = name\n    \n    def greet(self):\n        print(f'Привет, {self.name}!')\n```", 
             "code_request", ["python", "класс", "ооп"]),
            
            # Приветствия
            ("qa_pairs", "привет", 
             "Привет! Я AI-помощник. Задавайте любые вопросы - найду ответы в интернете! 🤖", 
             "greeting", ["приветствие"]),
            
            ("qa_pairs", "помощь", 
             "Я могу:\n• 🔍 Искать информацию в интернете\n• 💻 Показывать примеры кода\n• 📚 Объяснять концепции\n• 🎯 Отвечать на любые вопросы\n\nПросто спросите о чем угодно! 💡", 
             "help", ["помощь", "функции"]),
        ]
        
        # Добавляем только если база пустая
        if self.knowledge_base.get_statistics()["total_entries"] == 0:
            print("📖 Инициализация базовыми знаниями...")
            for category, question, answer, intent, tags in basic_knowledge:
                self.knowledge_base.add_entry(category, question, answer, intent, tags)
    
    def find_best_response(self, user_message, intent, entities, use_web_search=True):
        """Поиск лучшего ответа - ВСЕГДА используем веб-поиск если не нашли в базе"""
        
        # Сначала быстрая проверка в локальной базе знаний
        search_results = self.knowledge_base.search(user_message, min_confidence=0.5)
        
        if search_results and search_results[0].get('similarity_score', 0) > 0.7:
            best_match = search_results[0]
            self.knowledge_base.update_entry_usage(best_match["id"], success=True)
            confidence = best_match.get("confidence", 1.0) * best_match.get("success_rate", 1.0)
            return best_match["answer"], confidence, "knowledge_base"
        
        # ВСЕГДА пытаемся найти ответ в интернете
        print(f"🔍 Ищу в интернете: {user_message}")
        web_answer, web_source = self._web_search_and_save(user_message, intent, entities)
        
        if web_answer:
            return web_answer, 0.8, web_source
        
        # Если даже интернет не помог, генерируем умный ответ
        fallback_answer = self._generate_web_fallback_response(user_message, intent)
        return fallback_answer, 0.3, "generated"
    
    def _web_search_and_save(self, user_message, intent, entities):
        """Поиск в интернете и сохранение в базу знаний"""
        try:
            print(f"🌐 Запускаю улучшенный поиск для: {user_message}")
            search_results = self.web_search.search_internet(user_message, max_results=3)
        
            if search_results:
                # Формируем красивый ответ
                answer_parts = ["**🔍 Найдена информация по вашему запросу:**\n"]
            
                for i, result in enumerate(search_results, 1):
                    title = result.get('title', 'Без названия')
                    snippet = result.get('snippet', 'Описание отсутствует')
                    source = result.get('source', 'Неизвестный источник')
                
                    # Ограничиваем длину сниппета
                    if len(snippet) > 300:
                        snippet = snippet[:300] + "..."
                
                    answer_parts.append(f"\n**{i}. {title}**")
                    answer_parts.append(f"{snippet}")
                    if result.get('url'):
                        answer_parts.append(f"*🔗 Источник: {source}*")
                    answer_parts.append("")  # пустая строка для разделения
            
                full_answer = "\n".join(answer_parts)
            
                # Сохраняем в базу знаний для будущего использования
                tags = self._extract_tags_from_query(user_message)
                self.knowledge_base.add_entry(
                    category="web_knowledge",
                    question=user_message,
                    answer=full_answer,
                    intent=intent,
                    tags=tags,
                    confidence=0.9
                )
            
                print(f"✅ Найден ответ в интернете для: {user_message[:50]}...")
                return full_answer, "web_search"
            else:
                print(f"❌ Не найдено результатов для: {user_message}")
                # Возвращаем информационный ответ
                info_answer = (
                    f"**🔍 По запросу '{user_message}' не найдено точных совпадений.**\n\n"
                    f"*Возможные причины:*\n"
                    f"• Вопрос слишком специфический\n"
                    f"• Требуется уточнение формулировки\n"
                    f"• Информация может быть ограниченной\n\n"
                    f"Попробуйте переформулировать вопрос или задать его более конкретно."
                )
                return info_answer, "generated"
        
        except Exception as e:
            print(f"❌ Ошибка веб-поиска: {e}")
            error_answer = (
                f"**⚠️ Произошла ошибка при поиске**\n\n"
                f"Не удалось выполнить поиск в интернете. "
                f"Попробуйте повторить запрос позже или задать другой вопрос."
            )
            return error_answer, "generated"
    
    def _generate_web_fallback_response(self, user_message, intent):
        """Генерация ответа когда даже интернет не помог"""
        responses = [
            f"🤔 **Вопрос:** {user_message}\n\nК сожалению, не смог найти точный ответ в интернете. Попробуйте переформулировать вопрос или задать его более конкретно.",
            f"🔍 **Поиск:** {user_message}\n\nНе нашел подходящей информации по вашему запросу. Возможно, вопрос слишком специфический или требует уточнения.",
            f"💡 **Запрос:** {user_message}\n\nПока не могу найти ответ на этот вопрос. Попробуйте разбить его на несколько более простых вопросов."
        ]
        
        # Сохраняем вопрос для будущего изучения
        tags = self._extract_tags_from_query(user_message)
        self.knowledge_base.add_entry(
            category="unanswered",
            question=user_message,
            answer="ВОПРОС ТРЕБУЕТ ОТВЕТА - не найден в интернете",
            intent=intent,
            tags=tags,
            confidence=0.1
        )
        
        return random.choice(responses)
    
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
            'successful_searches': 0
        }
    
    def generate_smart_response(self, message):
        # Всегда сначала проверяем базовые интенты
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hello', 'hi']):
            return "Привет! 🖐️ Я AI-помощник с доступом к интернету. Задавайте любой вопрос - найду актуальную информацию! 🌐"
        
        if any(word in message_lower for word in ['пока', 'до свидания', 'bye']):
            return "До свидания! Возвращайтесь с новыми вопросами! 👋"
        
        if any(word in message_lower for word in ['помощь', 'help', 'что ты умеешь']):
            return "🦾 **Мои возможности:**\n\n• 🔍 **Поиск в интернете** - отвечаю на любые вопросы\n• 💻 **Программирование** - код, алгоритмы, технологии\n• 📚 **Объяснения** - сложные концепции простыми словами\n• 🎯 **Факты** - актуальная информация из сети\n\nПросто спросите о чем угодно! 💫"
        
        # Используем EnhancedLearningAI который ВСЕГДА ищет в интернете
        intents = self.learning_ai.classifier.predict(message)
        entities = self.extract_entities(message)
        primary_intent = intents[0] if intents else "unknown"
        
        print(f"🔍 Начинаю поиск для: {message}")
        response, confidence, source = self.learning_ai.find_best_response(
            message, primary_intent, entities, use_web_search=True
        )
        
        # Обновляем статистику
        self.learning_stats['conversations_processed'] += 1
        self.learning_stats['knowledge_base_entries'] = (
            self.learning_ai.get_knowledge_stats()["total_entries"]
        )
        
        if source == "web_search":
            self.learning_stats['web_searches'] += 1
            self.learning_stats['successful_searches'] += 1
            print(f"✅ Найден ответ через веб-поиск: {message[:30]}...")
        else:
            print(f"💡 Ответ из базы знаний: {message[:30]}...")
        
        # Сохраняем в историю
        self.conversation_history.append({
            'message': message,
            'response': response,
            'source': source,
            'confidence': confidence,
            'timestamp': datetime.now()
        })
        
        # Ограничиваем историю
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-20:]
        
        # Добавляем информацию об источнике в ответ
        source_info = {
            "knowledge_base": "\n\n💾 *Ответ из базы знаний*",
            "web_search": "\n\n🌐 *Информация найдена в интернете*", 
            "generated": "\n\n🤖 *Сгенерированный ответ*"
        }
        
        response += source_info.get(source, "")
        
        return response
    
    def extract_entities(self, message):
        """Простое извлечение сущностей"""
        return {'languages': [], 'concepts': []}
    
    def get_learning_stats(self):
        """Получение статистики"""
        total_searches = max(1, self.learning_stats['web_searches'])
        success_rate = (self.learning_stats['successful_searches'] / total_searches) * 100
        
        return {
            'total_conversations': self.learning_stats['conversations_processed'],
            'knowledge_base_entries': self.learning_stats['knowledge_base_entries'],
            'web_searches': self.learning_stats['web_searches'],
            'successful_searches': self.learning_stats['successful_searches'],
            'success_rate': round(success_rate, 1),
            'conversation_history_length': len(self.conversation_history)
        }
    
    def export_knowledge_base(self):
        """Экспорт базы знаний"""
        return self.learning_ai.export_knowledge()
    
    def get_conversation_history(self, limit=10):
        """Получение истории разговоров"""
        return self.conversation_history[-limit:] if self.conversation_history else []
    
    def clear_conversation_history(self):
        """Очистка истории разговоров"""
        self.conversation_history.clear()
        return "История разговоров очищена"


class AIHandler(BaseHTTPRequestHandler):
    ai = SmartAI()
    
    def do_GET(self):
        if self.path == '/':
            self._serve_html()
        elif self.path == '/stats':
            self._serve_stats()
        elif self.path == '/history':
            self._serve_history()
        elif self.path == '/export':
            self._export_knowledge()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/chat':
            self._handle_chat()
        elif self.path == '/clear-history':
            self._clear_history()
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
                
                .search-status {
                    background: linear-gradient(135deg, #ffd700, #ff8c00);
                    color: white;
                    padding: 10px 16px;
                    border-radius: 18px;
                    margin: 10px 0;
                    max-width: 200px;
                    border-bottom-left-radius: 5px;
                    animation: pulse 1.5s infinite;
                    font-weight: bold;
                }
                
                @keyframes pulse {
                    0% { opacity: 0.7; }
                    50% { opacity: 1; }
                    100% { opacity: 0.7; }
                }
                
                .typing-message {
                    background: white;
                    color: #333;
                    border: 2px solid #e9ecef;
                    border-bottom-left-radius: 5px;
                    margin: 10px 0;
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 18px;
                }
                
                .message-final {
                    background: white;
                    color: #333;
                    border: 2px solid #e9ecef;
                    border-bottom-left-radius: 5px;
                    margin: 10px 0;
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 18px;
                    animation: slideIn 0.3s ease;
                }
                
                @keyframes slideIn {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
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
                    <p>Задайте вопрос - найду ответ в интернете!</p>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai-message">
                        <strong>Привет! Я ваш AI-помощник с доступом к интернету 🌐</strong><br><br>
                        Просто задайте любой вопрос, и я найду актуальную информацию!<br>
                        • 🔍 Поиск в реальном времени<br>
                        • 💻 Ответы на любые темы<br>
                        • 🚀 Быстрые результаты
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
                    <input type="text" class="chat-input" id="messageInput" placeholder="Введите ваш вопрос..." autocomplete="off">
                    <button class="send-button" onclick="sendMessage()">Отправить</button>
                </div>
            </div>

            <script>
                const chatMessages = document.getElementById('chatMessages');
                const messageInput = document.getElementById('messageInput');
                const typingIndicator = document.getElementById('typingIndicator');
                let isWaitingForResponse = false;
                
                function addMessage(text, isUser, messageType = 'final') {
                    const messageDiv = document.createElement('div');
                    
                    if (messageType === 'search') {
                        messageDiv.className = 'search-status';
                        messageDiv.innerHTML = `🔍 ${text}`;
                    } else if (messageType === 'typing') {
                        messageDiv.className = 'typing-message';
                        messageDiv.innerHTML = text;
                    } else {
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
                    }
                    
                    chatMessages.appendChild(messageDiv);
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                    return messageDiv;
                }
                
                function showTyping() {
                    typingIndicator.style.display = 'block';
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
                
                function hideTyping() {
                    typingIndicator.style.display = 'none';
                }
                
                function typeText(element, text, speed = 10, callback = null) {
                    let i = 0;
                    element.innerHTML = '';
                    
                    function typeChar() {
                        if (i < text.length) {
                            // Добавляем символ
                            if (text[i] === '\\n') {
                                element.innerHTML += '<br>';
                            } else {
                                element.innerHTML += text[i];
                            }
                            i++;
                            
                            // Прокручиваем вниз
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                            
                            // Случайная скорость для естественности
                            const variation = Math.random() * 20 - 10;
                            setTimeout(typeChar, speed + variation);
                        } else if (callback) {
                            callback();
                        }
                    }
                    
                    typeChar();
                }
                
                async function sendMessage() {
                    if (isWaitingForResponse) return;
                    
                    const message = messageInput.value.trim();
                    if (!message) return;
                    
                    // Clear input
                    messageInput.value = '';
                    isWaitingForResponse = true;
                    
                    // Add user message
                    addMessage(message, true);
                    
                    // Show searching status
                    const searchMessage = addMessage('Поиск в интернете...', false, 'search');
                    
                    try {
                        const response = await fetch('/chat', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ message: message })
                        });
                        
                        const data = await response.json();
                        
                        // Remove search message
                        searchMessage.remove();
                        
                        // Add AI response with typing effect
                        const aiMessage = addMessage('', false, 'typing');
                        showTyping();
                        
                        // Type out the response
                        typeText(aiMessage, data.response, 5, () => {
                            // Convert to final message after typing
                            aiMessage.className = 'message ai-message';
                            const time = new Date().toLocaleTimeString('ru-RU', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                            });
                            aiMessage.innerHTML = aiMessage.innerHTML + `<div class="message-time">${time}</div>`;
                            hideTyping();
                            isWaitingForResponse = false;
                        });
                        
                    } catch (error) {
                        // Remove search message
                        searchMessage.remove();
                        hideTyping();
                        
                        // Show error
                        addMessage('❌ Ошибка соединения с сервером. Попробуйте еще раз.', false);
                        console.error('Error:', error);
                        isWaitingForResponse = false;
                    }
                }
                
                // Send message on Enter key
                messageInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !isWaitingForResponse) {
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
    
    def _serve_history(self):
        """Отдача истории разговоров"""
        history = self.ai.get_conversation_history(limit=20)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        self.wfile.write(json.dumps(history).encode('utf-8'))
    
    def _export_knowledge(self):
        """Экспорт базы знаний"""
        export_file = self.ai.export_knowledge_base()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "export_file": export_file}
        self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def _clear_history(self):
        """Очистка истории разговоров"""
        result = self.ai.clear_conversation_history()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "message": result}
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
