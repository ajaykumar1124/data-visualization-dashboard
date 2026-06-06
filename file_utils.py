"""
File Utilities Module
Handles file reading with multiple encodings and cleanup operations
"""

import os
import shutil
import chardet
import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """
    Robust file handler that can read files with various encodings
    """
    
    def __init__(self):
        # Common encodings to try
        self.encodings = [
            'utf-8',
            'utf-8-sig',  # UTF-8 with BOM
            'latin-1',
            'cp1252',     # Windows-1252
            'iso-8859-1',
            'ascii'
        ]
    
    def detect_encoding(self, file_path: str) -> str:
        """
        Detect file encoding using chardet
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding or 'utf-8' as fallback
        """
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(10000)  # Read first 10KB for detection
                result = chardet.detect(raw_data)
                
                if result and result['encoding']:
                    confidence = result.get('confidence', 0)
                    encoding = result['encoding']
                    
                    logger.info(f"Detected encoding: {encoding} (confidence: {confidence:.2f})")
                    
                    # Return detected encoding if confidence is high enough
                    if confidence > 0.7:
                        return encoding
                    
        except Exception as e:
            logger.warning(f"Encoding detection failed: {e}")
        
        # Fallback to UTF-8
        return 'utf-8'
    
    def read_text_file(self, file_path: str, encoding: Optional[str] = None) -> str:
        """
        Read text file with automatic encoding detection
        
        Args:
            file_path: Path to the file
            encoding: Specific encoding to use (optional)
            
        Returns:
            File content as string
        """
        if encoding:
            encodings_to_try = [encoding]
        else:
            # Try detected encoding first, then common encodings
            detected = self.detect_encoding(file_path)
            encodings_to_try = [detected] + [enc for enc in self.encodings if enc != detected]
        
        for enc in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=enc, errors='replace') as file:
                    content = file.read()
                    logger.info(f"Successfully read file with encoding: {enc}")
                    return content
                    
            except UnicodeDecodeError:
                logger.warning(f"Failed to read with encoding: {enc}")
                continue
            except Exception as e:
                logger.error(f"Error reading file with {enc}: {e}")
                continue
        
        # Last resort: read as binary and decode with errors='replace'
        try:
            with open(file_path, 'rb') as file:
                raw_content = file.read()
                content = raw_content.decode('utf-8', errors='replace')
                logger.warning("Used fallback binary reading with error replacement")
                return content
        except Exception as e:
            logger.error(f"Failed to read file even with fallback method: {e}")
            raise
    
    def read_csv_robust(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read CSV file with robust encoding handling
        
        Args:
            file_path: Path to CSV file
            **kwargs: Additional pandas read_csv parameters
            
        Returns:
            DataFrame
        """
        # Try to detect encoding first
        detected_encoding = self.detect_encoding(file_path)
        
        encodings_to_try = [detected_encoding] + [
            enc for enc in self.encodings if enc != detected_encoding
        ]
        
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding, **kwargs)
                logger.info(f"Successfully read CSV with encoding: {encoding}")
                return df
                
            except UnicodeDecodeError:
                logger.warning(f"CSV read failed with encoding: {encoding}")
                continue
            except Exception as e:
                logger.warning(f"CSV read error with {encoding}: {e}")
                continue
        
        # Final attempt with error handling
        try:
            df = pd.read_csv(file_path, encoding='utf-8', errors='replace', **kwargs)
            logger.warning("Used UTF-8 with error replacement for CSV")
            return df
        except Exception as e:
            logger.error(f"Failed to read CSV file: {e}")
            raise
    
    def read_excel_robust(self, file_path: str, **kwargs) -> pd.DataFrame:
        """
        Read Excel file with error handling
        
        Args:
            file_path: Path to Excel file
            **kwargs: Additional pandas read_excel parameters
            
        Returns:
            DataFrame
        """
        try:
            df = pd.read_excel(file_path, **kwargs)
            logger.info("Successfully read Excel file")
            return df
            
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            
            # Try different engines
            engines = ['openpyxl', 'xlrd']
            
            for engine in engines:
                try:
                    df = pd.read_excel(file_path, engine=engine, **kwargs)
                    logger.info(f"Successfully read Excel with engine: {engine}")
                    return df
                except Exception as engine_error:
                    logger.warning(f"Engine {engine} failed: {engine_error}")
                    continue
            
            raise Exception(f"Could not read Excel file with any available engine: {e}")
    
    def write_text_safe(self, file_path: str, content: str, encoding: str = 'utf-8'):
        """
        Write text file safely with proper encoding
        
        Args:
            file_path: Output file path
            content: Text content to write
            encoding: Encoding to use (default: utf-8)
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding, newline='') as file:
                file.write(content)
                
            logger.info(f"Successfully wrote file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to write file {file_path}: {e}")
            raise


