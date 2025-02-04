"""
Module for inlining Python dependencies using Claude to rewrite source code.
This module takes a Python file and a mapping of dependency functions, then uses
Claude to generate an equivalent version with dependencies inlined.
"""

import os
import anthropic
from typing import Dict, Any

class DependencyInliner:
    def __init__(self, api_key: str = None):
        """Initialize the dependency inliner with optional API key."""
        if not api_key:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        self.client = anthropic.Anthropic(api_key=api_key)

    def inline_dependencies(self, source_file: str, dependency_map: Dict[str, Dict[str, str]]) -> str:
        """
        Generate a new version of the source file with dependencies inlined.
        
        Args:
            source_file: Path to the Python source file to process
            dependency_map: Nested dictionary mapping:
                          {dependency_name: {function_name: function_source}}
        
        Returns:
            str: Rewritten source code with dependencies inlined
        """
        # Read the source file
        with open(source_file, 'r') as f:
            source_code = f.read()

        # Create the prompt for Claude
        prompt = self._create_prompt(source_code, dependency_map)

        # Call Claude to generate the rewritten code
        response = self.client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4000,
            temperature=0,
            system="You are a Python code rewriting assistant. Your task is to inline external dependencies into a single file while maintaining the same functionality.",
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )

        # Extract the rewritten code from Claude's response
        return self._extract_code(response.content[0].text)

    def _create_prompt(self, source_code: str, dependency_map: Dict[str, Dict[str, str]]) -> str:
        """Create the prompt for Claude to rewrite the code."""
        prompt = [
            "Please rewrite the following Python code by inlining all the external dependencies.",
            "The dependencies and their implementations are provided below.",
            "\nOriginal source code:\n```python",
            source_code,
            "```\n",
            "\nDependencies to inline:\n"
        ]

        for dep_name, functions in dependency_map.items():
            prompt.append(f"\nFrom {dep_name}:")
            for func_name, func_code in functions.items():
                prompt.append(f"\n{func_name}:\n```python")
                prompt.append(func_code)
                prompt.append("```")

        prompt.extend([
            "\nPlease provide a single Python file that:",
            "1. Contains all the necessary functionality without external dependencies",
            "2. Maintains the same behavior as the original code",
            "3. Properly handles any name conflicts",
            "4. Includes any necessary imports",
            "5. Is well-organized and readable"
        ])

        return "\n".join(prompt)

    def _extract_code(self, response: str) -> str:
        """Extract the code block from Claude's response."""
        # Look for code between triple backticks
        start = response.find("```python")
        if start == -1:
            start = response.find("```")
        if start == -1:
            return response

        start = response.find("\n", start) + 1
        end = response.find("```", start)
        
        if end == -1:
            return response[start:]
        
        return response[start:end].strip()
