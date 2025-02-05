import re

# Multipliers for time units
MULTIPLIERS = {
    'years': 31557600,    # 365.25 days
    'months': 2629800,    # 30.44 days
    'weeks': 604800,      # 7 days
    'days': 86400,        # 24 hours
    'hours': 3600,        # 60 minutes
    'minutes': 60,        # 60 seconds
    'seconds': 1,
    'mins': 60,
    'secs': 1,
    'yr': 31557600,
    'y': 31557600,
    'mon': 2629800,
    'w': 604800,
    'd': 86400,
    'h': 3600,
    'm': 60,
    's': 1
}

# Regex patterns for parsing time expressions
SIGN_PATTERN = r'^(?P<sign>[-+])?\s*(?P<unsigned>.*)$'
COMPILED_SIGN = re.compile(SIGN_PATTERN, re.IGNORECASE)

# Time format patterns
TIME_FORMATS = [
    r'^((?P<years>\d+)\s*y(ears?)?)?\s*((?P<months>\d+)\s*mon(ths?)?)?\s*((?P<weeks>\d+)\s*w(eeks?)?)?\s*((?P<days>\d+)\s*d(ays?)?)?\s*((?P<hours>\d+)\s*h(ours?)?)?\s*((?P<minutes>\d+)\s*m(in(utes?)?)?)?\s*((?P<seconds>[\d.]+)\s*s(ec(onds?)?)?)?\s*$',
    r'^(?P<hours>\d+):(?P<minutes>\d+)(:(?P<seconds>\d+))?$',
    r'^(?P<minutes>\d+):(?P<seconds>\d+)$'
]

COMPILED_TIMEFORMATS = [re.compile(fmt, re.IGNORECASE) for fmt in TIME_FORMATS]

def _interpret_as_minutes(sval, mdict):
    """
    Interpret ambiguous time expressions as minutes when granularity is 'minutes'
    """
    if ':' in sval:
        parts = sval.split(':')
        if len(parts) == 2:
            mdict = {'hours': parts[0], 'minutes': parts[1], 'seconds': None}
        elif len(parts) == 3:
            mdict = {'hours': parts[0], 'minutes': parts[1], 'seconds': parts[2]}
    return mdict

def timeparse(sval, granularity='seconds'):
    """
    Parse a time expression, returning it as a number of seconds.
    """
    if not sval:
        return None

    match = COMPILED_SIGN.match(sval)
    sign = -1 if match.groupdict()['sign'] == '-' else 1
    sval = match.groupdict()['unsigned']

    for timefmt in COMPILED_TIMEFORMATS:
        match = timefmt.match(sval)
        if match and match.group(0).strip():
            mdict = match.groupdict()
            if granularity == 'minutes':
                mdict = _interpret_as_minutes(sval, mdict)

            # If all fields are integer numbers
            if all(v.isdigit() for v in list(mdict.values()) if v):
                return sign * sum([MULTIPLIERS[k] * int(v, 10) for (k, v) in
                            list(mdict.items()) if v is not None])
            
            # If seconds is an integer number
            elif ('secs' not in mdict or
                  mdict['secs'] is None or
                  mdict['secs'].isdigit()):
                return (
                    sign * int(sum([MULTIPLIERS[k] * float(v) for (k, v) in
                             list(mdict.items()) if k != 'secs' and v is not None])) +
                    (int(mdict['secs'], 10) if mdict['secs'] else 0))
            else:
                # Seconds is a float
                return sign * sum([MULTIPLIERS[k] * float(v) for (k, v) in
                            list(mdict.items()) if v is not None])

    return None

def parse(sval, granularity='seconds'):
    """
    Alias for timeparse to match original library's interface
    """
    return timeparse(sval, granularity)

print(parse("1:24", 'seconds'))