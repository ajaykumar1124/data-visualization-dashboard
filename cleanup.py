"""
Project Cleanup Script
Removes cache files, temporary files, and other clutter
"""

import os
import shutil
import glob
from pathlib import Path
from typing import List, Dict
import argparse

class ProjectCleaner:
    """
    Comprehensive project cleanup utility
    """
    
    def __init__(self):
        self.cleanup_patterns = {
            'python_cache': [
                '__pycache__',
                '*.pyc',
                '*.pyo', 
                '*.pyd',
                '.pytest_cache',
                '*.egg-info'
            ],
            'temp_files': [
                'temp',
                'tmp',
                '*.tmp',
                '*.temp',
                '.DS_Store',
                'Thumbs.db'
            ],
            'log_files': [
                '*.log',
                'logs',
                '*.out'
            ],
            'backup_files': [
                '*.bak',
                '*.backup',
                '*~',
                '*.swp',
                '*.swo'
            ],
            'build_artifacts': [
                'build',
                'dist',
                '.coverage',
                'htmlcov',
                '.tox',
                '.pytest_cache'
            ]
        }
    
    def scan_project(self, root_path: str = '.') -> Dict[str, List[str]]:
        """
        Scan project for files and directories to clean
        
        Args:
            root_path: Root directory to scan
            
        Returns:
            Dictionary of cleanup categories and found items
        """
        found_items = {category: [] for category in self.cleanup_patterns.keys()}
        
        for root, dirs, files in os.walk(root_path):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            
            for category, patterns in self.cleanup_patterns.items():
                for pattern in patterns:
                    # Check directories
                    if pattern in dirs:
                        full_path = os.path.join(root, pattern)
                        found_items[category].append(full_path)
                    
                    # Check files with glob patterns
                    if '*' in pattern:
                        matches = glob.glob(os.path.join(root, pattern))
                        found_items[category].extend(matches)
                    elif pattern in files:
                        full_path = os.path.join(root, pattern)
                        found_items[category].append(full_path)
        
        # Remove duplicates
        for category in found_items:
            found_items[category] = list(set(found_items[category]))
        
        return found_items
    
    def calculate_size(self, items: List[str]) -> int:
        """
        Calculate total size of files and directories
        
        Args:
            items: List of file/directory paths
            
        Returns:
            Total size in bytes
        """
        total_size = 0
        
        for item in items:
            try:
                if os.path.isfile(item):
                    total_size += os.path.getsize(item)
                elif os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                total_size += os.path.getsize(file_path)
                            except (OSError, FileNotFoundError):
                                pass
            except (OSError, FileNotFoundError):
                pass
        
        return total_size
    
    def clean_items(self, items: List[str], dry_run: bool = False) -> Dict[str, int]:
        """
        Clean specified items
        
        Args:
            items: List of paths to clean
            dry_run: If True, only simulate cleanup
            
        Returns:
            Cleanup statistics
        """
        stats = {
            'files_removed': 0,
            'dirs_removed': 0,
            'errors': 0,
            'size_freed': 0
        }
        
        for item in items:
            try:
                if os.path.exists(item):
                    # Calculate size before removal
                    if os.path.isfile(item):
                        size = os.path.getsize(item)
                        if not dry_run:
                            os.remove(item)
                        stats['files_removed'] += 1
                        stats['size_freed'] += size
                        print(f"{'[DRY RUN] ' if dry_run else ''}Removed file: {item}")
                        
                    elif os.path.isdir(item):
                        size = self.calculate_size([item])
                        if not dry_run:
                            shutil.rmtree(item)
                        stats['dirs_removed'] += 1
                        stats['size_freed'] += size
                        print(f"{'[DRY RUN] ' if dry_run else ''}Removed directory: {item}")
                        
            except Exception as e:
                print(f"Error removing {item}: {e}")
                stats['errors'] += 1
        
        return stats
    
    def clean_project(self, root_path: str = '.', categories: List[str] = None, 
                     dry_run: bool = False) -> Dict[str, Dict[str, int]]:
        """
        Clean entire project
        
        Args:
            root_path: Root directory to clean
            categories: Specific categories to clean (None for all)
            dry_run: If True, only simulate cleanup
            
        Returns:
            Detailed cleanup statistics
        """
        print(f"🧹 {'Scanning' if dry_run else 'Cleaning'} project: {os.path.abspath(root_path)}")
        print("=" * 60)
        
        # Scan for items to clean
        found_items = self.scan_project(root_path)
        
        # Filter categories if specified
        if categories:
            found_items = {k: v for k, v in found_items.items() if k in categories}
        
        total_stats = {}
        grand_total_size = 0
        grand_total_items = 0
        
        for category, items in found_items.items():
            if not items:
                continue
                
            print(f"\n📂 {category.replace('_', ' ').title()}:")
            
            # Calculate size
            total_size = self.calculate_size(items)
            grand_total_size += total_size
            grand_total_items += len(items)
            
            print(f"   Found {len(items)} items ({total_size / 1024 / 1024:.1f} MB)")
            
            # Show some examples
            for item in items[:5]:
                print(f"   • {item}")
            if len(items) > 5:
                print(f"   ... and {len(items) - 5} more")
            
            # Clean items
            if not dry_run:
                stats = self.clean_items(items, dry_run=False)
                total_stats[category] = stats
            else:
                total_stats[category] = {
                    'files_removed': sum(1 for item in items if os.path.isfile(item)),
                    'dirs_removed': sum(1 for item in items if os.path.isdir(item)),
                    'size_freed': total_size,
                    'errors': 0
                }
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 {'Cleanup Summary (DRY RUN)' if dry_run else 'Cleanup Completed'}")
        print("=" * 60)
        
        total_files = sum(stats['files_removed'] for stats in total_stats.values())
        total_dirs = sum(stats['dirs_removed'] for stats in total_stats.values())
        total_errors = sum(stats['errors'] for stats in total_stats.values())
        
        print(f"Files {'would be ' if dry_run else ''}removed: {total_files}")
        print(f"Directories {'would be ' if dry_run else ''}removed: {total_dirs}")
        print(f"Space {'would be ' if dry_run else ''}freed: {grand_total_size / 1024 / 1024:.1f} MB")
        
        if total_errors > 0:
            print(f"Errors encountered: {total_errors}")
        
        if dry_run and grand_total_items > 0:
            print(f"\n💡 Run without --dry-run to actually clean {grand_total_items} items")
        elif not dry_run and grand_total_items > 0:
            print(f"\n✅ Successfully cleaned {grand_total_items} items!")
        else:
            print(f"\n✨ Project is already clean!")
        
        return total_stats


