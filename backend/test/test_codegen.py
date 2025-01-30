import os
import pytest
from textwrap import dedent
from python.codegen.dependency_inliner import DependencyInliner

def test_dependency_inliner_pytimeparse(tmp_path):
    # Create a simple test file that uses pytimeparse
    test_file = tmp_path / "test_time.py"
    test_file.write_text(dedent('''
import pytimeparse

def parse_number():
    return pytimeparse.parse('1h 30m')
    ''').strip())

    # Define the dependency map
    dependency_map = {
        "pytimeparse": {
            "parse": '''# Found in pytimeparse/timeparse.py
# (imported as parse in __init__.py)
def timeparse(sval, granularity='seconds'):
    \'\'\'
    Parse a time expression, returning it as a number of seconds.  If
    possible, the return value will be an `int`; if this is not
    possible, the return will be a `float`.  Returns `None` if a time
    expression cannot be parsed from the given string.

    Arguments:
    - `sval`: the string value to parse

    >>> timeparse('1:24')
    84
    >>> timeparse(':22')
    22
    >>> timeparse('1 minute, 24 secs')
    84
    >>> timeparse('1m24s')
    84
    >>> timeparse('1.2 minutes')
    72
    >>> timeparse('1.2 seconds')
    1.2

    Time expressions can be signed.

    >>> timeparse('- 1 minute')
    -60
    >>> timeparse('+ 1 minute')
    60
    
    If granularity is specified as ``minutes``, then ambiguous digits following
    a colon will be interpreted as minutes; otherwise they are considered seconds.
    
    >>> timeparse('1:30')
    90
    >>> timeparse('1:30', granularity='minutes')
    5400
    \'\'\'
    match = COMPILED_SIGN.match(sval)
    sign = -1 if match.groupdict()['sign'] == '-' else 1
    sval = match.groupdict()['unsigned']
    for timefmt in COMPILED_TIMEFORMATS:
        match = timefmt.match(sval)
        if match and match.group(0).strip():
            mdict = match.groupdict()
            if granularity == 'minutes':
                mdict = _interpret_as_minutes(sval, mdict)
            # if all of the fields are integer numbers
            if all(v.isdigit() for v in list(mdict.values()) if v):
                return sign * sum([MULTIPLIERS[k] * int(v, 10) for (k, v) in
                            list(mdict.items()) if v is not None])
            # if SECS is an integer number
            elif ('secs' not in mdict or
                  mdict['secs'] is None or
                  mdict['secs'].isdigit()):
                # we will return an integer
                return (
                    sign * int(sum([MULTIPLIERS[k] * float(v) for (k, v) in
                             list(mdict.items()) if k != 'secs' and v is not None])) +
                    (int(mdict['secs'], 10) if mdict['secs'] else 0))
            else:
                # SECS is a float, we will return a float
                return sign * sum([MULTIPLIERS[k] * float(v) for (k, v) in
                            list(mdict.items()) if v is not None])'''
        }
    }

    # Initialize the dependency inliner
    inliner = DependencyInliner(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    # Generate the inlined code
    inlined_code = inliner.inline_dependencies(str(test_file), dependency_map)

    print(inlined_code)
    
    # Write the inlined code to a new file
    inlined_file = tmp_path / "inlined_time.py"
    inlined_file.write_text(inlined_code)
    
    # Basic assertions about the inlined code
    assert "from pytimeparse import timeparse" not in inlined_code
    assert "def timeparse" in inlined_code
    assert "def process_times" in inlined_code

    # Optional: Import and test the functionality
    import sys
    sys.path.append(str(tmp_path))
    from inlined_time import process_times
    
    # Test the inlined code functionality
    test_times = ["1:24", "2m30s", "45 seconds"]
    expected = [84, 150, 45]
    result = process_times(test_times)
    assert result == expected
