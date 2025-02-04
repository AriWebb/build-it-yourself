import os
from typing import Dict, List, Set
import sys
import json

# Add the python directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from .source_parser import SourceParser
from .package_manager import PackageManager
from .package_parser import PackageParser

MODULES_TO_IGNORE = {'requests'}

class DependencyAnalyzer:
    """Analyzes Python files to find and extract relevant code from their dependencies."""

    def __init__(self, packages_dir: str = None):
        if packages_dir is None:
            packages_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'package_sources')
            
        # Initialize components
        self.builtin_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'math', 'random',
            'collections', 'itertools', 'functools', 'typing', 'pathlib',
            'io', 're', 'csv', 'logging', 'unittest', 'argparse',
            'configparser', 'abc', 'ast', 'asyncio', 'base64',
            'builtins', 'contextlib', 'copy', 'enum', 'fnmatch',
            'glob', 'gzip', 'hashlib', 'hmac', 'importlib', 'inspect',
            'json', 'mimetypes', 'numbers', 'operator', 'platform',
            'pprint', 'queue', 'shutil', 'signal', 'socket',
            'sqlite3', 'ssl', 'stat', 'string', 'struct',
            'subprocess', 'tempfile', 'textwrap', 'threading',
            'traceback', 'urllib', 'uuid', 'warnings', 'weakref',
            'xml', 'yaml', 'zipfile', 'zlib'
        } | MODULES_TO_IGNORE
        
        self.source_parser = SourceParser(self.builtin_modules)
        self.package_manager = PackageManager(packages_dir)
        self.package_parser = PackageParser()

    def analyze_file(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """Analyze a Python file and return a dictionary mapping package names to 
        dictionaries of {function_name: source_code}."""
        # Extract imports and find referenced functions
        imports = self.source_parser.extract_imports(file_path)
        referenced_functions = self.source_parser.find_function_references(file_path)
        
        results = {}
        for package_name in imports:
            print(f"Analyzing package {package_name}")
            
            # TODO: In the future, we should get the specific version from:
            # 1. User's requirements.txt or similar dependency file
            # 2. User input/configuration
            # 3. Currently installed version in the environment
            # For now, we'll just download the latest version
            
            package_dir = self.package_manager.download_and_extract_package(package_name)
            if not package_dir:
                continue
                
            # Find all referenced functions from this package
            package_functions = [(m, f, n) for m, f, n in referenced_functions if m == package_name]
            function_snippets = {}
            
            for module_name, function_name, full_name in package_functions:
                snippet = self.package_parser.find_api_function(package_dir, module_name, function_name)
                if snippet:
                    function_snippets[function_name] = snippet
            
            if function_snippets:
                results[package_name] = function_snippets
            else:
                print(f"No snippets found for {package_name}")
        
        return results

def analyze_dependencies(file_path: str) -> Dict[str, Dict[str, str]]:
    """Convenience function to analyze a file's dependencies."""
    analyzer = DependencyAnalyzer()
    return analyzer.analyze_file(file_path)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python dependency_analyzer.py <python_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    results = analyze_dependencies(file_path)
    print(json.dumps(results, indent=2))
