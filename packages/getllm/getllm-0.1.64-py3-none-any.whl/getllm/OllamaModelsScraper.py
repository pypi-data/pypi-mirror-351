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
                # Get the card's HTML for debugging
                try:
                    card_html = card_element.get_attribute('outerHTML')
                    if card_html and len(card_html) > 500:  # Only log if we have a reasonable amount of HTML
                        with open('debug_card.html', 'w', encoding='utf-8') as f:
                            f.write(card_html)
                        print("📝 Saved card HTML to debug_card.html")
                except Exception as e:
                    print(f"⚠️ Could not get card HTML: {str(e)}")
                
                # Get model name - try multiple possible selectors and strategies
                name = None
                
                # Strategy 1: Try to find name in common elements
                name_selectors = [
                    'h3', 'h2', 'h4',  # Common heading elements
                    'a[href^="/library/"]',  # Links to model pages
                    'div[class*="name"], span[class*="name"]',  # Elements with 'name' in class
                    'div:first-child',  # First child element
                    'a:first-child'  # First link
                ]
                
                for selector in name_selectors:
                    try:
                        elements = card_element.find_elements(By.CSS_SELECTOR, selector)
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 2 and len(text) < 100:  # Reasonable length for a name
                                name = text
                                break
                        if name:
                            break
                    except:
                        continue
                
                # Strategy 2: If no name found, try to extract from URL
                if not name or name == "Unknown":
                    try:
                        link = card_element.find_element(By.CSS_SELECTOR, 'a[href^="/library/"]')
                        if link:
                            href = link.get_attribute('href')
                            if href and '/library/' in href:
                                name = href.split('/library/')[-1].split('/')[0].split('?')[0]
                                if name:
                                    name = name.replace('-', ' ').title()
                    except:
                        pass
                
                # Strategy 3: Try to find the largest text element
                if not name or name == "Unknown":
                    try:
                        all_texts = [e.text.strip() for e in card_element.find_elements(By.XPATH, './/*') if e.text.strip()]
                        if all_texts:
                            # Sort by length and get the longest reasonable text
                            all_texts.sort(key=len, reverse=True)
                            for text in all_texts:
                                if 3 < len(text) < 100 and ' ' not in text:  # Likely a model name
                                    name = text
                                    break
                    except:
                        pass
                
                if name:
                    model_info["name"] = name
                
                # Get model URL
                try:
                    link = card_element.find_element(By.CSS_SELECTOR, 'a[href^="/library/"]')
                    if link:
                        href = link.get_attribute('href')
                        if href:
                            model_info["url"] = href
                            # If we still don't have a name, try to get it from the URL
                            if model_info["name"] == "Unknown" and '/library/' in href:
                                model_name = href.split('/library/')[-1].split('/')[0].split('?')[0]
                                if model_name:
                                    model_info["name"] = model_name.replace('-', ' ').title()
                except:
                    pass
                
                # Get description - look for a medium-length text block
                try:
                    # Try to find a paragraph or div with reasonable length text
                    all_texts = []
                    for elem in card_element.find_elements(By.XPATH, './/p | .//div'):
                        text = elem.text.strip()
                        if 20 < len(text) < 500:  # Reasonable length for a description
                            all_texts.append(text)
                    
                    if all_texts:
                        # Prefer longer descriptions, but not too long
                        all_texts.sort(key=len)
                        model_info["description"] = all_texts[-1]
                except:
                    pass
                
                # Get metadata (pulls, size, updated) - look for common patterns
                try:
                    # Get all text content and look for patterns
                    full_text = card_element.text.lower()
                    
                    # Look for pull/download count
                    import re
                    pull_match = re.search(r'(\d+[\d,]*)\s*(pulls?|downloads?)', full_text)
                    if pull_match:
                        model_info["pulls"] = pull_match.group(1).replace(',', '')
                    
                    # Look for size
                    size_match = re.search(r'(\d+\.?\d*)\s*(GB|MB|KB)', full_text)
                    if size_match:
                        model_info["size"] = f"{size_match.group(1)} {size_match.group(2)}"
                    
                    # Look for update/date information
                    date_match = re.search(r'(updated|last)\s*(?:on|:)?\s*([a-z0-9,\s]+(?:ago|today|yesterday|\d{4}))', full_text)
                    if date_match:
                        model_info["updated"] = date_match.group(2).strip()
                except:
                    pass
                
                # Get tags - look for small clickable elements or badges
                try:
                    tag_candidates = card_element.find_elements(By.CSS_SELECTOR, 
                        'span, div, a, button, .tag, .badge, .chip, [class*="tag"], [class*="badge"]')
                    
                    for tag in tag_candidates:
                        try:
                            tag_text = tag.text.strip()
                            if (tag_text and 
                                len(tag_text) < 30 and 
                                tag_text.lower() not in ['ollama', 'model', 'library', ''] and
                                tag_text != model_info["name"] and
                                not tag_text.isdigit() and
                                not any(x in tag_text.lower() for x in ['pull', 'download', 'updated', 'last', 'gb', 'mb', 'kb'])):
                                model_info["tags"].append(tag_text)
                        except:
                            continue
                    
                    # Remove duplicates while preserving order
                    seen = set()
                    model_info["tags"] = [x for x in model_info["tags"] if not (x in seen or seen.add(x))]
                    
                except Exception as e:
                    print(f"⚠️ Error extracting tags: {str(e)}")
                
                # Generate ollama pull command if we have a valid name
                if model_info["name"] != "Unknown":
                    model_name = model_info["name"].lower().replace(' ', ':')
                    model_info["ollama_command"] = f"ollama pull {model_name}"
                
            except Exception as e:
                print(f"⚠️ Warning in model info extraction: {str(e)}")
                import traceback
                traceback.print_exc()
                
            return model_info
            
        except Exception as e:
            print(f"⚠️ Error extracting model info: {str(e)}")
            import traceback
            traceback.print_exc()
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
    parser.add_argument('--limit', '-l', type=int, default=None,
                        help='Limit the number of models to process (for testing)')

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
        # Full scrape mode with optional limit
        models = scraper.scrape_all_models(detailed=args.detailed)
        
        # Apply limit if specified
        if args.limit and args.limit > 0 and len(models) > args.limit:
            print(f"\nℹ️ Limiting to {args.limit} models as requested")
            models = models[:args.limit]
            
        # Save the results
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