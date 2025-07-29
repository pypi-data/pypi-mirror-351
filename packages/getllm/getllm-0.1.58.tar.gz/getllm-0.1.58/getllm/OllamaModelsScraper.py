#!/usr/bin/env python3
"""
Ollama Models Scraper
Pobiera i zapisuje wszystkie dostępne modele z Ollama Library do JSON
"""

import json
import time
from typing import List, Dict, Any
from urllib.parse import urljoin
import argparse
import sys
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

class OllamaModelsScraper:
    def __init__(self, headless: bool = True):
        self.base_url = "https://ollama.com"
        self.library_url = f"{self.base_url}/library"
        self.search_url = f"{self.base_url}/search"
        self.models = []
        self.headless = headless
        self.driver = self._init_driver()
    
    def _init_driver(self):
        """Initialize and return a Selenium WebDriver"""
        # Install/update ChromeDriver
        chromedriver_autoinstaller.install()
        
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        
        # Initialize Chrome WebDriver
        driver = webdriver.Chrome(options=options)
        return driver
    
    def get_page(self, url: str, wait_for: str = None, timeout: int = 20) -> BeautifulSoup:
        """Load a page with Selenium and return parsed HTML"""
        print(f"🌐 Loading URL: {url}")
        try:
            self.driver.get(url)
            
            # Wait for the page to load completely
            if wait_for:
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Save page source for debugging
            page_source = self.driver.page_source
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            print("💾 Saved page source to debug_page.html")
            
            return BeautifulSoup(page_source, 'html.parser')
            
        except Exception as e:
            print(f"❌ Error loading {url}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            print("✅ WebDriver closed")

    def extract_model_info(self, card_element) -> Dict[str, Any]:
        """Extract model information from a model card element"""
        try:
            # Initialize default values
            model_info = {
                "name": "Unknown",
                "url": "",
                "pulls": "0",
                "size": "Unknown",
                "updated": "Unknown",
                "description": "",
                "tags": [],
                "source": "ollama",
                "ollama_command": "",
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            try:
                # Get model name - try multiple possible selectors
                name_selectors = ['h3', '.model-name', '.name', 'a[href^="/library/"] h3']
                for selector in name_selectors:
                    try:
                        name_elem = card_element.find_element(By.CSS_SELECTOR, selector)
                        if name_elem:
                            model_info["name"] = name_elem.text.strip()
                            break
                    except:
                        continue
                
                # Get model URL
                try:
                    link_selector = 'a[href^="/library/"]'
                    link_elem = card_element.find_element(By.CSS_SELECTOR, link_selector)
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        if href:
                            model_info["url"] = href
                            # Extract model name from URL if name not found
                            if model_info["name"] == "Unknown" and '/library/' in href:
                                model_info["name"] = href.split('/library/')[-1].split('/')[0]
                except:
                    pass
                
                # Get description
                try:
                    desc_elems = card_element.find_elements(By.CSS_SELECTOR, 'p, .description, .model-description')
                    if desc_elems:
                        model_info["description"] = desc_elems[0].text.strip()
                except:
                    pass
                
                # Get metadata (pulls, size, updated)
                try:
                    meta_selectors = [
                        'div.text-sm.text-gray-500',
                        '.metadata',
                        '.model-meta',
                        'div:has(> svg) + span',
                        'div.flex.items-center.text-sm.text-gray-500'
                    ]
                    
                    for selector in meta_selectors:
                        try:
                            meta_elems = card_element.find_elements(By.CSS_SELECTOR, selector)
                            if meta_elems:
                                metadata = [elem.text.strip().lower() for elem in meta_elems if elem.text.strip()]
                                
                                # Extract pulls/downloads
                                pulls = next((m for m in metadata if any(x in m for x in ['pull', 'download'])), None)
                                if pulls:
                                    model_info["pulls"] = pulls
                                
                                # Extract size
                                size = next((m for m in metadata if any(x in m for x in ['gb', 'mb', 'kb'])), None)
                                if size:
                                    model_info["size"] = size
                                
                                # Extract last updated
                                updated = next((m for m in metadata if any(x in m for x in ['ago', 'updated', 'last'])), None)
                                if updated:
                                    model_info["updated"] = updated
                                
                                if any([pulls, size, updated]):
                                    break
                        except:
                            continue
                except:
                    pass
                
                # Get tags
                try:
                    tag_selectors = [
                        'span.bg-gray-100, span.inline-flex',
                        '.tag, .model-tag',
                        'span:not([class]):not([id])',
                        'div:has(> svg) + span'
                    ]
                    
                    for selector in tag_selectors:
                        try:
                            tag_elems = card_element.find_elements(By.CSS_SELECTOR, selector)
                            if tag_elems:
                                for tag in tag_elems:
                                    try:
                                        tag_text = tag.text.strip()
                                        if tag_text and tag_text.lower() not in ['ollama', 'model', 'library', '']:
                                            model_info["tags"].append(tag_text)
                                    except:
                                        continue
                                if model_info["tags"]:  # If we found some tags, no need to try other selectors
                                    break
                        except:
                            continue
                except:
                    pass
                
                # Generate ollama pull command if we have a valid name
                if model_info["name"] != "Unknown":
                    model_info["ollama_command"] = f"ollama pull {model_info['name']}"
                
            except Exception as e:
                print(f"⚠️ Warning in model info extraction: {str(e)[:100]}...")
                
            return model_info
            
        except Exception as e:
            print(f"⚠️ Error extracting model info: {str(e)[:100]}...")
            return None
            
        except Exception as e:
            print(f"⚠️ Error extracting model info: {e}")
            import traceback
            traceback.print_exc()
            return None

    def scrape_library_page(self, page: int = 1, limit: int = None) -> List[Dict[str, Any]]:
        """Scrape one page of the Ollama library
        
        Args:
            page: Page number to scrape (1-based)
            limit: Maximum number of models to scrape (None for no limit)
            
        Returns:
            List of model dictionaries
        """
        print(f"📄 Scraping library page {page}...")
        
        url = f"{self.library_url}?page={page}" if page > 1 else self.library_url
        
        try:
            # Load the page
            print(f"🌐 Loading URL: {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            # Wait for dynamic content to load
            time.sleep(3)
            
            # Take a screenshot for debugging
            try:
                screenshot_path = f"page_{page}_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"📸 Saved screenshot to {screenshot_path}")
            except Exception as e:
                print(f"⚠️ Could not take screenshot: {str(e)}")
            
            # Get the page source for debugging
            try:
                page_source = self.driver.page_source
                with open(f"page_{page}_source.html", 'w', encoding='utf-8') as f:
                    f.write(page_source)
                print(f"📝 Saved page source to page_{page}_source.html")
            except Exception as e:
                print(f"⚠️ Could not save page source: {str(e)}")
            
            # Try to find model cards using multiple strategies
            model_cards = []
            
            # Strategy 1: Look for model cards with specific class names
            selectors = [
                'div[class*="model"][class*="card"]',  # Matches class containing both 'model' and 'card'
                'a[href^="/library/"]',
                'div[class*="grid"][class*="gap"] > div',  # Grid layout items
                'div[class*="space-y"] > div',  # Items with vertical spacing
                'div[class*="p-"][class*="border"]',  # Items with padding and border
                'div[class*="rounded"]'  # Items with rounded corners
            ]
            
            for selector in selectors:
                try:
                    cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if len(cards) > len(model_cards):
                        model_cards = cards
                        print(f"🔍 Found {len(cards)} potential model cards with selector: {selector}")
                        if len(cards) >= 10:  # If we found a reasonable number of cards, use this selector
                            break
                except Exception as e:
                    continue
            
            # If we didn't find any cards, try a more generic approach
            if not model_cards:
                print("⚠️ No model cards found with specific selectors, trying generic approach...")
                all_elements = self.driver.find_elements(By.XPATH, '//*')
                model_cards = [el for el in all_elements 
                             if el.tag_name in ['div', 'a'] 
                             and len(el.text) > 50  # Reasonable minimum text length for a model card
                             and len(el.find_elements(By.XPATH, './/*')) > 3]  # Has several child elements
                print(f"🔍 Found {len(model_cards)} potential model cards with generic selector")
            
            # Apply limit if specified
            if limit and len(model_cards) > limit:
                print(f"ℹ️ Limiting to first {limit} model cards")
                model_cards = model_cards[:limit]
            
            print(f"🔍 Found {len(model_cards)} model cards on page {page}")
            
            models = []
            for i, card in enumerate(model_cards, 1):
                try:
                    print(f"\n🔄 Processing card {i}/{len(model_cards)}")
                    print(f"Card text preview: {card.text[:100]}..." if card.text else "No text content")
                    
                    # Scroll the card into view to ensure it's clickable
                    try:
                        self.driver.execute_script(
                            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", 
                            card
                        )
                        time.sleep(0.5)  # Small delay for any animations
                    except Exception as e:
                        print(f"  ⚠️ Could not scroll to card: {str(e)}")
                    
                    # Extract model info
                    model_info = self.extract_model_info(card)
                    
                    if model_info and model_info.get('name') != 'Unknown':
                        models.append(model_info)
                        print(f"✅ Added model: {model_info['name']}")
                    else:
                        print(f"⚠️ Skipped card {i} - no valid model info extracted")
                        # Print card HTML for debugging
                        try:
                            print(f"Card HTML: {card.get_attribute('outerHTML')[:200]}...")
                        except:
                            print("Could not get card HTML")
                        
                except Exception as e:
                    print(f"⚠️ Error processing model card {i}: {str(e)[:200]}...")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\n✅ Successfully processed {len(models)} models from page {page}")
            return models
            
        except Exception as e:
            print(f"❌ Error scraping library page {page}: {str(e)[:200]}...")
            import traceback
            traceback.print_exc()
            return []

    def search_models(self, query: str = "", category: str = "") -> List[Dict[str, Any]]:
        """Search for models by query and category"""
        print(f"🔍 Searching for: query='{query}', category='{category}'")
        
        # For now, we'll just use the library page
        # The search functionality on Ollama's site is client-side rendered
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