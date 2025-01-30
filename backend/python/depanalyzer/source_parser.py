import ast
from typing import Set, List, Tuple, Dict

class SourceParser:
    """Parses Python source files to extract imports and function references."""
    
    def __init__(self, builtin_modules: Set[str]):
        self.builtin_modules = builtin_modules

    def extract_imports(self, file_path: str) -> Set[str]:
        """Extract all package imports from a Python file."""
        with open(file_path, 'r') as f:
            content = f.read()
            tree = ast.parse(content)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

        # Filter out builtin modules
        return {imp for imp in imports if imp not in self.builtin_modules}

    def find_function_references(self, file_path: str) -> List[Tuple[str, str, str]]:
        """Find all function references in a Python file.
        Returns a list of tuples (module_path, function_name, full_name)"""
        with open(file_path, 'r') as f:
            source_content = f.read()
            tree = ast.parse(source_content)

        referenced_functions = []
        imported_names = {}  # Maps imported names to their full module paths

        # First pass: collect all imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imported_names[name.name] = name.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for name in node.names:
                        # For 'from module import function', map the function name to its full path
                        imported_names[name.name] = f"{node.module}.{name.name}"

        # Second pass: find function calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Direct function call (e.g., parse('1h'))
                    func_name = node.func.id
                    if func_name in imported_names:
                        full_path = imported_names[func_name]
                        module = full_path.split('.')[0]
                        referenced_functions.append((module, func_name, full_path))
                elif isinstance(node.func, ast.Attribute):
                    # Module.function call (e.g., pytimeparse.parse('1h'))
                    if isinstance(node.func.value, ast.Name):
                        module_name = node.func.value.id
                        method_name = node.func.attr
                        if module_name in imported_names:
                            full_name = f"{module_name}.{method_name}"
                            referenced_functions.append((module_name, method_name, full_name))

        return referenced_functions
