import pytest
import json
from depanalyzer import DependencyAnalyzer

def test_ignored_imports(analyzer, create_test_file):
    """Test that imports in MODULES_TO_IGNORE are properly ignored."""
    test_content = '''
import requests
import json

def fetch_data():
    response = requests.get('https://api.example.com/data')
    return json.loads(response.text)

if __name__ == '__main__':
    data = fetch_data()
'''
    test_file = create_test_file(test_content)
    results = analyzer.analyze_file(test_file)
    assert len(results) == 0, "Expected no results for ignored modules"

def test_simple_import(analyzer, create_test_file):
    """Test analyzing a file with a simple third-party import."""    
    test_content = '''
import pytimeparse

def parse_number():
    return pytimeparse.parse('1h 30m')
'''
    test_file = create_test_file(test_content)
    results = analyzer.analyze_file(test_file)
    print("\nResults from test_simple_import:")
    print(json.dumps(results, indent=2))
    assert len(results) > 0, "Expected to find results for pytimeparse module"
    assert 'pytimeparse' in results, "Expected to find 'pytimeparse' in results"
    assert 'parse' in results['pytimeparse'], "Expected to find 'parse' function in pytimeparse"

def test_simple_from_import(analyzer, create_test_file):
    """Test analyzing a file with a simple third-party import."""    
    test_content = '''
from pytimeparse import parse

def parse_number():
    return parse('1h 30m')
'''
    test_file = create_test_file(test_content)
    results = analyzer.analyze_file(test_file)
    print("\nResults from test_simple_from_import:")
    print(json.dumps(results, indent=2))
    assert len(results) > 0, "Expected to find results for pytimeparse module"
    assert 'pytimeparse' in results, "Expected to find 'pytimeparse' in results"
    assert 'parse' in results['pytimeparse'], "Expected to find 'parse' function in pytimeparse"
