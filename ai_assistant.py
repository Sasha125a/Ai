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
import zipfile
import tempfile
from pathlib import Path

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
        self.search_engines = ['bing', 'duckduckgo', 'wikipedia', 'stackoverflow']
    
    def search_internet(self, query, max_results=5):
        """Умный поиск с анализом типа запроса и специализированными источниками"""
        print(f"🔍 Запускаю точный поиск для: '{query}'")
        
        # Анализируем тип запроса для оптимизации поиска
        query_type = self._analyze_query_type(query)
        print(f"🎯 Тип запроса: {query_type}")
        
        # Выбираем стратегию поиска в зависимости от типа запроса
        search_strategy = self._get_search_strategy(query_type)
        
        all_results = []
        used_engines = set()
        
        # Выполняем поиск по стратегии
        for engine in search_strategy:
            if len(all_results) >= max_results:
                break
                
            if engine not in used_engines:
                try:
                    results = self._search_with_engine(engine, query, query_type, max_results - len(all_results))
                    if results:
                        all_results.extend(results)
                        used_engines.add(engine)
                        print(f"✅ {engine.capitalize()} найдено: {len(results)} результатов")
                except Exception as e:
                    print(f"❌ {engine.capitalize()} ошибка: {e}")
        
        # Если результатов мало, пробуем остальные движки
        if len(all_results) < max_results:
            remaining_engines = [e for e in self.search_engines if e not in used_engines]
            for engine in remaining_engines:
                if len(all_results) >= max_results:
                    break
                try:
                    results = self._search_with_engine(engine, query, query_type, max_results - len(all_results))
                    if results:
                        all_results.extend(results)
                        print(f"✅ {engine.capitalize()} (резерв) найдено: {len(results)} результатов")
                except Exception as e:
                    print(f"❌ {engine.capitalize()} ошибка: {e}")
        
        # Сортируем результаты по релевантности
        sorted_results = self._sort_by_relevance(query, all_results)
        
        print(f"🎯 Всего найдено результатов: {len(sorted_results)}")
        return sorted_results[:max_results]
    
    def _analyze_query_type(self, query):
        """Анализирует тип запроса для оптимизации поиска"""
        query_lower = query.lower()
        
        # Программирование и код
        if any(word in query_lower for word in ['код', 'программир', 'функция', 'класс', 'ошибка', 'python', 'javascript', 'java']):
            return 'programming'
        
        # Определения и объяснения
        elif any(phrase in query_lower for phrase in ['что такое', 'кто такой', 'определение', 'означает', 'объясни']):
            return 'definition'
        
        # Как сделать (инструкции)
        elif any(phrase in query_lower for phrase in ['как сделать', 'как создать', 'как настроить', 'как использовать', 'инструкция']):
            return 'howto'
        
        # Сравнение
        elif any(word in query_lower for word in ['разница', 'сравнение', 'лучше', 'хуже', 'vs', 'versus']):
            return 'comparison'
        
        # Технические вопросы
        elif any(word in query_lower for word in ['ошибка', 'проблема', 'не работает', 'исправить', 'баг']):
            return 'technical'
        
        # Факты и информация
        elif any(word in query_lower for word in ['сколько', 'когда', 'где', 'почему', 'зачем']):
            return 'fact'
        
        else:
            return 'general'
    
    def _get_search_strategy(self, query_type):
        """Возвращает оптимальную стратегию поиска для типа запроса"""
        strategies = {
            'programming': ['stackoverflow', 'bing', 'duckduckgo'],
            'definition': ['wikipedia', 'bing', 'duckduckgo'],
            'howto': ['bing', 'stackoverflow', 'duckduckgo'],
            'comparison': ['bing', 'duckduckgo'],
            'technical': ['stackoverflow', 'bing', 'duckduckgo'],
            'fact': ['bing', 'wikipedia', 'duckduckgo'],
            'general': ['bing', 'duckduckgo', 'wikipedia']
        }
        return strategies.get(query_type, ['bing', 'duckduckgo'])
    
    def _search_with_engine(self, engine, query, query_type, max_results):
        """Поиск с использованием конкретного движка"""
        if engine == 'bing':
            return self._bing_search(query, max_results, query_type)
        elif engine == 'duckduckgo':
            return self._duckduckgo_search(query, max_results)
        elif engine == 'wikipedia':
            return self._wikipedia_search(query, max_results)
        elif engine == 'stackoverflow':
            return self._stackoverflow_search(query, max_results)
        return []
    
    def _bing_search(self, query, max_results, query_type):
        """Улучшенный поиск через Bing с оптимизацией запроса"""
        try:
            # Оптимизируем запрос для Bing
            optimized_query = self._optimize_query(query, query_type, 'bing')
            
            url = "https://www.bing.com/search"
            params = {'q': optimized_query, 'count': max_results + 2}  # Берем немного больше для фильтрации
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            results = []
            
            # Несколько паттернов для надежного парсинга
            patterns = [
                r'<li class="b_algo">(.*?)</li>',
                r'<li class="b_algo"[^>]*>(.*?)</li>',
                r'<div class="b_algo">(.*?)</div>'
            ]
            
            for pattern in patterns:
                items = re.findall(pattern, response.text, re.DOTALL)
                if items:
                    break
            
            for item in items[:max_results + 2]:
                try:
                    # Извлекаем заголовок
                    title_match = re.search(r'<h2>\s*<a[^>]*>(.*?)</a>\s*</h2>', item, re.DOTALL)
                    if not title_match:
                        title_match = re.search(r'<a[^>]*>(.*?)</a>', item, re.DOTALL)
                    
                    # Извлекаем ссылку
                    url_match = re.search(r'href="([^"]+)"', item)
                    
                    # Извлекаем описание
                    desc_match = re.search(r'<p[^>]*>(.*?)</p>', item, re.DOTALL)
                    
                    if title_match and url_match:
                        title = re.sub(r'<.*?>', '', title_match.group(1)).strip()
                        url = url_match.group(1)
                        
                        # Очищаем описание
                        snippet = ""
                        if desc_match:
                            snippet = re.sub(r'<.*?>', '', desc_match.group(1)).strip()
                            snippet = re.sub(r'\s+', ' ', snippet)
                        
                        # Проверяем релевантность
                        if (self._is_relevant_result(query, title, snippet) and 
                            url.startswith('http') and
                            not any(domain in url for domain in ['bing.com', 'microsoft.com'])):
                            
                            results.append({
                                'title': title[:120],
                                'snippet': snippet[:350],
                                'source': 'Bing',
                                'url': url,
                                'relevance_score': self._calculate_relevance(query, title, snippet)
                            })
                except Exception as e:
                    continue
            
            return results[:max_results]
        except Exception as e:
            print(f"❌ Ошибка парсинга Bing: {e}")
            return []
    
    def _duckduckgo_search(self, query, max_results):
        """Улучшенный поиск через DuckDuckGo"""
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
                    'url': data.get('AbstractURL', ''),
                    'relevance_score': 0.8
                })
            
            # Также получаем связанные темы
            if data.get('RelatedTopics'):
                for topic in data.get('RelatedTopics', [])[:max_results-1]:
                    if topic.get('Text') and topic.get('FirstURL'):
                        results.append({
                            'title': topic.get('Text', '')[:100],
                            'snippet': topic.get('Text', ''),
                            'source': 'DuckDuckGo',
                            'url': topic.get('FirstURL', ''),
                            'relevance_score': 0.6
                        })
            
            return results[:max_results]
        except Exception as e:
            print(f"❌ Ошибка DuckDuckGo: {e}")
            return []
    
    def _wikipedia_search(self, query, max_results):
        """Поиск в Wikipedia с улучшенным извлечением ключевых слов"""
        try:
            # Улучшенное извлечение ключевого слова
            clean_query = self._extract_main_keyword(query)
            if not clean_query or len(clean_query) < 2:
                return []
                
            url = f"https://ru.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
            response = self.session.get(url, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                snippet = data.get('extract', '')
                if snippet:
                    return [{
                        'title': f"📚 {data.get('title', 'Википедия')}",
                        'snippet': snippet,
                        'source': 'Wikipedia',
                        'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                        'relevance_score': 0.9
                    }]
        except Exception as e:
            print(f"⚠️ Wikipedia поиск не удался: {e}")
        return []
    
    def _stackoverflow_search(self, query, max_results):
        """Поиск в StackOverflow для программистских вопросов"""
        try:
            # Оптимизируем запрос для StackOverflow
            so_query = re.sub(r'[^\w\s]', ' ', query)  # Убираем спецсимволы
            so_query = ' '.join(so_query.split()[:6])  # Берем первые 6 слов
            
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                'order': 'desc',
                'sort': 'relevance',
                'q': so_query,
                'site': 'stackoverflow',
                'filter': 'withbody',
                'pagesize': max_results
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            results = []
            for item in data.get('items', [])[:max_results]:
                # Извлекаем чистый текст из HTML
                body = re.sub(r'<.*?>', '', item.get('body', ''))
                snippet = body[:300] + '...' if len(body) > 300 else body
                
                results.append({
                    'title': item.get('title', ''),
                    'snippet': snippet,
                    'source': 'StackOverflow',
                    'url': item.get('link', ''),
                    'relevance_score': 0.85
                })
            
            return results
        except Exception as e:
            print(f"❌ Ошибка StackOverflow: {e}")
            return []
    
    def _optimize_query(self, query, query_type, engine):
        """Оптимизирует запрос для конкретного поискового движка"""
        # Убираем лишние слова
        stop_words = {'пожалуйста', 'можете', 'расскажите', 'подскажите'}
        words = [word for word in query.split() if word.lower() not in stop_words]
        base_query = ' '.join(words)
        
        # Добавляем модификаторы в зависимости от типа запроса и движка
        if query_type == 'programming' and engine == 'bing':
            return base_query + ' site:stackoverflow.com OR site:github.com'
        elif query_type == 'definition':
            return f'"{base_query}" определение'
        elif query_type == 'howto':
            return base_query + ' инструкция руководство'
        
        return base_query
    
    def _extract_main_keyword(self, query):
        """Извлекает основное ключевое слово из запроса"""
        # Убираем вопросительные слова
        query = re.sub(r'что такое|кто такой|определение|означает|объясни', '', query, flags=re.IGNORECASE)
        # Убираем знаки препинания в конце
        query = re.sub(r'[?.!]$', '', query.strip())
        # Берем первое существительное или все, если короткий запрос
        words = query.strip().split()
        return words[0] if words else ""
    
    def _is_relevant_result(self, query, title, snippet):
        """Проверяет релевантность результата"""
        query_words = set(query.lower().split())
        content = (title + ' ' + snippet).lower()
        
        # Считаем количество совпадающих слов
        matches = sum(1 for word in query_words if word in content and len(word) > 2)
        return matches >= max(1, len(query_words) // 2)
    
    def _calculate_relevance(self, query, title, snippet):
        """Вычисляет оценку релевантности от 0 до 1"""
        query_words = set(word for word in query.lower().split() if len(word) > 2)
        if not query_words:
            return 0.5
            
        content = (title + ' ' + snippet).lower()
        
        # Считаем совпадения в заголовке (более важно)
        title_matches = sum(1 for word in query_words if word in title.lower())
        # Считаем совпадения в сниппете
        snippet_matches = sum(1 for word in query_words if word in snippet.lower())
        
        total_score = (title_matches * 2 + snippet_matches) / (len(query_words) * 3)
        return min(1.0, total_score)
    
    def _sort_by_relevance(self, query, results):
        """Сортирует результаты по релевантности"""
        for result in results:
            if 'relevance_score' not in result:
                result['relevance_score'] = self._calculate_relevance(query, result['title'], result['snippet'])
        
        return sorted(results, key=lambda x: x.get('relevance_score', 0), reverse=True)
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

class ZipAnalyzer:
    """Класс для анализа ZIP-архивов"""
    
    def __init__(self):
        self.temp_dir = None
    
    def analyze_zip(self, zip_file_path):
        """Анализирует ZIP-архив и возвращает структуру"""
        try:
            if not os.path.exists(zip_file_path):
                return {"error": "Файл не найден"}
            
            # Создаем временную директорию для распаковки
            self.temp_dir = tempfile.mkdtemp()
            
            structure = {
                "filename": os.path.basename(zip_file_path),
                "total_size": os.path.getsize(zip_file_path),
                "file_count": 0,
                "folder_count": 0,
                "structure": [],
                "file_types": {},
                "created_at": datetime.now().isoformat()
            }
            
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Получаем список всех файлов
                file_list = zip_ref.namelist()
                structure["file_count"] = len(file_list)
                
                # Анализируем структуру
                structure["structure"] = self._build_tree_structure(file_list)
                structure["folder_count"] = self._count_folders(file_list)
                structure["file_types"] = self._analyze_file_types(file_list)
                
                # Распаковываем для детального анализа
                zip_ref.extractall(self.temp_dir)
                
                # Добавляем информацию о содержимом файлов
                structure["content_analysis"] = self._analyze_contents(self.temp_dir)
            
            return structure
            
        except zipfile.BadZipFile:
            return {"error": "Некорректный ZIP-файл"}
        except Exception as e:
            return {"error": f"Ошибка анализа: {str(e)}"}
    
    def _build_tree_structure(self, file_list):
        """Строит древовидную структуру файлов"""
        root = {}
        
        for file_path in file_list:
            # Пропускаем служебные файлы macOS
            if '__MACOSX' in file_path or '.DS_Store' in file_path:
                continue
                
            parts = file_path.split('/')
            current = root
            
            for i, part in enumerate(parts):
                if not part:  # Пустые части (например, от завершающего /)
                    continue
                    
                if i == len(parts) - 1:
                    # Это файл
                    current[part] = {"type": "file", "path": file_path}
                else:
                    # Это папка
                    if part not in current:
                        current[part] = {"type": "folder", "children": {}}
                    current = current[part]["children"]
        
        return self._format_tree(root)
    
    def _format_tree(self, node, level=0):
        """Форматирует дерево в читаемый вид"""
        result = []
        indent = "  " * level
        
        for name, info in sorted(node.items()):
            if info["type"] == "folder":
                result.append(f"{indent}📁 {name}/")
                result.extend(self._format_tree(info["children"], level + 1))
            else:
                result.append(f"{indent}📄 {name}")
        
        return result
    
    def _count_folders(self, file_list):
        """Считает количество уникальных папок"""
        folders = set()
        for file_path in file_list:
            dir_path = os.path.dirname(file_path)
            if dir_path:  # Не корневая директория
                folders.add(dir_path)
        return len(folders)
    
    def _analyze_file_types(self, file_list):
        """Анализирует типы файлов в архиве"""
        file_types = {}
        for file_path in file_list:
            if not file_path.endswith('/'):  # Это не папка
                ext = os.path.splitext(file_path)[1].lower()
                if not ext:
                    ext = "без расширения"
                file_types[ext] = file_types.get(ext, 0) + 1
        return dict(sorted(file_types.items(), key=lambda x: x[1], reverse=True))
    
    def _analyze_contents(self, extract_path):
        """Анализирует содержимое файлов"""
        analysis = {
            "readme_files": [],
            "code_files": [],
            "config_files": [],
            "image_files": [],
            "document_files": []
        }
        
        code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.html', '.css', '.php', '.rb', '.go', '.rs'}
        config_extensions = {'.json', '.xml', '.yaml', '.yml', '.ini', '.cfg', '.conf', '.toml'}
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        document_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx', '.rtf'}
        
        for root_dir, dirs, files in os.walk(extract_path):
            for file in files:
                file_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(file_path, extract_path)
                ext = os.path.splitext(file)[1].lower()
                
                # Пропускаем системные файлы
                if file.startswith('.') or '__MACOSX' in rel_path:
                    continue
                
                # Классифицируем файлы
                if file.lower() in ['readme', 'readme.txt', 'readme.md', 'readme.rst']:
                    analysis["readme_files"].append(rel_path)
                elif ext in code_extensions:
                    analysis["code_files"].append(rel_path)
                elif ext in config_extensions:
                    analysis["config_files"].append(rel_path)
                elif ext in image_extensions:
                    analysis["image_files"].append(rel_path)
                elif ext in document_extensions:
                    analysis["document_files"].append(rel_path)
        
        return analysis
    
    def read_file_content(self, file_path, max_lines=50):
        """Читает содержимое файла с ограничением по количеству строк"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        lines.append("... (файл слишком большой, показаны первые 50 строк)")
                        break
                    lines.append(line.rstrip())
                return lines
        except:
            try:
                with open(file_path, 'r', encoding='cp1251', errors='ignore') as f:
                    lines = []
                    for i, line in enumerate(f):
                        if i >= max_lines:
                            lines.append("... (файл слишком большой, показаны первые 50 строк)")
                            break
                        lines.append(line.rstrip())
                    return lines
            except:
                return ["[Не удалось прочитать файл - бинарный файл или неизвестная кодировка]"]
    
    def cleanup(self):
        """Очищает временные файлы"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None

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
        self.zip_analyzer = ZipAnalyzer()
        self.learning_stats = {
            'conversations_processed': 0,
            'knowledge_base_entries': 0,
            'web_searches': 0,
            'successful_searches': 0,
            'zip_files_analyzed': 0
        }
    
    def generate_smart_response(self, message):
        """Основной метод генерации ответов - исправленная версия"""
        # Всегда сначала проверяем базовые интенты
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['привет', 'здравствуй', 'hello', 'hi']):
            return "Привет! 🖐️ Я AI-помощник с доступом к интернете. Задавайте любой вопрос - найду актуальную информацию! 🌐"
        
        if any(word in message_lower for word in ['пока', 'до свидания', 'bye']):
            return "До свидания! Возвращайтесь с новыми вопросами! 👋"
        
        if any(word in message_lower for word in ['помощь', 'help', 'что ты умеешь']):
            return self._get_help_response()
        
        # Проверяем запросы на анализ ZIP-файлов (только если явно упоминаются)
        if any(word in message_lower for word in ['zip', 'архив', 'структур', 'распакуй', 'проанализируй архив']):
            zip_response = self._handle_zip_analysis_request(message)
            if zip_response:
                return zip_response
        
        # ИСПРАВЛЕНИЕ: Используем обычный поиск для всех остальных запросов
        print(f"🔍 Обрабатываю запрос: {message}")
        
        intents = self.learning_ai.classifier.predict(message)
        entities = self.extract_entities(message)
        primary_intent = intents[0] if intents else "unknown"
        
        # Всегда пытаемся найти ответ через EnhancedLearningAI
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
        
        return response
    
    def _get_help_response(self):
        """Возвращает сообщение помощи"""
        return """🦾 **Мои возможности:**

• 🔍 **Поиск в интернете** - отвечаю на любые вопросы
• 💻 **Программирование** - код, алгоритмы, технологии  
• 📚 **Объяснения** - сложные концепции простыми словами
• 🎯 **Факты** - актуальная информация из сети
• 📦 **Анализ ZIP-архивов** - структура и содержимое файлов

**Как использовать:**
• Просто задайте вопрос - я найду ответ в интернете!
• Для анализа архивов: прикрепите ZIP-файл и напишите "проанализируй этот архив"
• Можно одновременно отправлять файлы и текстовые запросы

Просто спросите о чем угодно! 💫"""
    
    def _handle_zip_analysis_request(self, message):
        """Обрабатывает запросы на анализ ZIP-файлов"""
        # Только информационное сообщение, если файл не прикреплен
        return """📦 **Анализ ZIP-архивов**

Я могу проанализировать ZIP-файл и показать:
• 📁 Полную структуру папок и файлов
• 📊 Статистику по типам файлов  
• 🔍 Содержимое текстовых файлов
• 💻 Анализ кода (Python, JS, Java и др.)

**Как использовать:**
1. Нажмите на скрепку 📎 рядом с полем ввода
2. Выберите ZIP-файл для загрузки
3. Напишите запрос (например, "проанализируй этот архив")
4. Нажмите "Отправить"

Я автоматически распаковываю архив и показываю подробный анализ!"""
    
    def analyze_uploaded_zip(self, zip_file_path):
        """Анализирует загруженный ZIP-файл"""
        try:
            print(f"📦 Анализирую ZIP-файл: {zip_file_path}")
            
            # Анализируем структуру
            analysis = self.zip_analyzer.analyze_zip(zip_file_path)
            
            if "error" in analysis:
                return f"❌ Ошибка анализа: {analysis['error']}"
            
            # Формируем красивый отчет
            report = self._format_zip_analysis_report(analysis)
            
            # Обновляем статистику
            self.learning_stats['zip_files_analyzed'] += 1
            
            # Очищаем временные файлы
            self.zip_analyzer.cleanup()
            
            return report
            
        except Exception as e:
            self.zip_analyzer.cleanup()
            return f"❌ Ошибка при анализе ZIP-файла: {str(e)}"
    
    def _format_zip_analysis_report(self, analysis):
        """Форматирует отчет об анализе ZIP-файла"""
        report = []
        
        # Заголовок
        report.append(f"📦 **АНАЛИЗ АРХИВА: {analysis['filename']}**")
        report.append("=" * 50)
        
        # Основная статистика
        report.append("\n📊 **ОСНОВНАЯ СТАТИСТИКА:**")
        report.append(f"• 📁 Всего файлов: {analysis['file_count']}")
        report.append(f"• 📂 Папок: {analysis['folder_count']}")
        report.append(f"• 💾 Размер архива: {self._format_size(analysis['total_size'])}")
        
        # Типы файлов
        if analysis['file_types']:
            report.append("\n📄 **ТИПЫ ФАЙЛОВ:**")
            for ext, count in analysis['file_types'].items():
                report.append(f"• `{ext if ext else 'без расшир'}`: {count} файл(ов)")
        
        # Структура
        report.append("\n📁 **СТРУКТУРА ПАПОК:**")
        if analysis['structure']:
            for line in analysis['structure']:
                report.append(line)
        else:
            report.append("  (архив пуст)")
        
        # Анализ содержимого
        content = analysis.get('content_analysis', {})
        if any(content.values()):
            report.append("\n🔍 **КАТЕГОРИИ ФАЙЛОВ:**")
            
            if content['readme_files']:
                report.append("\n📖 **README файлы:**")
                for file in content['readme_files'][:3]:
                    report.append(f"  • {file}")
            
            if content['code_files']:
                report.append("\n💻 **Файлы с кодом:**")
                for file in content['code_files'][:5]:
                    report.append(f"  • {file}")
                
                # Показываем содержимое первого Python файла если есть
                py_files = [f for f in content['code_files'] if f.endswith('.py')]
                if py_files:
                    first_py = py_files[0]
                    full_path = os.path.join(self.zip_analyzer.temp_dir, first_py)
                    content_lines = self.zip_analyzer.read_file_content(full_path, 10)
                    
                    report.append(f"\n**Содержимое {first_py} (первые 10 строк):**")
                    report.append("```python")
                    report.extend(content_lines)
                    report.append("```")
            
            if content['config_files']:
                report.append("\n⚙️ **Конфигурационные файлы:**")
                for file in content['config_files'][:3]:
                    report.append(f"  • {file}")
        
        report.append("\n" + "=" * 50)
        report.append("✅ Анализ завершен!")
        
        return "\n".join(report)
    
    def _format_size(self, size_bytes):
        """Форматирует размер в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
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
            'conversation_history_length': len(self.conversation_history),
            'zip_files_analyzed': self.learning_stats['zip_files_analyzed']
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
        elif self.path == '/upload':
            self._serve_upload_form()
        elif self.path.startswith('/download/'):
            self._serve_file_download()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path == '/chat':
            self._handle_chat()
        elif self.path == '/clear-history':
            self._clear_history()
        elif self.path == '/upload-file':
            self._handle_file_upload()
        elif self.path == '/analyze-with-file':
            self._handle_analysis_with_file()
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
                    position: relative;
                }
                
                .chat-header h1 {
                    font-size: 1.5em;
                    margin-bottom: 5px;
                }
                
                .chat-header p {
                    opacity: 0.9;
                    font-size: 0.9em;
                }
                
                .header-buttons {
                    position: absolute;
                    right: 15px;
                    top: 50%;
                    transform: translateY(-50%);
                    display: flex;
                    gap: 10px;
                }
                
                .header-btn {
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 15px;
                    cursor: pointer;
                    font-size: 0.8em;
                    text-decoration: none;
                    transition: background 0.3s;
                }
                
                .header-btn:hover {
                    background: rgba(255,255,255,0.3);
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
                    padding: 15px 20px;
                    background: white;
                    border-top: 1px solid #e9ecef;
                    display: flex;
                    gap: 10px;
                    align-items: flex-end;
                }
                
                .input-wrapper {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    gap: 8px;
                }
                
                .chat-input {
                    width: 100%;
                    padding: 12px 16px;
                    border: 2px solid #e9ecef;
                    border-radius: 25px;
                    font-size: 14px;
                    outline: none;
                    transition: border-color 0.3s;
                    resize: none;
                    min-height: 44px;
                    max-height: 120px;
                    font-family: inherit;
                }
                
                .chat-input:focus {
                    border-color: #3498db;
                }
                
                .attached-files {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    margin-top: 5px;
                }
                
                .file-tag {
                    background: #e3f2fd;
                    border: 1px solid #bbdefb;
                    border-radius: 15px;
                    padding: 4px 12px;
                    font-size: 0.8em;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .file-tag .remove-file {
                    background: none;
                    border: none;
                    color: #f44336;
                    cursor: pointer;
                    font-size: 1.1em;
                    padding: 0;
                    width: 16px;
                    height: 16px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .file-actions {
                    display: flex;
                    gap: 8px;
                    align-items: center;
                }
                
                .attach-button {
                    background: none;
                    border: none;
                    font-size: 1.5em;
                    cursor: pointer;
                    padding: 8px;
                    border-radius: 50%;
                    transition: background 0.3s;
                    color: #666;
                }
                
                .attach-button:hover {
                    background: #f5f5f5;
                    color: #333;
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
                    min-width: 80px;
                }
                
                .send-button:hover {
                    transform: translateY(-1px);
                }
                
                .send-button:active {
                    transform: translateY(0);
                }
                
                .send-button:disabled {
                    background: #bdc3c7;
                    cursor: not-allowed;
                    transform: none;
                }
                
                .file-input {
                    display: none;
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
                
                .file-message {
                    background: linear-gradient(135deg, #00b894, #00a085);
                    color: white;
                    padding: 15px;
                    border-radius: 18px;
                    margin: 10px 0;
                    max-width: 80%;
                    margin-left: auto;
                    border-bottom-right-radius: 5px;
                }
                
                .file-info {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .file-icon {
                    font-size: 1.5em;
                }
                
                .file-details {
                    flex: 1;
                }
                
                .file-name {
                    font-weight: bold;
                    margin-bottom: 4px;
                }
                
                .file-size {
                    font-size: 0.8em;
                    opacity: 0.9;
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
                
                .zip-analysis {
                    background: linear-gradient(135deg, #fd79a8, #e84393);
                    color: white;
                    padding: 15px;
                    border-radius: 18px;
                    margin: 10px 0;
                    max-width: 90%;
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
                    
                    .header-buttons {
                        position: static;
                        transform: none;
                        justify-content: center;
                        margin-top: 10px;
                    }
                    
                    .chat-input-container {
                        padding: 10px 15px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="chat-container">
                <div class="chat-header">
                    <h1>🧠 AI Assistant</h1>
                    <p>Задайте вопрос или загрузите файл для анализа</p>
                    <div class="header-buttons">
                        <a href="/stats" class="header-btn">📊 Статистика</a>
                    </div>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message ai-message">
                        <strong>Привет! Я ваш AI-помощник 🤖</strong><br><br>
                        Я могу:<br>
                        • 🔍 Искать информацию в интернете<br>
                        • 📦 Анализировать ZIP-архивы<br>
                        • 📄 Читать текстовые файлы<br>
                        • 💻 Анализировать код<br><br>
                        <strong>Просто напишите сообщение или прикрепите файл!</strong>
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
                    <div class="file-actions">
                        <input type="file" id="fileInput" class="file-input" multiple accept=".zip,.txt,.py,.js,.java,.html,.css,.json,.md">
                        <button class="attach-button" onclick="document.getElementById('fileInput').click()" title="Прикрепить файл">
                            📎
                        </button>
                    </div>
                    
                    <div class="input-wrapper">
                        <textarea class="chat-input" id="messageInput" placeholder="Введите ваш вопрос..." autocomplete="off" rows="1"></textarea>
                        <div class="attached-files" id="attachedFiles"></div>
                    </div>
                    
                    <button class="send-button" onclick="sendMessage()" id="sendButton">Отправить</button>
                </div>
            </div>

            <script>
                const chatMessages = document.getElementById('chatMessages');
                const messageInput = document.getElementById('messageInput');
                const fileInput = document.getElementById('fileInput');
                const attachedFiles = document.getElementById('attachedFiles');
                const sendButton = document.getElementById('sendButton');
                const typingIndicator = document.getElementById('typingIndicator');
                
                let attachedFilesList = [];
                let isWaitingForResponse = false;
                
                // Авто-высота textarea
                messageInput.addEventListener('input', function() {
                    this.style.height = 'auto';
                    this.style.height = (this.scrollHeight) + 'px';
                });
                
                // Обработка выбора файлов
                fileInput.addEventListener('change', function(e) {
                    const files = Array.from(e.target.files);
                    files.forEach(file => {
                        if (!attachedFilesList.some(f => f.name === file.name)) {
                            attachedFilesList.push(file);
                            updateAttachedFilesDisplay();
                        }
                    });
                    this.value = ''; // Сбрасываем input
                });
                
                function updateAttachedFilesDisplay() {
                    attachedFiles.innerHTML = '';
                    attachedFilesList.forEach((file, index) => {
                        const fileTag = document.createElement('div');
                        fileTag.className = 'file-tag';
                        fileTag.innerHTML = `
                            📄 ${file.name}
                            <button class="remove-file" onclick="removeFile(${index})">×</button>
                        `;
                        attachedFiles.appendChild(fileTag);
                    });
                    
                    // Обновляем состояние кнопки отправки
                    sendButton.disabled = attachedFilesList.length === 0 && !messageInput.value.trim();
                }
                
                function removeFile(index) {
                    attachedFilesList.splice(index, 1);
                    updateAttachedFilesDisplay();
                }
                
                function addMessage(text, isUser, messageType = 'final', files = []) {
                    const messageDiv = document.createElement('div');
                    
                    if (messageType === 'search') {
                        messageDiv.className = 'search-status';
                        messageDiv.innerHTML = `🔍 ${text}`;
                    } else if (messageType === 'typing') {
                        messageDiv.className = 'typing-message';
                        messageDiv.innerHTML = text;
                    } else if (messageType === 'file') {
                        messageDiv.className = 'file-message';
                        files.forEach(file => {
                            const fileInfo = document.createElement('div');
                            fileInfo.className = 'file-info';
                            fileInfo.innerHTML = `
                                <div class="file-icon">📎</div>
                                <div class="file-details">
                                    <div class="file-name">${file.name}</div>
                                    <div class="file-size">${formatFileSize(file.size)}</div>
                                </div>
                            `;
                            messageDiv.appendChild(fileInfo);
                        });
                        if (text) {
                            const textDiv = document.createElement('div');
                            textDiv.style.marginTop = '10px';
                            textDiv.textContent = text;
                            messageDiv.appendChild(textDiv);
                        }
                    } else if (messageType === 'zip-analysis') {
                        messageDiv.className = 'zip-analysis';
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
                            if (text[i] === '\\n') {
                                element.innerHTML += '<br>';
                            } else {
                                element.innerHTML += text[i];
                            }
                            i++;
                            
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                            
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
                    const files = attachedFilesList;
                    
                    if (!message && files.length === 0) return;
                    
                    // Clear input and files
                    messageInput.value = '';
                    attachedFilesList = [];
                    updateAttachedFilesDisplay();
                    messageInput.style.height = 'auto';
                    
                    isWaitingForResponse = true;
                    sendButton.disabled = true;
                    
                    // Add user message with files
                    if (files.length > 0) {
                        addMessage(message, true, 'file', files);
                    } else if (message) {
                        addMessage(message, true);
                    }
                    
                    // Show searching status
                    const searchMessage = addMessage('Обрабатываю запрос...', false, 'search');
                    
                    try {
                        let response;
                        
                        if (files.length > 0) {
                            // Отправка с файлами
                            const formData = new FormData();
                            formData.append('message', message);
                            files.forEach(file => {
                                formData.append('files', file);
                            });
                            
                            response = await fetch('/analyze-with-file', {
                                method: 'POST',
                                body: formData
                            });
                        } else {
                            // Обычный запрос
                            response = await fetch('/chat', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({ message: message })
                            });
                        }
                        
                        const data = await response.json();
                        
                        // Remove search message
                        searchMessage.remove();
                        
                        // Add AI response with typing effect
                        const aiMessage = addMessage('', false, 'typing');
                        showTyping();
                        
                        // Type out the response
                        typeText(aiMessage, data.response, 5, () => {
                            aiMessage.className = data.response.includes('📦') ? 'zip-analysis' : 'message ai-message';
                            const time = new Date().toLocaleTimeString('ru-RU', { 
                                hour: '2-digit', 
                                minute: '2-digit' 
                            });
                            aiMessage.innerHTML = aiMessage.innerHTML + `<div class="message-time">${time}</div>`;
                            hideTyping();
                            isWaitingForResponse = false;
                            sendButton.disabled = false;
                        });
                        
                    } catch (error) {
                        searchMessage.remove();
                        hideTyping();
                        addMessage('❌ Ошибка соединения с сервером. Попробуйте еще раз.', false);
                        console.error('Error:', error);
                        isWaitingForResponse = false;
                        sendButton.disabled = false;
                    }
                }
                
                // Send message on Enter key (Ctrl+Enter for new line)
                messageInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && !e.shiftKey && !isWaitingForResponse) {
                        e.preventDefault();
                        sendMessage();
                    }
                });
                
                // Enable/disable send button based on input
                messageInput.addEventListener('input', function() {
                    sendButton.disabled = attachedFilesList.length === 0 && !this.value.trim();
                });
                
                function formatFileSize(bytes) {
                    if (bytes === 0) return '0 Bytes';
                    const k = 1024;
                    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                }
                
                // Focus input on load
                messageInput.focus();
                
                // Auto-scroll to bottom on load
                chatMessages.scrollTop = chatMessages.scrollHeight;
            </script>
        </body>
        </html>
        '''
        self.wfile.write(html.encode('utf-8'))
    
    def _handle_file_upload(self):
        """Обрабатывает загрузку файлов"""
        try:
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            boundary_match = re.search(r'boundary=(.*)$', content_type)
            if not boundary_match:
                self.send_error(400, "No boundary found")
                return
            
            boundary = boundary_match.group(1).encode()
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            parts = post_data.split(b'--' + boundary)
            uploaded_files = []
            
            for part in parts:
                if b'name="files"' in part and b'filename="' in part:
                    filename_match = re.search(b'filename="([^"]+)"', part)
                    if filename_match:
                        filename = filename_match.group(1).decode('utf-8')
                        
                        # Извлекаем содержимое файла
                        file_content = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                        
                        # Сохраняем файл
                        temp_dir = "temp_uploads"
                        os.makedirs(temp_dir, exist_ok=True)
                        file_path = os.path.join(temp_dir, f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
                        
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        uploaded_files.append({
                            'filename': filename,
                            'path': file_path,
                            'size': len(file_content)
                        })
            
            if uploaded_files:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    "success": True,
                    "files": uploaded_files,
                    "message": f"Загружено {len(uploaded_files)} файл(ов)"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            else:
                self.send_error(400, "No files uploaded")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки файлов: {e}")
            self.send_error(500, f"Upload error: {str(e)}")
    
    def _handle_analysis_with_file(self):
        """Обрабатывает запросы с прикрепленными файлами"""
        try:
            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            boundary_match = re.search(r'boundary=(.*)$', content_type)
            if not boundary_match:
                self.send_error(400, "No boundary found")
                return
            
            boundary = boundary_match.group(1).encode()
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            parts = post_data.split(b'--' + boundary)
            message = ""
            uploaded_files = []
            
            for part in parts:
                if b'name="message"' in part:
                    # Извлекаем текстовое сообщение
                    message_content = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                    message = message_content.decode('utf-8')
                
                elif b'name="files"' in part and b'filename="' in part:
                    filename_match = re.search(b'filename="([^"]+)"', part)
                    if filename_match:
                        filename = filename_match.group(1).decode('utf-8')
                        
                        # Извлекаем содержимое файла
                        file_content = part.split(b'\r\n\r\n')[1].rsplit(b'\r\n', 1)[0]
                        
                        # Сохраняем файл
                        temp_dir = "temp_uploads"
                        os.makedirs(temp_dir, exist_ok=True)
                        file_path = os.path.join(temp_dir, f"chat_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}")
                        
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        uploaded_files.append({
                            'filename': filename,
                            'path': file_path,
                            'size': len(file_content)
                        })
            
            # Обрабатываем файлы
            response_text = ""
            if uploaded_files:
                for file_info in uploaded_files:
                    if file_info['filename'].lower().endswith('.zip'):
                        # Анализ ZIP-архива
                        analysis_result = self.ai.analyze_uploaded_zip(file_info['path'])
                        response_text += f"\n\n📦 **Анализ архива {file_info['filename']}:**\n{analysis_result}"
                    else:
                        # Анализ текстового файла
                        try:
                            with open(file_info['path'], 'r', encoding='utf-8') as f:
                                content = f.read(5000)  # Читаем первые 5000 символов
                                response_text += f"\n\n📄 **Содержимое {file_info['filename']}:**\n```\n{content}\n```"
                        except:
                            response_text += f"\n\n📄 **Файл {file_info['filename']}:**\nНе удалось прочитать файл (возможно, бинарный файл)"
                    
                    # Удаляем временный файл
                    try:
                        os.remove(file_info['path'])
                    except:
                        pass
            
            # Добавляем ответ на текстовый запрос если есть
            if message:
                if response_text:
                    response_text = f"**Ваш запрос:** {message}" + response_text
                else:
                    # Если нет файлов, используем обычный поиск
                    chat_response = self.ai.generate_smart_response(message)
                    response_text = chat_response
            
            if not response_text:
                response_text = "Пожалуйста, введите запрос или загрузите файл для анализа."
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                "success": True,
                "response": response_text
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            print(f"❌ Ошибка анализа с файлом: {e}")
            self.send_error(500, f"Analysis error: {str(e)}")
    
    # Остальные методы остаются без изменений
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
        """Обрабатывает чат-запросы"""
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
            print(f"❌ Ошибка обработки чата: {e}")
            self.send_error(500, f"Error: {str(e)}")
    
    def log_message(self, format, *args):
        """Кастомное логирование"""
        print(f"🌐 AI Assistant: {format % args}")

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
