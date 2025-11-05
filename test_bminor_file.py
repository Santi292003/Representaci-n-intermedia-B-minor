#!/usr/bin/env python3
# test_bminor_file.py
'''
Script genérico para probar archivos .bminor específicos
'''

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model import *
from Checker import Check
from errors import error_count, reset_errors

def create_test_programs():
    '''Crear programas de prueba para archivos bminor específicos'''
    
    programs = {
        'bad0': Program([
            # bad0.bminor: Incorrect type for initializer
            VarDecl('a', 'integer', FloatLit(0.1), 3),
            VarDecl('b', 'float', IntegerLit(1), 4),
            VarDecl('c', 'char', VarLoc('a'), 5),
            VarDecl('e', 'integer', StringLit("hello\\n"), 7),
            VarDecl('f', 'integer', CharLit('s'), 8),
            VarDecl('g', 'integer', BooleanLit(False), 9),
        ]),
        
        'bad1': Program([
            # bad1.bminor: functions of incorrect types
            FuncDecl('a', 'array[1]integer', [], [
                ReturnStmt(None, 4)  # Error: should return array but returns void
            ], 3),
            
            FuncDecl('b', 'void', [], [
                VarDecl('c', 'function_integer', None, 8),
                ReturnStmt(IntegerLit(1), 9)  # Error: void function returning integer
            ], 7)
        ]),
        
        'good0': Program([
            # good0.bminor: Variable declarations (should pass)
            VarDecl('a', 'integer', IntegerLit(0), 2),
            VarDecl('b', 'integer', IntegerLit(1), 3),
            VarDecl('d', 'float', FloatLit(45.67), 5),
            VarDecl('e', 'boolean', BooleanLit(False), 6),
            VarDecl('f', 'char', CharLit('q'), 7),
            VarDecl('g', 'string', StringLit("hello bminor\\n"), 8),
        ]),
        
        'good1': Program([
            # good1.bminor: Function declarations (should pass)
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
    }
    
    return programs

def test_file(filename):
    '''Probar un archivo específico'''
    programs = create_test_programs()
    
    if filename not in programs:
        print(f"❌ Error: No hay prueba disponible para '{filename}'")
        print(f"Archivos disponibles: {', '.join(programs.keys())}")
        return False
    
    print(f"=== Probando {filename}.bminor ===")
    print(f"Archivo: typechecker/{filename}.bminor")
    
    # Determinar si debe pasar o fallar
    should_pass = filename.startswith('good')
    expected = "PASAR" if should_pass else "FALLAR"
    print(f"Resultado esperado: {expected}")
    print()
    
    reset_errors()
    
    try:
        program = programs[filename]
        print(f"Programa creado con {len(program.body)} declaraciones")
        print()
        
        print("Ejecutando analizador semántico...")
        env = Check.checker(program)
        errors = error_count()
        
        print()
        print(f"=== RESULTADOS ===")
        print(f"Errores detectados: {errors}")
        
        success = False
        if should_pass and errors == 0:
            print("✓ CORRECTO - No se detectaron errores (como se esperaba)")
            success = True
        elif not should_pass and errors > 0:
            print("✓ CORRECTO - Se detectaron errores (como se esperaba)")
            success = True
        elif should_pass and errors > 0:
            print("✗ INCORRECTO - Se detectaron errores inesperados")
        else:
            print("✗ INCORRECTO - No se detectaron errores cuando se esperaban")
        
        return success
        
    except Exception as e:
        print(f"✗ ERROR - Excepción durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    '''Función principal'''
    if len(sys.argv) != 2:
        print("=== Probador de Archivos .bminor ===")
        print()
        print("Uso:")
        print("  python3 test_bminor_file.py <nombre_archivo>")
        print()
        print("Ejemplos:")
        print("  python3 test_bminor_file.py bad0")
        print("  python3 test_bminor_file.py bad1") 
        print("  python3 test_bminor_file.py good0")
        print("  python3 test_bminor_file.py good1")
        print()
        
        # Mostrar archivos disponibles
        programs = create_test_programs()
        print("Archivos disponibles:")
        for filename in sorted(programs.keys()):
            file_type = "✓ Debe pasar" if filename.startswith('good') else "✗ Debe fallar"
            print(f"  {filename} - {file_type}")
        
        return 1
    
    filename = sys.argv[1]
    success = test_file(filename)
    
    print()
    if success:
        print(f"🎉 Prueba de {filename}.bminor completada exitosamente")
        return 0
    else:
        print(f"❌ Prueba de {filename}.bminor falló")
        return 1

if __name__ == "__main__":
    sys.exit(main())
