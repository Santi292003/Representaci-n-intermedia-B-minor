#!/usr/bin/env python3
# test_runner.py
'''
Test runner for the semantic analyzer
This creates simple AST nodes to test the semantic analyzer functionality
'''

import os
import sys
from rich import print
from rich.console import Console
from rich.table import Table

from model import *
from Checker import Check
from errors import error_count, reset_errors

console = Console()

def create_test_program_good0():
    '''
    Create AST for good0.bminor:
    /* Variable declarations */
    a: integer = 0;
    b: integer = 1;
    c: integer = -1;
    d: float = 45.67;
    e: boolean = false;
    f: char = 'q';
    g: string = "hello bminor\n";
    '''
    return Program([
        VarDecl('a', 'integer', IntegerLit(0), 2),
        VarDecl('b', 'integer', IntegerLit(1), 3),
        VarDecl('c', 'integer', UnaryOper('-', IntegerLit(1)), 4),
        VarDecl('d', 'float', FloatLit(45.67), 5),
        VarDecl('e', 'boolean', BooleanLit(False), 6),
        VarDecl('f', 'char', CharLit('q'), 7),
        VarDecl('g', 'string', StringLit("hello bminor\\n"), 8),
    ])

def create_test_program_good1():
    '''
    Create AST for good1.bminor:
    /* Function declarations */
    a: function void (arg1: integer, arg2: integer) = {
        return;
    }
    
    b: function integer (arg1: array [2] integer) = {
        a(arg1[0], arg1[1]);
        return 1 + arg1[0];
    }
    '''
    return Program([
        FuncDecl('a', 'void', [
            VarParm('arg1', 'integer'),
            VarParm('arg2', 'integer')
        ], [
            ReturnStmt(None, 3)
        ], 2),
        
        FuncDecl('b', 'integer', [
            VarParm('arg1', 'array[2]integer')
        ], [
            ExprStmt(FuncCall('a', [
                ArrayLoc(VarLoc('arg1'), IntegerLit(0)),
                ArrayLoc(VarLoc('arg1'), IntegerLit(1))
            ]), 7),
            ReturnStmt(BinOper('+', IntegerLit(1), ArrayLoc(VarLoc('arg1'), IntegerLit(0))), 8)
        ], 6)
    ])

def create_test_program_bad0():
    '''
    Create AST for bad0.bminor:
    /* Incorrect type for initializer */
    a: integer = 0.1;
    b: float = 1;
    c: char = a;
    '''
    return Program([
        VarDecl('a', 'integer', FloatLit(0.1), 3),
        VarDecl('b', 'float', IntegerLit(1), 4),
        VarDecl('c', 'char', VarLoc('a'), 5),
    ])

def create_test_program_bad1():
    '''
    Create AST for bad1.bminor:
    /* functions of incorrect types */
    a: function array [1] integer () = {
        return;
    }
    
    b: function void () = {
        c: function integer();
        return 1;
    }
    '''
    return Program([
        FuncDecl('a', 'array[1]integer', [], [
            ReturnStmt(None, 4)
        ], 3),
        
        FuncDecl('b', 'void', [], [
            VarDecl('c', 'function_integer', None, 8),
            ReturnStmt(IntegerLit(1), 9)
        ], 7)
    ])

def create_test_program_bad2():
    '''
    Create AST for bad2.bminor (function call with wrong arguments):
    '''
    return Program([
        VarDecl('arr', 'array[5]integer', ArrayLiteral([
            IntegerLit(1), IntegerLit(2), IntegerLit(3), IntegerLit(4), IntegerLit(5)
        ]), 3),
        
        FuncDecl('a', 'void', [
            VarParm('arg1', 'integer'),
            VarParm('arg2', 'float'),
            VarParm('arg3', 'char'),
            VarParm('arg4', 'string'),
            VarParm('arg5', 'array[]integer')
        ], [
            ReturnStmt(None, 7)
        ], 5),
        
        FuncDecl('main', 'void', [], [
            VarDecl('i', 'integer', IntegerLit(0), 12),
            VarDecl('f', 'float', FloatLit(3.14), 13),
            
            # Wrong number of arguments
            ExprStmt(FuncCall('a', [
                VarLoc('i'), VarLoc('f'), CharLit('c'), StringLit("string")
            ]), 18),
            
            # Wrong argument types
            ExprStmt(FuncCall('a', [
                VarLoc('f'), VarLoc('i'), StringLit("string"), VarLoc('arr')
            ]), 19),
        ], 11)
    ])

def run_test(test_name, program, should_pass=True):
    '''
    Run a single test case
    '''
    reset_errors()
    
    try:
        env = Check.checker(program)
        errors = error_count()
        
        if should_pass and errors == 0:
            return True, f"✓ PASS - No errors detected"
        elif not should_pass and errors > 0:
            return True, f"✓ PASS - {errors} errors detected as expected"
        elif should_pass and errors > 0:
            return False, f"✗ FAIL - {errors} unexpected errors"
        else:
            return False, f"✗ FAIL - Expected errors but none found"
            
    except Exception as e:
        return False, f"✗ FAIL - Exception: {e}"

def main():
    '''
    Run all test cases
    '''
    console.print("\n[bold blue]Ejecutando pruebas del analizador semántico[/bold blue]\n")
    
    tests = [
        ("good0 - Variable declarations", create_test_program_good0(), True),
        ("good1 - Function declarations", create_test_program_good1(), True),
        ("bad0 - Type mismatches", create_test_program_bad0(), False),
        ("bad1 - Function return type errors", create_test_program_bad1(), False),
        ("bad2 - Function call errors", create_test_program_bad2(), False),
    ]
    
    table = Table(title="Resultados de las Pruebas")
    table.add_column("Test", style="cyan")
    table.add_column("Resultado", style="green")
    table.add_column("Descripción")
    
    passed = 0
    total = len(tests)
    
    for test_name, program, should_pass in tests:
        success, message = run_test(test_name, program, should_pass)
        if success:
            passed += 1
        
        table.add_row(test_name, "PASS" if success else "FAIL", message)
    
    console.print(table)
    console.print(f"\n[bold]Resultado: {passed}/{total} pruebas pasaron[/bold]")
    
    if passed == total:
        console.print("[green]¡Todas las pruebas pasaron![/green]")
        return 0
    else:
        console.print("[red]Algunas pruebas fallaron[/red]")
        return 1

if __name__ == "__main__":
    sys.exit(main())
