#!/usr/bin/env python3
"""
HuggingFace Models Scraper
Pobiera wszystkie dostępne modele z HuggingFace Hub przez API do JSON
"""

import json
import time
import requests
from typing import List, Dict, Any, Optional
import argparse
import sys
from datetime import datetime


class HuggingFaceModelsScraper:
    def __init__(self, use_token: bool = False):
        self.base_url = "https://huggingface.co"
        self.api_url = "https://huggingface.co/api"
        self.session = requests.Session()

        # Optional HF token for rate limiting
        if use_token:
            token = input("Enter your HuggingFace token (optional, press Enter to skip): ").strip()
            if token:
                self.session.headers.update({"Authorization": f"Bearer {token}"})

        self.session.headers.update({
            'User-Agent': 'HF-Models-Scraper/1.0',
            'Accept': 'application/json'
        })

    def get_models_page(self, params: dict) -> Dict[str, Any]:
        """Pobiera stronę modeli przez API"""
        try:
            response = self.session.get(f"{self.api_url}/models", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error fetching models: {e}")
            return []

    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """Pobiera szczegółowe informacje o modelu"""
        try:
            response = self.session.get(f"{self.api_url}/models/{model_id}", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Error getting details for {model_id}: {e}")
            return {}

    def get_model_files(self, model_id: str) -> List[Dict[str, Any]]:
        """Pobiera listę plików modelu"""
        try:
            response = self.session.get(f"{self.api_url}/models/{model_id}/tree/main", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"⚠️ Error getting files for {model_id}: {e}")
            return []

    def check_ollama_compatibility(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sprawdza kompatybilność z Ollama"""
        compatibility = {
            "ollama_compatible": False,
            "gguf_available": False,
            "gguf_files": [],
            "supported_formats": [],
            "recommended_for_ollama": False
        }

        # Sprawdź tagi
        tags = model_data.get('tags', [])
        pipeline_tag = model_data.get('pipeline_tag', '')

        # Formaty kompatybilne z Ollama
        ollama_formats = ['gguf', 'ggml']
        supported_pipelines = [
            'text-generation', 'conversational', 'text2text-generation',
            'feature-extraction', 'sentence-similarity', 'fill-mask'
        ]

        # Sprawdź pipeline
        if pipeline_tag in supported_pipelines:
            compatibility["ollama_compatible"] = True
            compatibility["supported_formats"].append(pipeline_tag)

        # Sprawdź tagi dla formatów
        for tag in tags:
            if any(fmt in tag.lower() for fmt in ollama_formats):
                compatibility["gguf_available"] = True
                compatibility["ollama_compatible"] = True

        # Sprawdź pliki modelu
        try:
            files = self.get_model_files(model_data.get('modelId', ''))
            for file_info in files:
                filename = file_info.get('path', '').lower()
                if filename.endswith('.gguf'):
                    compatibility["gguf_available"] = True
                    compatibility["gguf_files"].append(file_info)
                    compatibility["ollama_compatible"] = True
        except:
            pass

        # Rekomendacja
        if (compatibility["gguf_available"] and
                pipeline_tag == 'text-generation' and
                model_data.get('downloads', 0) > 100):
            compatibility["recommended_for_ollama"] = True

        return compatibility

    def process_model(self, model: Dict[str, Any], detailed: bool = False) -> Dict[str, Any]:
        """Przetwarza dane modelu"""
        model_id = model.get('modelId', model.get('id', ''))

        processed = {
            "id": model_id,
            "name": model.get('modelId', model_id),
            "author": model_id.split('/')[0] if '/' in model_id else "unknown",
            "model_name": model_id.split('/')[-1] if '/' in model_id else model_id,
            "url": f"{self.base_url}/{model_id}",
            "downloads": model.get('downloads', 0),
            "likes": model.get('likes', 0),
            "pipeline_tag": model.get('pipeline_tag', ''),
            "tags": model.get('tags', []),
            "created_at": model.get('createdAt', ''),
            "updated_at": model.get('lastModified', ''),
            "private": model.get('private', False),
            "gated": model.get('gated', False),
            "library_name": model.get('library_name', ''),
            "source": "huggingface",
            "scraped_at": datetime.now().isoformat()
        }

        # Sprawdź kompatybilność z Ollama
        compatibility = self.check_ollama_compatibility(model)
        processed.update(compatibility)

        # Dodatkowe szczegóły jeśli requested
        if detailed and processed["ollama_compatible"]:
            print(f"🔍 Getting details for {model_id}...")
            details = self.get_model_details(model_id)

            if details:
                processed.update({
                    "description": details.get('description', ''),
                    "model_size": details.get('safetensors', {}).get('total', 0),
                    "config": details.get('config', {}),
                    "model_card": details.get('cardData', {}),
                    "siblings": len(details.get('siblings', [])),
                    "widget_data": details.get('widgetData', [])
                })

        # Generuj komendę Ollama jeśli kompatybilny
        if processed["gguf_available"]:
            processed[
                "ollama_import_command"] = f"# Download GGUF file manually from {processed['url']}/tree/main and use: ollama create {model_id.replace('/', '-')} -f Modelfile"
        elif processed["ollama_compatible"]:
            processed["ollama_import_command"] = f"# May require conversion to GGUF format first"

        return processed

    def search_models(self,
                      query: str = "",
                      task: str = "",
                      language: str = "",
                      library: str = "",
                      tags: List[str] = None,
                      sort: str = "downloads",
                      limit: int = 1000) -> List[Dict[str, Any]]:
        """Przeszukuje modele według kryteriów"""

        params = {
            "limit": min(limit, 1000),  # API limit
            "sort": sort,
            "direction": -1
        }

        if query:
            params["search"] = query
        if task:
            params["pipeline_tag"] = task
        if language:
            params["language"] = language
        if library:
            params["library"] = library
        if tags:
            params["tags"] = ",".join(tags)

        print(f"🔍 Searching with params: {params}")

        all_models = []
        offset = 0

        while len(all_models) < limit:
            params["offset"] = offset

            models_data = self.get_models_page(params)
            if not models_data:
                break

            batch_models = models_data if isinstance(models_data, list) else []
            if not batch_models:
                break

            all_models.extend(batch_models)
            print(f"📄 Fetched {len(batch_models)} models (total: {len(all_models)})")

            if len(batch_models) < params["limit"]:
                break  # Last page

            offset += params["limit"]
            time.sleep(0.1)  # Rate limiting

        return all_models[:limit]

    def scrape_ollama_compatible_models(self, limit: int = 5000, detailed: bool = False) -> List[Dict[str, Any]]:
        """Scrape'uje modele kompatybilne z Ollama"""
        print("🚀 Searching for Ollama-compatible models...")

        # Najpierw szukaj modeli z tagiem GGUF
        gguf_models = self.search_models(
            tags=["gguf"],
            sort="downloads",
            limit=limit // 4
        )

        # Potem modele text-generation
        text_gen_models = self.search_models(
            task="text-generation",
            sort="downloads",
            limit=limit // 2
        )

        # Modele embedding
        embedding_models = self.search_models(
            task="feature-extraction",
            sort="downloads",
            limit=limit // 8
        )

        # Modele conversational
        conv_models = self.search_models(
            task="conversational",
            sort="downloads",
            limit=limit // 8
        )

        # Połącz i usuń duplikaty
        all_models = []
        seen_ids = set()

        for models_batch in [gguf_models, text_gen_models, embedding_models, conv_models]:
            for model in models_batch:
                model_id = model.get('modelId', model.get('id', ''))
                if model_id and model_id not in seen_ids:
                    seen_ids.add(model_id)
                    processed = self.process_model(model, detailed=detailed)
                    all_models.append(processed)

                    if len(all_models) % 100 == 0:
                        print(f"✅ Processed {len(all_models)} models...")

                    time.sleep(0.05)  # Rate limiting

        # Filtruj tylko kompatybilne z Ollama
        compatible_models = [m for m in all_models if m.get('ollama_compatible', False)]

        print(f"✅ Found {len(compatible_models)} Ollama-compatible models out of {len(all_models)} total")
        return compatible_models

    def scrape_all_models(self, limit: int = 10000, detailed: bool = False) -> List[Dict[str, Any]]:
        """Scrape'uje wszystkie modele"""
        print(f"🚀 Starting HuggingFace models scraping (limit: {limit})...")

        all_models = self.search_models(
            sort="downloads",
            limit=limit
        )

        processed_models = []

        for i, model in enumerate(all_models):
            processed = self.process_model(model, detailed=detailed)
            processed_models.append(processed)

            if (i + 1) % 100 == 0:
                print(f"✅ Processed {i + 1}/{len(all_models)} models...")

            time.sleep(0.05)  # Rate limiting

        return processed_models

    def save_to_json(self, models: List[Dict[str, Any]], filename: str):
        """Zapisuje modele do pliku JSON"""
        try:
            # Statystyki
            stats = {
                "total_models": len(models),
                "ollama_compatible": len([m for m in models if m.get('ollama_compatible', False)]),
                "gguf_available": len([m for m in models if m.get('gguf_available', False)]),
                "recommended_for_ollama": len([m for m in models if m.get('recommended_for_ollama', False)])
            }

            # Zbierz pipeline tags
            pipeline_counts = {}
            for model in models:
                tag = model.get('pipeline_tag', 'unknown')
                pipeline_counts[tag] = pipeline_counts.get(tag, 0) + 1

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "source": "huggingface.co",
                    "scraped_at": datetime.now().isoformat(),
                    "statistics": stats,
                    "pipeline_tags": pipeline_counts,
                    "models": models
                }, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved {len(models)} models to {filename}")
            print(f"📊 Stats: {stats}")

        except Exception as e:
            print(f"❌ Error saving to JSON: {e}")

    def search_local_models(self, models: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Przeszukuje pobrane modele lokalnie"""
        query_lower = query.lower()
        results = []

        for model in models:
            if (query_lower in model['name'].lower() or
                    query_lower in model.get('description', '').lower() or
                    any(query_lower in tag.lower() for tag in model.get('tags', [])) or
                    query_lower in model.get('pipeline_tag', '').lower()):
                results.append(model)

        return results


def main():
    parser = argparse.ArgumentParser(description='Scrape HuggingFace models')
    parser.add_argument('--output', '-o', default='huggingface_models.json',
                        help='Output JSON file')
    parser.add_argument('--limit', '-l', type=int, default=5000,
                        help='Maximum number of models to fetch')
    parser.add_argument('--detailed', '-d', action='store_true',
                        help='Fetch detailed model information (much slower)')
    parser.add_argument('--ollama-only', action='store_true',
                        help='Only fetch Ollama-compatible models')
    parser.add_argument('--search', '-s', type=str,
                        help='Search for specific models')
    parser.add_argument('--task', '-t', type=str,
                        help='Filter by task/pipeline tag')
    parser.add_argument('--language', type=str,
                        help='Filter by language')
    parser.add_argument('--use-token', action='store_true',
                        help='Use HuggingFace token for higher rate limits')

    args = parser.parse_args()

    scraper = HuggingFaceModelsScraper(use_token=args.use_token)

    if args.search:
        # Search mode
        models = scraper.search_models(
            query=args.search,
            task=args.task or "",
            language=args.language or "",
            limit=args.limit
        )

        processed_models = []
        for model in models[:20]:  # Process first 20 for display
            processed = scraper.process_model(model)
            processed_models.append(processed)

        print(f"\n🔍 Search results for '{args.search}':")
        for i, model in enumerate(processed_models, 1):
            compat = "✅" if model.get('ollama_compatible') else "❌"
            gguf = "🟢" if model.get('gguf_available') else "🔴"
            print(f"{i}. {model['name']} {compat} {gguf}")
            print(f"   Downloads: {model['downloads']}, Task: {model['pipeline_tag']}")
            print(f"   URL: {model['url']}")

    else:
        # Full scrape mode
        if args.ollama_only:
            models = scraper.scrape_ollama_compatible_models(
                limit=args.limit,
                detailed=args.detailed
            )
        else:
            models = scraper.scrape_all_models(
                limit=args.limit,
                detailed=args.detailed
            )

        scraper.save_to_json(models, args.output)

        # Show Ollama-compatible summary
        ollama_models = [m for m in models if m.get('ollama_compatible', False)]
        gguf_models = [m for m in models if m.get('gguf_available', False)]

        print(f"\n📊 OLLAMA COMPATIBILITY SUMMARY:")
        print(f"Total models: {len(models)}")
        print(f"Ollama compatible: {len(ollama_models)}")
        print(f"GGUF available: {len(gguf_models)}")
        print(f"Recommended for Ollama: {len([m for m in models if m.get('recommended_for_ollama')])}")

        if gguf_models:
            print(f"\n🟢 Top GGUF models for Ollama:")
            sorted_gguf = sorted(gguf_models, key=lambda x: x['downloads'], reverse=True)
            for i, model in enumerate(sorted_gguf[:10], 1):
                print(f"{i}. {model['name']} ({model['downloads']} downloads)")


if __name__ == "__main__":
    main()