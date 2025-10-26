#!/usr/bin/env python3
"""
Pulsai Rebranding Script
Automated replacement of Open Web UI → Pulsai across the codebase
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import argparse

@dataclass
class RebrandStats:
    """Statistics for rebranding operations"""
    files_scanned: int = 0
    files_modified: int = 0
    total_replacements: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class PulsaiRebrander:
    """Main rebranding engine"""
    
    # Files and directories to exclude
    EXCLUDE_DIRS = {
        '.git', 'node_modules', '__pycache__', '.venv', 'venv',
        'dist', 'build', '.cursor', '.cache', 'pyodide', 'static/static'
    }
    
    EXCLUDE_FILES = {
        'LICENSE', 'LICENSE_HISTORY', 'CONTRIBUTOR_LICENSE_AGREEMENT',
        '.gitignore', 'package-lock.json', 'poetry.lock', 'rye.lock',
        'rebrand.py'  # Don't rebrand this script itself
    }
    
    # File extensions to process
    INCLUDE_EXTENSIONS = {
        '.py', '.svelte', '.ts', '.js', '.json', '.yaml', '.yml',
        '.md', '.txt', '.toml', '.html', '.css', '.sh', '.dockerfile',
        '.xml', '.env.example'
    }
    
    # Replacement patterns (order matters for specificity)
    REPLACEMENTS = {
        # Exact matches first
        'Open WebUI': 'Pulsai',
        'Open Web UI': 'Pulsai',
        'OpenWebUI': 'Pulsai',
        'open-webui': 'pulsai',
        'open_webui': 'pulsai',
        'WEBUI_NAME': 'PULSAI_NAME',
        'WEBUI_VERSION': 'PULSAI_VERSION',
        'WEBUI_API': 'PULSAI_API',
        'webui.sh': 'pulsai.sh',
        'webui.py': 'pulsai.py',
        
        # URLs and repos
        'github.com/open-webui/open-webui': 'github.com/pulsai/pulsai',
        'ghcr.io/open-webui': 'ghcr.io/pulsai',
        'open-webui.com': 'pulsai.com',
        
        # Docker images
        'ghcr.io/open-webui/open-webui': 'ghcr.io/pulsai/pulsai',
        'open-webui:': 'pulsai:',
    }
    
    # Context-sensitive replacements (require regex)
    CONTEXT_PATTERNS = [
        # Variable names but not in comments
        (r'\bWEBUI\b(?![\s\-_])', 'PULSAI'),
        (r'\bWebUI\b(?![\s\-_])', 'Pulsai'),
        (r'\bwebui\b(?![\s\-_])', 'pulsai'),
    ]
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.stats = RebrandStats()
        
    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Check if in excluded directory
        for part in file_path.parts:
            if part in self.EXCLUDE_DIRS:
                return False
        
        # Check if excluded filename
        if file_path.name in self.EXCLUDE_FILES:
            return False
        
        # Check extension
        if file_path.suffix not in self.INCLUDE_EXTENSIONS:
            # Also check for no extension (like Dockerfile)
            if file_path.suffix == '' and file_path.name not in {'Dockerfile', 'Makefile'}:
                return False
        
        return True
    
    def replace_in_content(self, content: str, file_path: Path) -> Tuple[str, int]:
        """Replace all occurrences in content"""
        modified_content = content
        replacement_count = 0
        
        # Special handling for JSON files (preserve structure)
        is_json = file_path.suffix == '.json'
        
        # Apply direct replacements
        for old, new in self.REPLACEMENTS.items():
            if old in modified_content:
                count = modified_content.count(old)
                modified_content = modified_content.replace(old, new)
                replacement_count += count
        
        # Apply context-sensitive regex patterns
        for pattern, replacement in self.CONTEXT_PATTERNS:
            matches = re.findall(pattern, modified_content)
            if matches:
                modified_content = re.sub(pattern, replacement, modified_content)
                replacement_count += len(matches)
        
        return modified_content, replacement_count
    
    def process_file(self, file_path: Path) -> int:
        """Process a single file"""
        try:
            # Read file with encoding detection
            encodings = ['utf-8', 'latin-1', 'cp1252']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                self.stats.errors.append(f"Could not decode: {file_path}")
                return 0
            
            # Apply replacements
            modified_content, count = self.replace_in_content(content, file_path)
            
            if count > 0:
                if not self.dry_run:
                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                
                self.stats.files_modified += 1
                return count
            
            return 0
            
        except Exception as e:
            self.stats.errors.append(f"Error processing {file_path}: {str(e)}")
            return 0
    
    def scan_directory(self) -> None:
        """Recursively scan and process directory"""
        print(f"🔍 Scanning directory: {self.root_dir}")
        print(f"{'🏃 DRY RUN MODE' if self.dry_run else '✏️  WRITE MODE'}\n")
        
        for file_path in self.root_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            self.stats.files_scanned += 1
            
            # Show progress every 50 files
            if self.stats.files_scanned % 50 == 0:
                print(f"  Scanned {self.stats.files_scanned} files...", end='\r')
            
            replacements = self.process_file(file_path)
            if replacements > 0:
                self.stats.total_replacements += replacements
                rel_path = file_path.relative_to(self.root_dir)
                print(f"  ✓ {rel_path}: {replacements} replacements")
    
    def print_report(self) -> None:
        """Print final report"""
        print("\n" + "="*70)
        print("📊 REBRANDING REPORT")
        print("="*70)
        print(f"Files scanned:       {self.stats.files_scanned}")
        print(f"Files modified:      {self.stats.files_modified}")
        print(f"Total replacements:  {self.stats.total_replacements}")
        
        if self.stats.errors:
            print(f"\n⚠️  Errors encountered: {len(self.stats.errors)}")
            for error in self.stats.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.stats.errors) > 10:
                print(f"  ... and {len(self.stats.errors) - 10} more")
        
        print("\n" + "="*70)
        
        if self.dry_run:
            print("🏃 This was a DRY RUN - no files were modified")
            print("   Run without --dry-run to apply changes")
        else:
            print("✅ Rebranding complete!")
            print("   Review changes and run tests before committing")
    
    def verify_changes(self) -> List[str]:
        """Verify no unwanted patterns remain"""
        unwanted_patterns = [
            'Open WebUI',
            'Open Web UI',
            'OpenWebUI',
            'open-webui',
            'open_webui'
        ]
        
        findings = []
        
        for file_path in self.root_dir.rglob('*'):
            if not file_path.is_file():
                continue
            
            if not self.should_process_file(file_path):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                for pattern in unwanted_patterns:
                    if pattern in content:
                        rel_path = file_path.relative_to(self.root_dir)
                        findings.append(f"{rel_path}: found '{pattern}'")
            except Exception:
                pass
        
        return findings

def main():
    parser = argparse.ArgumentParser(
        description='Pulsai Rebranding Script - Replace Open Web UI → Pulsai'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify no unwanted patterns remain after rebranding'
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to process (default: current directory)'
    )
    
    args = parser.parse_args()
    
    root_dir = Path(args.root).resolve()
    
    if not root_dir.exists():
        print(f"❌ Error: Directory not found: {root_dir}")
        sys.exit(1)
    
    print("🎨 Pulsai Rebranding Tool")
    print("="*70)
    
    if args.verify:
        print("🔍 Verification mode - checking for remaining patterns...\n")
        rebrander = PulsaiRebrander(root_dir, dry_run=True)
        findings = rebrander.verify_changes()
        
        if findings:
            print(f"⚠️  Found {len(findings)} files with old branding:\n")
            for finding in findings[:20]:
                print(f"  - {finding}")
            if len(findings) > 20:
                print(f"  ... and {len(findings) - 20} more")
            sys.exit(1)
        else:
            print("✅ Verification passed - no old branding found!")
            sys.exit(0)
    
    # Confirm if not dry-run
    if not args.dry_run:
        print(f"⚠️  This will modify files in: {root_dir}")
        response = input("Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Run rebranding
    rebrander = PulsaiRebrander(root_dir, dry_run=args.dry_run)
    rebrander.scan_directory()
    rebrander.print_report()
    
    # Suggest next steps
    if not args.dry_run:
        print("\n📝 Recommended next steps:")
        print("  1. Review changes: git diff")
        print("  2. Run verification: python scripts/rebrand.py --verify")
        print("  3. Test the application")
        print("  4. Commit changes: git add -A && git commit -m 'Rebrand to Pulsai'")

if __name__ == '__main__':
    main()