def main():
    """Main cleanup function with command line interface"""
    parser = argparse.ArgumentParser(description='Clean project files and cache')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be cleaned without actually cleaning')
    parser.add_argument('--categories', nargs='+', 
                       choices=['python_cache', 'temp_files', 'log_files', 'backup_files', 'build_artifacts'],
                       help='Specific categories to clean')
    parser.add_argument('--path', default='.', 
                       help='Root path to clean (default: current directory)')
    
    args = parser.parse_args()
    
    cleaner = ProjectCleaner()
    
    try:
        stats = cleaner.clean_project(
            root_path=args.path,
            categories=args.categories,
            dry_run=args.dry_run
        )
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Cleanup interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Cleanup failed: {e}")
        return False


def quick_clean():
    """Quick cleanup function for common use"""
    print("🚀 Quick Project Cleanup")
    print("=" * 30)
    
    cleaner = ProjectCleaner()
    
    # Focus on Python cache and temp files
    categories = ['python_cache', 'temp_files']
    
    try:
        # First show what would be cleaned
        print("📋 Scanning for cleanup items...")
        cleaner.clean_project(categories=categories, dry_run=True)
        
        # Ask for confirmation
        response = input("\n❓ Proceed with cleanup? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            print("\n🧹 Cleaning...")
            cleaner.clean_project(categories=categories, dry_run=False)
        else:
            print("❌ Cleanup cancelled")
            
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # No arguments, run quick clean
        quick_clean()
    else:
        # Run with command line arguments
        success = main()
        sys.exit(0 if success else 1)