#!/usr/bin/env python3
# comprehensive_test.py
'''
Comprehensive test runner for the semantic analyzer
'''

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import *
from Checker import Check
from errors import error_count, reset_errors

def create_test_good_variables():
    '''Test basic variable declarations with correct types'''
    return Program([
        VarDecl('a', 'integer', IntegerLit(0), 1),
        VarDecl('b', 'float', FloatLit(3.14), 2),
        VarDecl('c', 'boolean', BooleanLit(True), 3),
        VarDecl('d', 'char', CharLit('x'), 4),
        VarDecl('e', 'string', StringLit("hello"), 5),
    ])

def create_test_bad_variables():
    '''Test variable declarations with type mismatches'''
    return Program([
        VarDecl('a', 'integer', FloatLit(3.14), 1),  # integer = float
        VarDecl('b', 'float', IntegerLit(42), 2),    # float = integer
        VarDecl('c', 'boolean', IntegerLit(1), 3),   # boolean = integer
        VarDecl('d', 'char', StringLit("hello"), 4), # char = string
    ])

def create_test_good_functions():
    '''Test function declarations and calls'''
    return Program([
        FuncDecl('add', 'integer', [
            VarParm('x', 'integer'),
            VarParm('y', 'integer')
        ], [
            ReturnStmt(BinOper('+', VarLoc('x'), VarLoc('y')), 4)
        ], 1),
        
        FuncDecl('main', 'void', [], [
            VarDecl('result', 'integer', FuncCall('add', [IntegerLit(5), IntegerLit(3)]), 8),
            ReturnStmt(None, 9)
        ], 7)
    ])

def create_test_bad_functions():
    '''Test function calls with wrong arguments'''
    return Program([
        FuncDecl('test', 'void', [
            VarParm('x', 'integer')
        ], [
            ReturnStmt(None, 3)
        ], 1),
        
        FuncDecl('main', 'void', [], [
            ExprStmt(FuncCall('test', [FloatLit(3.14)]), 7),  # Wrong argument type
            ExprStmt(FuncCall('test', []), 8),                # Missing argument
            ExprStmt(FuncCall('undefined', [IntegerLit(1)]), 9), # Undefined function
        ], 6)
    ])

def create_test_good_expressions():
    '''Test valid binary operations'''
    return Program([
        VarDecl('a', 'integer', IntegerLit(5), 1),
        VarDecl('b', 'integer', IntegerLit(3), 2),
        VarDecl('result1', 'integer', BinOper('+', VarLoc('a'), VarLoc('b')), 3),
        VarDecl('result2', 'boolean', BinOper('<', VarLoc('a'), VarLoc('b')), 4),
    ])

def create_test_bad_expressions():
    '''Test invalid binary operations'''
    return Program([
        VarDecl('a', 'integer', IntegerLit(5), 1),
        VarDecl('b', 'float', FloatLit(3.14), 2),
        VarDecl('bad1', 'integer', BinOper('+', VarLoc('a'), VarLoc('b')), 3), # integer + float
        VarDecl('bad2', 'boolean', BinOper('&&', VarLoc('a'), VarLoc('b')), 4), # integer && float
    ])

def create_test_undefined_variables():
    '''Test usage of undefined variables'''
    return Program([
        VarDecl('a', 'integer', VarLoc('undefined'), 1),  # undefined variable
        VarDecl('b', 'integer', BinOper('+', VarLoc('a'), VarLoc('also_undefined')), 2),
    ])

def run_test(test_name, program, should_pass=True):
    '''Run a single test case'''
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
    '''Run all test cases'''
    print("=== Analizador Semántico - Pruebas Comprehensivas ===\n")
    
    tests = [
        ("Variables válidas", create_test_good_variables(), True),
        ("Variables con tipos incorrectos", create_test_bad_variables(), False),
        ("Funciones válidas", create_test_good_functions(), True),
        ("Funciones con argumentos incorrectos", create_test_bad_functions(), False),
        ("Expresiones válidas", create_test_good_expressions(), True),
        ("Expresiones con tipos incompatibles", create_test_bad_expressions(), False),
        ("Variables no definidas", create_test_undefined_variables(), False),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, program, should_pass in tests:
        success = run_test(test_name, program, should_pass)
        if success:
            passed += 1
        print()
    
    print(f"=== Resultado Final ===")
    print(f"Pruebas pasadas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! El analizador semántico está funcionando correctamente.")
        return 0
    else:
        print("❌ Algunas pruebas fallaron. Revisar la implementación.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
