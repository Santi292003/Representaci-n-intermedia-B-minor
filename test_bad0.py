#!/usr/bin/env python3
# test_bad0.py
'''
Prueba específica para bad0.bminor
'''

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import *
from Checker import Check
from errors import error_count, reset_errors

def create_bad0_program():
    '''
    Recrear el programa bad0.bminor como AST:
    
    /* Incorrect type for initializer */
    a: integer = 0.1;
    b: float = 1;
    c: char = a;
    d: array [b] integer = {true, 1, 3, a, b};
    e: integer = "hello\n";
    f: integer = 's';
    g: integer = false;
    h: float = "hello\n";
    i: float = 's';
    j: float = false;
    k: string = 1;
    l: string = 's';
    m: string = false;
    '''
    return Program([
        # Línea 3: a: integer = 0.1;
        VarDecl('a', 'integer', FloatLit(0.1), 3),
        
        # Línea 4: b: float = 1;
        VarDecl('b', 'float', IntegerLit(1), 4),
        
        # Línea 5: c: char = a;
        VarDecl('c', 'char', VarLoc('a'), 5),
        
        # Línea 6: d: array [b] integer = {true, 1, 3, a, b};
        VarDecl('d', 'array[b]integer', ArrayLiteral([
            BooleanLit(True), 
            IntegerLit(1), 
            IntegerLit(3), 
            VarLoc('a'), 
            VarLoc('b')
        ]), 6),
        
        # Línea 7: e: integer = "hello\n";
        VarDecl('e', 'integer', StringLit("hello\\n"), 7),
        
        # Línea 8: f: integer = 's';
        VarDecl('f', 'integer', CharLit('s'), 8),
        
        # Línea 9: g: integer = false;
        VarDecl('g', 'integer', BooleanLit(False), 9),
        
        # Línea 10: h: float = "hello\n";
        VarDecl('h', 'float', StringLit("hello\\n"), 10),
        
        # Línea 11: i: float = 's';
        VarDecl('i', 'float', CharLit('s'), 11),
        
        # Línea 12: j: float = false;
        VarDecl('j', 'float', BooleanLit(False), 12),
        
        # Línea 13: k: string = 1;
        VarDecl('k', 'string', IntegerLit(1), 13),
        
        # Línea 14: l: string = 's';
        VarDecl('l', 'string', CharLit('s'), 14),
        
        # Línea 15: m: string = false;
        VarDecl('m', 'string', BooleanLit(False), 15),
    ])

def test_bad0():
    '''Ejecutar la prueba de bad0.bminor'''
    print("=== Probando bad0.bminor ===")
    print("Archivo: typechecker/bad0.bminor")
    print("Descripción: Incorrect type for initializer")
    print()
    
    reset_errors()
    
    try:
        program = create_bad0_program()
        print(f"Programa creado con {len(program.body)} declaraciones")
        print()
        
        print("Ejecutando analizador semántico...")
        env = Check.checker(program)
        errors = error_count()
        
        print()
        print(f"=== RESULTADOS ===")
        print(f"Errores detectados: {errors}")
        
        if errors > 0:
            print("✓ CORRECTO - Se detectaron errores como se esperaba")
            print()
            print("Este archivo debe fallar porque contiene:")
            print("- Asignaciones de tipos incompatibles")
            print("- integer = float, char = integer, etc.")
            return True
        else:
            print("✗ INCORRECTO - No se detectaron errores")
            print("Este archivo debería fallar la validación semántica")
            return False
            
    except Exception as e:
        print(f"✗ ERROR - Excepción durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    '''Función principal'''
    success = test_bad0()
    
    print()
    if success:
        print("🎉 Prueba de bad0.bminor completada exitosamente")
        return 0
    else:
        print("❌ Prueba de bad0.bminor falló")
        return 1

if __name__ == "__main__":
    sys.exit(main())
