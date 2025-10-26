#!/usr/bin/env python3
"""
Pulsai Translation Update Script
Update terminology: Functions → Outils, Pipeline → Tunnel
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List

class TranslationUpdater:
    """Update translations across all locale files"""
    
    LOCALES_DIR = "src/lib/i18n/locales"
    
    # Translation mappings (English → French for reference)
    # These will be applied to all locale files
    REPLACEMENTS = {
        # Functions → Outils
        "Functions": "Outils",
        "Function": "Outil",
        "functions": "outils",
        "function": "outil",
        
        # Pipeline → Tunnel  
        "Pipelines": "Tunnels",
        "Pipeline": "Tunnel",
        "pipelines": "tunnels",
        "pipeline": "tunnel",
    }
    
    # Specific translations per locale
    LOCALE_SPECIFIC = {
        "en-US": {
            "Functions": "Tools",
            "Function": "Tool", 
            "Pipelines": "Tunnels",
            "Pipeline": "Tunnel"
        },
        "en-GB": {
            "Functions": "Tools",
            "Function": "Tool",
            "Pipelines": "Tunnels", 
            "Pipeline": "Tunnel"
        },
        "fr-FR": {
            "Functions": "Outils",
            "Function": "Outil",
            "Pipelines": "Tunnels",
            "Pipeline": "Tunnel"
        },
        "fr-CA": {
            "Functions": "Outils",
            "Function": "Outil", 
            "Pipelines": "Tunnels",
            "Pipeline": "Tunnel"
        },
        "es-ES": {
            "Functions": "Herramientas",
            "Function": "Herramienta",
            "Pipelines": "Túneles",
            "Pipeline": "Túnel"
        },
        "de-DE": {
            "Functions": "Werkzeuge",
            "Function": "Werkzeug",
            "Pipelines": "Tunnel",
            "Pipeline": "Tunnel"
        },
        "it-IT": {
            "Functions": "Strumenti",
            "Function": "Strumento",
            "Pipelines": "Tunnel",
            "Pipeline": "Tunnel"
        },
        "pt-BR": {
            "Functions": "Ferramentas",
            "Function": "Ferramenta",
            "Pipelines": "Túneis",
            "Pipeline": "Túnel"
        },
        "pt-PT": {
            "Functions": "Ferramentas",
            "Function": "Ferramenta",
            "Pipelines": "Túneis",
            "Pipeline": "Túnel"
        },
        "nl-NL": {
            "Functions": "Hulpmiddelen",
            "Function": "Hulpmiddel",
            "Pipelines": "Tunnels",
            "Pipeline": "Tunnel"
        },
        "pl-PL": {
            "Functions": "Narzędzia",
            "Function": "Narzędzie",
            "Pipelines": "Tunele",
            "Pipeline": "Tunel"
        },
        "ru-RU": {
            "Functions": "Инструменты",
            "Function": "Инструмент",
            "Pipelines": "Туннели",
            "Pipeline": "Туннель"
        },
        "ja-JP": {
            "Functions": "ツール",
            "Function": "ツール",
            "Pipelines": "トンネル",
            "Pipeline": "トンネル"
        },
        "zh-CN": {
            "Functions": "工具",
            "Function": "工具",
            "Pipelines": "隧道",
            "Pipeline": "隧道"
        },
        "zh-TW": {
            "Functions": "工具",
            "Function": "工具",
            "Pipelines": "隧道",
            "Pipeline": "隧道"
        },
        "ko-KR": {
            "Functions": "도구",
            "Function": "도구",
            "Pipelines": "터널",
            "Pipeline": "터널"
        },
        "ar": {
            "Functions": "أدوات",
            "Function": "أداة",
            "Pipelines": "أنفاق",
            "Pipeline": "نفق"
        },
        "tr-TR": {
            "Functions": "Araçlar",
            "Function": "Araç",
            "Pipelines": "Tüneller",
            "Pipeline": "Tünel"
        },
        "sv-SE": {
            "Functions": "Verktyg",
            "Function": "Verktyg",
            "Pipelines": "Tunnlar",
            "Pipeline": "Tunnel"
        },
        "no-NO": {
            "Functions": "Verktøy",
            "Function": "Verktøy",
            "Pipelines": "Tunneler",
            "Pipeline": "Tunnel"
        },
        "da-DK": {
            "Functions": "Værktøjer",
            "Function": "Værktøj",
            "Pipelines": "Tunneler",
            "Pipeline": "Tunnel"
        },
        "fi-FI": {
            "Functions": "Työkalut",
            "Function": "Työkalu",
            "Pipelines": "Tunnelit",
            "Pipeline": "Tunneli"
        }
    }
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir).resolve()
        self.locales_path = self.root_dir / self.LOCALES_DIR
        self.dry_run = dry_run
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "total_replacements": 0,
            "errors": []
        }
    
    def get_locale_translations(self, locale: str) -> Dict[str, str]:
        """Get translations for specific locale, fallback to English"""
        return self.LOCALE_SPECIFIC.get(locale, self.LOCALE_SPECIFIC.get("en-US", {}))
    
    def update_translation_value(self, value: str, locale: str) -> tuple[str, bool]:
        """Update a translation value, return (new_value, changed)"""
        if not isinstance(value, str):
            return value, False
        
        locale_translations = self.get_locale_translations(locale)
        new_value = value
        changed = False
        
        # Apply locale-specific replacements
        for old, new in locale_translations.items():
            if old in new_value:
                new_value = new_value.replace(old, new)
                changed = True
        
        return new_value, changed
    
    def process_json_object(self, obj: dict, locale: str) -> tuple[dict, int]:
        """Recursively process JSON object, return (modified_obj, replacement_count)"""
        count = 0
        modified = {}
        
        for key, value in obj.items():
            if isinstance(value, str):
                new_value, changed = self.update_translation_value(value, locale)
                modified[key] = new_value
                if changed:
                    count += 1
            elif isinstance(value, dict):
                modified[key], sub_count = self.process_json_object(value, locale)
                count += sub_count
            elif isinstance(value, list):
                modified[key] = value  # Don't modify lists
            else:
                modified[key] = value
        
        return modified, count
    
    def process_translation_file(self, file_path: Path) -> int:
        """Process a single translation file"""
        try:
            # Extract locale from path (e.g., "en-US" from "locales/en-US/translation.json")
            locale = file_path.parent.name
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Process the JSON
            modified_data, count = self.process_json_object(data, locale)
            
            if count > 0:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(modified_data, f, ensure_ascii=False, indent='\t')
                
                self.stats["files_modified"] += 1
                self.stats["total_replacements"] += count
                
                rel_path = file_path.relative_to(self.root_dir)
                print(f"  ✓ {rel_path}: {count} replacements")
            
            return count
            
        except Exception as e:
            self.stats["errors"].append(f"Error processing {file_path}: {str(e)}")
            return 0
    
    def scan_locales(self):
        """Scan and process all locale files"""
        print(f"🔍 Scanning translation files in: {self.locales_path}")
        print(f"{'🏃 DRY RUN MODE' if self.dry_run else '✏️  WRITE MODE'}\n")
        
        if not self.locales_path.exists():
            print(f"❌ Error: Locales directory not found: {self.locales_path}")
            return
        
        # Find all translation.json files
        translation_files = list(self.locales_path.glob("*/translation.json"))
        
        print(f"Found {len(translation_files)} locale files\n")
        
        for file_path in sorted(translation_files):
            self.stats["files_processed"] += 1
            self.process_translation_file(file_path)
    
    def print_report(self):
        """Print final report"""
        print("\n" + "="*70)
        print("📊 TRANSLATION UPDATE REPORT")
        print("="*70)
        print(f"Files processed:     {self.stats['files_processed']}")
        print(f"Files modified:      {self.stats['files_modified']}")
        print(f"Total replacements:  {self.stats['total_replacements']}")
        
        if self.stats["errors"]:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:10]:
                print(f"  - {error}")
        
        print("\n" + "="*70)
        
        if self.dry_run:
            print("🏃 This was a DRY RUN - no files were modified")
            print("   Run without --dry-run to apply changes")
        else:
            print("✅ Translation updates complete!")
            print("\n📝 Updated terminology:")
            print("  • Functions → Outils (Tools)")
            print("  • Pipeline → Tunnel")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Pulsai Translation Update - Functions→Outils, Pipeline→Tunnel'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    
    if not root_dir.exists():
        print(f"❌ Error: Directory not found: {root_dir}")
        sys.exit(1)
    
    print("🌐 Pulsai Translation Update Tool")
    print("="*70)
    
    # Run translation updates
    updater = TranslationUpdater(root_dir, dry_run=args.dry_run)
    updater.scan_locales()
    updater.print_report()
    
    if not args.dry_run:
        print("\n📝 Next steps:")
        print("  1. Review changes: git diff src/lib/i18n/locales/")
        print("  2. Test language switcher in UI")
        print("  3. Commit: git add -A && git commit -m 'Update translations: Functions→Outils, Pipeline→Tunnel'")

if __name__ == '__main__':
    main()
