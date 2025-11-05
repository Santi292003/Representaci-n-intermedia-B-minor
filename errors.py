# errors.py
'''
Error handling for the bminor compiler
'''

import sys

# Global error counter
_error_count = 0

def error(message, lineno=0):
    '''
    Report an error message
    '''
    global _error_count
    _error_count += 1
    if lineno > 0:
        print(f"Error en línea {lineno}: {message}", file=sys.stderr)
    else:
        print(f"Error: {message}", file=sys.stderr)

def errors_detected():
    '''
    Return True if any errors have been detected
    '''
    return _error_count > 0

def error_count():
    '''
    Return the number of errors detected
    '''
    return _error_count

def reset_errors():
    '''
    Reset the error count (useful for testing)
    '''
    global _error_count
    _error_count = 0
