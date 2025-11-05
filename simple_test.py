#!/usr/bin/env python3
# simple_test.py
'''
Simple test runner for the semantic analyzer without external dependencies
'''

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import *
from Checker import Check
from errors import error_count, reset_errors

def create_test_program_good0():
    '''
    Create AST for good0.bminor:
    a: integer = 0;
    b: integer = 1;
    '''
    return Program([
        VarDecl('a', 'integer', IntegerLit(0), 2),
        VarDecl('b', 'integer', IntegerLit(1), 3),
    ])

def create_test_program_bad0():
    '''
    Create AST for bad0.bminor:
    a: integer = 0.1;  // Type mismatch
    '''
    return Program([
        VarDecl('a', 'integer', FloatLit(0.1), 3),
    ])

def run_test(test_name, program, should_pass=True):
    '''
    Run a single test case
    '''
    print(f"Running test: {test_name}")
    reset_errors()
    
    try:
        env = Check.checker(program)
        errors = error_count()
        
        
        if should_pass and errors == 0:
            print(f"  ✓ PASS - No errors detected")
            return True
        elif not should_pass and errors > 0:
            print(f"  ✓ PASS - {errors} errors detected as expected")
            return True
        elif should_pass and errors > 0:
            print(f"  ✗ FAIL - {errors} unexpected errors")
            return False
        else:
            print(f"  ✗ FAIL - Expected errors but none found")
            return False
            
    except Exception as e:
        print(f"  ✗ FAIL - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    '''
    Run all test cases
    '''
    print("Ejecutando pruebas del analizador semántico\n")
    
    tests = [
        ("good0 - Variable declarations", create_test_program_good0(), True),
        ("bad0 - Type mismatches", create_test_program_bad0(), False),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, program, should_pass in tests:
        success = run_test(test_name, program, should_pass)
        if success:
            passed += 1
        print()
    
    print(f"Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("¡Todas las pruebas pasaron!")
        return 0
    else:
        print("Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())
