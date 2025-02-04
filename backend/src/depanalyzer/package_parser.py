import os
import ast
from typing import Optional

class PackageParser:
    """Analyzes downloaded Python packages to find function definitions."""

    def find_function_in_file(self, file_path: str, module_name: str, function_name: str) -> Optional[str]:
        """Find a function definition in a Python file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name == function_name:
                        # Get the function source code
                        func_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                        return '\n'.join(func_lines)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == function_name:
                            # Get the assignment source code
                            assign_lines = content.splitlines()[node.lineno-1:node.end_lineno]
                            return '\n'.join(assign_lines)

        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        return None

    def find_api_function(self, package_dir: str, module_name: str, function_name: str) -> str:
        """Find API function definitions that might be defined in various ways."""
        # Common patterns for where functions might be defined
        patterns = [
            f"def {function_name}",
            f"{function_name} = ",
            f"class {function_name}",
        ]
        
        # First try to find in the main module directory
        module_path = os.path.join(package_dir, 'src' if os.path.exists(os.path.join(package_dir, 'src')) else '', module_name.replace('.', '/'))
        if not os.path.exists(module_path):
            module_path = os.path.join(package_dir, module_name.replace('.', '/'))
        
        print(f"Looking for function in: {module_path}")

        # First check __init__.py for any aliases
        init_file = os.path.join(module_path, '__init__.py') if os.path.exists(module_path) else None
        if init_file and os.path.exists(init_file):
            try:
                with open(init_file, 'r') as f:
                    init_content = f.read()
                    
                # Look for import statements that alias our target function
                tree = ast.parse(init_content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for name in node.names:
                            if name.asname == function_name:
                                # We found an alias, now look for the original function
                                original_module = node.module.lstrip('.') if node.module else ''
                                original_name = name.name
                                print(f"Found alias in __init__.py: {function_name} -> {original_module}.{original_name}")
                                
                                # Look for the original function in the relative path
                                relative_module_path = os.path.join(module_path, *original_module.split('.')) if original_module else module_path
                                if os.path.exists(relative_module_path + '.py'):
                                    with open(relative_module_path + '.py', 'r') as f:
                                        content = f.read()
                                        snippet = self.find_function_in_file(relative_module_path + '.py', original_module, original_name)
                                        if snippet:
                                            return f"# Found in {os.path.relpath(relative_module_path + '.py', package_dir)}\n# (imported as {function_name} in __init__.py)\n{snippet}"
            except Exception as e:
                print(f"Error processing __init__.py: {e}")
        
        # If we didn't find it through aliases, look through all Python files
        for root, _, files in os.walk(module_path if os.path.exists(module_path) else package_dir):
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # First try to find exact function definition
                    snippet = self.find_function_in_file(file_path, module_name, function_name)
                    if snippet:
                        return f"# Found in {os.path.relpath(file_path, package_dir)}\n{snippet}"
                        
                    # If not found, look for any of the patterns
                    for pattern in patterns:
                        if pattern in content:
                            # Find the line with the pattern
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if pattern in line:
                                    # Extract a reasonable context (10 lines before and after)
                                    start = max(0, i - 10)
                                    end = min(len(lines), i + 10)
                                    return f"# Found in {os.path.relpath(file_path, package_dir)}\n" + '\n'.join(lines[start:end])
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    continue
        return ""
