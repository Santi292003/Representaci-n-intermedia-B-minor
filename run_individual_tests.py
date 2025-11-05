#!/usr/bin/env python3
# run_individual_tests.py
'''
Ejecutor de pruebas individuales para el analizador semántico
'''

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import *
from Checker import Check
from errors import error_count, reset_errors

def run_single_test(test_name, program, should_pass=True):
    '''Ejecutar una sola prueba'''
    print(f"=== Ejecutando: {test_name} ===")
    reset_errors()
    
    try:
        env = Check.checker(program)
        errors = error_count()
        
        print(f"Errores detectados: {errors}")
        
        if should_pass and errors == 0:
            print("✓ RESULTADO: CORRECTO - No se detectaron errores")
            return True
        elif not should_pass and errors > 0:
            print(f"✓ RESULTADO: CORRECTO - Se detectaron {errors} errores como se esperaba")
            return True
        elif should_pass and errors > 0:
            print(f"✗ RESULTADO: INCORRECTO - Se detectaron {errors} errores inesperados")
            return False
        else:
            print("✗ RESULTADO: INCORRECTO - Se esperaban errores pero no se encontraron")
            return False
            
    except Exception as e:
        print(f"✗ RESULTADO: ERROR - Excepción: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_1_variables_correctas():
    '''Prueba 1: Declaraciones de variables correctas'''
    program = Program([
        VarDecl('a', 'integer', IntegerLit(42), 1),
        VarDecl('b', 'float', FloatLit(3.14), 2),
        VarDecl('c', 'boolean', BooleanLit(True), 3),
    ])
    return run_single_test("Variables con tipos correctos", program, True)

def test_2_variables_incorrectas():
    '''Prueba 2: Declaraciones de variables con tipos incorrectos'''
    program = Program([
        VarDecl('a', 'integer', FloatLit(3.14), 1),  # Error: integer = float
        VarDecl('b', 'boolean', IntegerLit(1), 2),   # Error: boolean = integer
    ])
    return run_single_test("Variables con tipos incorrectos", program, False)

def test_3_funciones_correctas():
    '''Prueba 3: Declaración y llamada de función correcta'''
    program = Program([
        FuncDecl('suma', 'integer', [
            VarParm('x', 'integer'),
            VarParm('y', 'integer')
        ], [
            ReturnStmt(BinOper('+', VarLoc('x'), VarLoc('y')), 3)
        ], 1),
        
        VarDecl('resultado', 'integer', FuncCall('suma', [IntegerLit(5), IntegerLit(3)]), 5)
    ])
    return run_single_test("Función con tipos correctos", program, True)

def test_4_funciones_incorrectas():
    '''Prueba 4: Llamada de función con argumentos incorrectos'''
    program = Program([
        FuncDecl('test', 'void', [VarParm('x', 'integer')], [ReturnStmt(None, 2)], 1),
        ExprStmt(FuncCall('test', [FloatLit(3.14)]), 3)  # Error: argumento incorrecto
    ])
    return run_single_test("Función con argumentos incorrectos", program, False)

def test_5_expresiones_correctas():
    '''Prueba 5: Operaciones binarias correctas'''
    program = Program([
        VarDecl('a', 'integer', IntegerLit(10), 1),
        VarDecl('b', 'integer', IntegerLit(5), 2),
        VarDecl('suma', 'integer', BinOper('+', VarLoc('a'), VarLoc('b')), 3),
        VarDecl('comparacion', 'boolean', BinOper('<', VarLoc('a'), VarLoc('b')), 4),
    ])
    return run_single_test("Expresiones con tipos correctos", program, True)

def test_6_expresiones_incorrectas():
    '''Prueba 6: Operaciones binarias incorrectas'''
    program = Program([
        VarDecl('a', 'integer', IntegerLit(10), 1),
        VarDecl('b', 'float', FloatLit(5.0), 2),
        VarDecl('error', 'integer', BinOper('+', VarLoc('a'), VarLoc('b')), 3)  # Error: integer + float
    ])
    return run_single_test("Expresiones con tipos incompatibles", program, False)

def test_7_variables_no_definidas():
    '''Prueba 7: Uso de variables no definidas'''
    program = Program([
        VarDecl('a', 'integer', VarLoc('no_existe'), 1)  # Error: variable no definida
    ])
    return run_single_test("Variables no definidas", program, False)

def main():
    '''Menú principal para ejecutar pruebas individuales'''
    tests = [
        ("1", "Variables correctas", test_1_variables_correctas),
        ("2", "Variables incorrectas", test_2_variables_incorrectas),
        ("3", "Funciones correctas", test_3_funciones_correctas),
        ("4", "Funciones incorrectas", test_4_funciones_incorrectas),
        ("5", "Expresiones correctas", test_5_expresiones_correctas),
        ("6", "Expresiones incorrectas", test_6_expresiones_incorrectas),
        ("7", "Variables no definidas", test_7_variables_no_definidas),
        ("all", "Todas las pruebas", None)
    ]
    
    if len(sys.argv) > 1:
        # Ejecutar prueba específica desde línea de comandos
        test_num = sys.argv[1]
        
        if test_num == "all":
            print("=== Ejecutando todas las pruebas ===\n")
            passed = 0
            total = len(tests) - 1  # Excluir "all"
            
            for num, name, func in tests[:-1]:  # Excluir "all"
                if func():
                    passed += 1
                print()
            
            print(f"=== Resultado Final ===")
            print(f"Pruebas pasadas: {passed}/{total}")
            return 0 if passed == total else 1
        
        # Buscar y ejecutar prueba específica
        for num, name, func in tests[:-1]:  # Excluir "all"
            if num == test_num:
                success = func()
                return 0 if success else 1
        
        print(f"Error: Prueba '{test_num}' no encontrada")
        print("Pruebas disponibles:", ", ".join([num for num, _, _ in tests]))
        return 1
    
    else:
        # Mostrar menú interactivo
        print("=== Ejecutor de Pruebas Individuales ===")
        print("Selecciona una prueba para ejecutar:")
        print()
        
        for num, name, _ in tests:
            print(f"  {num}: {name}")
        
        print()
        print("Uso:")
        print("  python3 run_individual_tests.py <número>")
        print("  python3 run_individual_tests.py all")
        print()
        print("Ejemplos:")
        print("  python3 run_individual_tests.py 1    # Ejecutar prueba 1")
        print("  python3 run_individual_tests.py all  # Ejecutar todas las pruebas")
        
        return 0

if __name__ == "__main__":
    sys.exit(main())
