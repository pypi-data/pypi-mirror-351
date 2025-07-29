#!/usr/bin/env python3
"""
Ollama Models Scraper
Pobiera i zapisuje wszystkie dostępne modele z Ollama Library do JSON
"""

import json
import time
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, parse_qs, urlparse
import argparse
import sys


class OllamaModelsScraper:
    def __init__(self):
        self.base_url = "https://ollama.com"
        self.library_url = f"{self.base_url}/library"
        self.search_url = f"{self.base_url}/search"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.models = []

    def get_page(self, url: str, params: dict = None) -> BeautifulSoup:
        """Pobiera stronę i zwraca parsed HTML"""
        try:
            print(f"🌐 Fetching URL: {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # Save raw HTML for debugging
            debug_filename = f"debug_{url.replace('https://', '').replace('/', '_')}.html"
            with open(debug_filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Saved response to {debug_filename}")
            
            # Print first 500 chars of response for quick inspection
            print("📄 Response preview:")
            print(response.text[:500] + "...")
            
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def extract_model_info(self, model_element) -> Dict[str, Any]:
        """Wyciąga informacje o modelu z elementu HTML"""
        try:
            # Nazwa modelu
            name_element = model_element.find('h2') or model_element.find('h3') or model_element.find('.font-medium')
            name = name_element.get_text(strip=True) if name_element else "Unknown"

            # Link do modelu
            link_element = model_element.find('a')
            relative_url = link_element.get('href') if link_element else ""
            full_url = urljoin(self.base_url, relative_url)

            # Pulls/Downloads
            pulls_element = model_element.find(text=lambda x: x and ('pull' in x.lower() or 'download' in x.lower()))
            pulls = pulls_element.strip() if pulls_element else "0"

            # Rozmiar
            size_element = model_element.find(text=lambda x: x and ('gb' in x.lower() or 'mb' in x.lower()))
            size = size_element.strip() if size_element else "Unknown"

            # Ostatnia aktualizacja
            updated_element = model_element.find(text=lambda x: x and ('ago' in x.lower() or 'updated' in x.lower()))
            updated = updated_element.strip() if updated_element else "Unknown"

            # Opis
            description_element = model_element.find('p') or model_element.find('.text-gray-600')
            description = description_element.get_text(strip=True) if description_element else ""

            # Tagi/kategorie
            tags = []
            tag_elements = model_element.find_all('span', class_='tag') or model_element.find_all('.badge')
            for tag in tag_elements:
                tags.append(tag.get_text(strip=True))

            return {
                "name": name,
                "url": full_url,
                "pulls": pulls,
                "size": size,
                "updated": updated,
                "description": description,
                "tags": tags,
                "source": "ollama",
                "ollama_command": f"ollama pull {name}",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print(f"⚠️ Error extracting model info: {e}")
            return None

    def get_model_details(self, model_url: str) -> Dict[str, Any]:
        """Pobiera szczegółowe informacje o modelu ze strony modelu"""
        soup = self.get_page(model_url)
        if not soup:
            return {}

        details = {}
        try:
            # Parametry modelu
            params_section = soup.find('section', text=lambda x: x and 'parameters' in x.lower())
            if params_section:
                details['parameters'] = params_section.get_text(strip=True)

            # Architektura
            arch_element = soup.find(text=lambda x: x and 'architecture' in x.lower())
            if arch_element:
                details['architecture'] = arch_element.parent.get_text(strip=True)

            # Dostępne tagi/wersje
            tags_section = soup.find_all('div', class_='tag')
            available_tags = []
            for tag in tags_section:
                available_tags.append(tag.get_text(strip=True))
            details['available_tags'] = available_tags

        except Exception as e:
            print(f"⚠️ Error getting model details: {e}")

        return details

    def scrape_library_page(self, page: int = 1) -> List[Dict[str, Any]]:
        """Scrape'uje jedną stronę library"""
        print(f"📄 Scraping library page {page}...")

        params = {'page': page} if page > 1 else {}
        soup = self.get_page(self.library_url, params)

        if not soup:
            return []


        models = []

        # Nowa struktura strony Ollama
        model_cards = soup.select('a[href^="/library/"]')
        
        for card in model_cards:
            try:
                # Pobieranie podstawowych informacji
                name_elem = card.select_one('h3')
                if not name_elem:
                    continue
                    
                name = name_elem.get_text(strip=True)
                url = urljoin(self.base_url, card['href'])
                
                # Pobieranie opisu
                description_elem = card.select_one('p')
                description = description_elem.get_text(strip=True) if description_elem else ""
                
                # Pobieranie liczby pobrań i innych metadanych
                meta_elements = card.select('div.text-sm.text-gray-500')
                pulls = "0"
                size = "Unknown"
                updated = "Unknown"
                
                for meta in meta_elements:
                    text = meta.get_text(strip=True).lower()
                    if 'pull' in text or 'download' in text:
                        pulls = text
                    elif 'gb' in text or 'mb' in text:
                        size = text
                    elif 'ago' in text or 'updated' in text:
                        updated = text
                
                # Pobieranie tagów
                tags = []
                tag_elements = card.select('span.bg-gray-100, span.inline-flex')
                for tag in tag_elements:
                    tag_text = tag.get_text(strip=True)
                    if tag_text and tag_text not in ['Ollama', 'Model', 'Library']:
                        tags.append(tag_text)
                
                models.append({
                    "name": name,
                    "url": url,
                    "pulls": pulls,
                    "size": size,
                    "updated": updated,
                    "description": description,
                    "tags": tags,
                    "source": "ollama",
                    "ollama_command": f"ollama pull {name}",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
                })
                
            except Exception as e:
                print(f"⚠️ Error processing model card: {e}")
                continue
                
        return models

    def search_models(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        """Przeszukuje modele według zapytania i kategorii"""
        print(f"🔍 Searching for: query='{query}', category='{category}'")

        # Używamy tej samej metody co do scrapowania biblioteki,
        # ponieważ strona wyszukiwania ma podobną strukturę
        return self.scrape_library_page()

    def scrape_all_categories(self) -> List[Dict[str, Any]]:
        """Scrape'uje wszystkie kategorie modeli"""
        categories = [
            "", "vision", "code", "embedding", "tools", "multimodal",
            "chat", "reasoning", "math", "roleplay"
        ]

        all_models = []
        seen_models = set()

        for category in categories:
            print(f"📂 Scraping category: {category or 'all'}")

            models = self.search_models(category=category)

            for model in models:
                model_key = f"{model['name']}_{model['url']}"
                if model_key not in seen_models:
                    seen_models.add(model_key)
                    all_models.append(model)

            time.sleep(1)  # Rate limiting

        return all_models

    def scrape_all_models(self, detailed: bool = False) -> List[Dict[str, Any]]:
        """Główna funkcja - scrape'uje wszystkie modele"""
        print("🚀 Starting Ollama models scraping...")

        # Scrape library pages
        all_models = []
        page = 1
        max_pages = 50  # Safety limit

        while page <= max_pages:
            models = self.scrape_library_page(page)
            if not models:  # No more models found
                break

            all_models.extend(models)
            print(f"✅ Found {len(models)} models on page {page}")

            page += 1
            time.sleep(1)  # Rate limiting

        # Scrape categories for additional models
        category_models = self.scrape_all_categories()

        # Merge and deduplicate
        seen_models = set()
        final_models = []

        for models_list in [all_models, category_models]:
            for model in models_list:
                model_key = f"{model['name']}_{model['url']}"
                if model_key not in seen_models:
                    seen_models.add(model_key)

                    # Get detailed info if requested
                    if detailed and model['url']:
                        print(f"🔍 Getting details for {model['name']}...")
                        details = self.get_model_details(model['url'])
                        model.update(details)
                        time.sleep(0.5)  # Rate limiting

                    final_models.append(model)

        print(f"✅ Total unique models found: {len(final_models)}")
        return final_models

    def save_to_json(self, models: List[Dict[str, Any]], filename: str):
        """Zapisuje modele do pliku JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "source": "ollama.com",
                    "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "total_models": len(models),
                    "models": models
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(models)} models to {filename}")
        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")

    def search_local_models(self, query: str) -> List[Dict[str, Any]]:
        """Przeszukuje pobrane modele lokalnie"""
        if not self.models:
            print("❌ No models loaded. Run scrape_all_models() first.")
            return []

        query_lower = query.lower()
        results = []

        for model in self.models:
            if (query_lower in model['name'].lower() or
                    query_lower in model['description'].lower() or
                    any(query_lower in tag.lower() for tag in model['tags'])):
                results.append(model)

        return results


def main():
    parser = argparse.ArgumentParser(description='Scrape Ollama models')
    parser.add_argument('--output', '-o', default='ollama_models.json',
                        help='Output JSON file')
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='Fetch detailed model information (slower)')
    parser.add_argument('--search', '-s', type=str,
                        help='Search for specific models')
    parser.add_argument('--category', '-c', type=str,
                        help='Filter by category')

    args = parser.parse_args()

    scraper = OllamaModelsScraper()

    if args.search:
        # Search mode
        models = scraper.search_models(query=args.search, category=args.category or "")
        print(f"\n🔍 Search results for '{args.search}':")
        for i, model in enumerate(models[:10], 1):  # Show first 10
            print(f"{i}. {model['name']} - {model['description'][:100]}...")
            print(f"   Command: {model['ollama_command']}")
    else:
        # Full scrape mode
        models = scraper.scrape_all_models(detailed=args.detailed)
        scraper.save_to_json(models, args.output)

        # Show summary
        print(f"\n📊 SUMMARY:")
        print(f"Total models: {len(models)}")

        # Count by categories/tags
        tag_counts = {}
        for model in models:
            for tag in model['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        print(f"Top categories:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {tag}: {count}")


if __name__ == "__main__":
    main()