class CacheManager:
    """
    Manages Python cache files and temporary directories
    """
    
    def __init__(self):
        self.cache_patterns = [
            '__pycache__',
            '*.pyc',
            '*.pyo',
            '*.pyd',
            '.pytest_cache',
            '.coverage',
            '*.egg-info'
        ]
    
    def find_cache_directories(self, root_path: str = '.') -> List[str]:
        """
        Find all cache directories in the project
        
        Args:
            root_path: Root directory to search
            
        Returns:
            List of cache directory paths
        """
        cache_dirs = []
        
        for root, dirs, files in os.walk(root_path):
            # Check for __pycache__ directories
            if '__pycache__' in dirs:
                cache_path = os.path.join(root, '__pycache__')
                cache_dirs.append(cache_path)
            
            # Check for other cache patterns
            for pattern in self.cache_patterns:
                if pattern.startswith('.') and pattern in dirs:
                    cache_path = os.path.join(root, pattern)
                    cache_dirs.append(cache_path)
        
        return cache_dirs
    
    def find_cache_files(self, root_path: str = '.') -> List[str]:
        """
        Find all cache files in the project
        
        Args:
            root_path: Root directory to search
            
        Returns:
            List of cache file paths
        """
        cache_files = []
        
        for root, dirs, files in os.walk(root_path):
            for file in files:
                if (file.endswith('.pyc') or 
                    file.endswith('.pyo') or 
                    file.endswith('.pyd')):
                    cache_file = os.path.join(root, file)
                    cache_files.append(cache_file)
        
        return cache_files
    
    def clean_cache(self, root_path: str = '.', dry_run: bool = False) -> Dict[str, int]:
        """
        Clean all cache files and directories
        
        Args:
            root_path: Root directory to clean
            dry_run: If True, only report what would be deleted
            
        Returns:
            Dictionary with cleanup statistics
        """
        stats = {
            'directories_removed': 0,
            'files_removed': 0,
            'space_freed_mb': 0,
            'errors': 0
        }
        
        # Find cache directories
        cache_dirs = self.find_cache_directories(root_path)
        cache_files = self.find_cache_files(root_path)
        
        # Calculate space that would be freed
        total_size = 0
        
        for cache_dir in cache_dirs:
            try:
                dir_size = self._get_directory_size(cache_dir)
                total_size += dir_size
                
                if not dry_run:
                    shutil.rmtree(cache_dir)
                    logger.info(f"Removed cache directory: {cache_dir}")
                else:
                    logger.info(f"Would remove cache directory: {cache_dir}")
                
                stats['directories_removed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to remove cache directory {cache_dir}: {e}")
                stats['errors'] += 1
        
        for cache_file in cache_files:
            try:
                file_size = os.path.getsize(cache_file)
                total_size += file_size
                
                if not dry_run:
                    os.remove(cache_file)
                    logger.info(f"Removed cache file: {cache_file}")
                else:
                    logger.info(f"Would remove cache file: {cache_file}")
                
                stats['files_removed'] += 1
                
            except Exception as e:
                logger.error(f"Failed to remove cache file {cache_file}: {e}")
                stats['errors'] += 1
        
        stats['space_freed_mb'] = total_size / (1024 * 1024)
        
        return stats
    
    def _get_directory_size(self, directory: str) -> int:
        """Get total size of directory in bytes"""
        total_size = 0
        
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
        except Exception:
            pass
        
        return total_size


def clean_project_cache():
    """
    Clean all Python cache files in the project
    """
    print("🧹 Cleaning Python Cache Files...")
    
    cache_manager = CacheManager()
    
    # First, show what would be cleaned (dry run)
    print("\n📋 Scanning for cache files...")
    dry_stats = cache_manager.clean_cache(dry_run=True)
    
    print(f"Found:")
    print(f"  • {dry_stats['directories_removed']} cache directories")
    print(f"  • {dry_stats['files_removed']} cache files")
    print(f"  • {dry_stats['space_freed_mb']:.1f} MB to be freed")
    
    if dry_stats['directories_removed'] > 0 or dry_stats['files_removed'] > 0:
        # Actually clean the cache
        print("\n🗑️ Cleaning cache...")
        actual_stats = cache_manager.clean_cache(dry_run=False)
        
        print(f"✅ Cleanup completed:")
        print(f"  • Removed {actual_stats['directories_removed']} directories")
        print(f"  • Removed {actual_stats['files_removed']} files")
        print(f"  • Freed {actual_stats['space_freed_mb']:.1f} MB")
        
        if actual_stats['errors'] > 0:
            print(f"  ⚠️ {actual_stats['errors']} errors occurred")
    else:
        print("✅ No cache files found to clean")


def test_file_reading():
    """
    Test file reading with various encodings
    """
    print("📖 Testing File Reading Capabilities...")
    
    file_handler = FileHandler()
    
    # Test with sample files if they exist
    test_files = [
        'requirements.txt',
        'README.md',
        'dashboard.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            try:
                print(f"\n📄 Testing: {test_file}")
                
                # Detect encoding
                encoding = file_handler.detect_encoding(test_file)
                print(f"   Detected encoding: {encoding}")
                
                # Read file
                content = file_handler.read_text_file(test_file)
                print(f"   ✅ Successfully read {len(content)} characters")
                
                # Show first few lines
                lines = content.split('\n')[:3]
                for i, line in enumerate(lines, 1):
                    preview = line[:50] + "..." if len(line) > 50 else line
                    print(f"   Line {i}: {preview}")
                
            except Exception as e:
                print(f"   ❌ Failed to read {test_file}: {e}")
        else:
            print(f"   ⚠️ File not found: {test_file}")


if __name__ == "__main__":
    print("🛠️ File Utilities - Testing and Cleanup")
    print("=" * 50)
    
    # Test file reading
    test_file_reading()
    
    print("\n" + "=" * 50)
    
    # Clean cache
    clean_project_cache()
    
    print("\n🎉 File utilities testing completed!")
    print("\n💡 Usage examples:")
    print("   from file_utils import FileHandler, CacheManager")
    print("   handler = FileHandler()")
    print("   content = handler.read_text_file('myfile.txt')")
    print("   df = handler.read_csv_robust('data.csv')")