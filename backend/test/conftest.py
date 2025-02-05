import os
import sys
import tempfile

# Add the python directory to the path so we can import the module
python_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python'))
sys.path.insert(0, python_dir)

import pytest
from src.depanalyzer.dependency_analyzer import DependencyAnalyzer

@pytest.fixture
def analyzer():
    """Provides a fresh DependencyAnalyzer instance for each test."""
    return DependencyAnalyzer()

@pytest.fixture
def create_test_file():
    """Fixture that provides a function to create temporary test files.
    The file will be automatically cleaned up after the test."""
    created_files = []
    
    def _create_file(content: str) -> str:
        """Helper function to create a temporary test file with given content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            created_files.append(f.name)
            return f.name
    
    yield _create_file
    
    # Cleanup all created files after the test
    for file_path in created_files:
        try:
            os.unlink(file_path)
        except OSError:
            pass
