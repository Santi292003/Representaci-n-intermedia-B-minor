'''
Script de prueba del generador de IR usando el parser real
Incluye pruebas de if/else
'''

from parser import parse_string
from Checker import Check
from irgen import IRGenerator
from errors import errors_detected, reset_errors

def test_code(description, code):
    '''
    Prueba un código B-Minor completo
    '''
    print("=" * 70)
    print(f"PRUEBA: {description}")
    print("=" * 70)
    print("\n📄 Código B-Minor:")
    print("-" * 70)
    print(code)
    print("-" * 70)
    
    # Reset errors
    reset_errors()
    
    # Parse
    print("\n🔍 Parseando...")
    ast = parse_string(code)
    
    if ast is None or errors_detected():
        print("❌ Error en el parsing")
        return False
    
    print("✅ Parsing exitoso")
    
    # Semantic check
    print("\n🔍 Análisis semántico...")
    env = Check.checker(ast)
    
    if errors_detected():
        print("❌ Errores en análisis semántico")
        return False
    
    print("✅ Análisis semántico exitoso")
    
    # Generate IR
    print("\n🔍 Generando IR...")
    try:
        module = IRGenerator.generate(ast, env)
        print("✅ IR generado exitosamente")
        
        print("\n📝 Código LLVM IR:")
        print("-" * 70)
        print(str(module))
        print("-" * 70)
        print()
        return True
    except Exception as e:
        print(f"❌ Error generando IR: {e}")
        import traceback
        traceback.print_exc()
        return False

# =====================================================================
# PRUEBAS ANTERIORES
# =====================================================================

def test1_simple_variables():
    code = '''
x: integer = 5;
y: integer = 10;
z: integer = x + y;
'''
    return test_code("Variables simples", code)

def test2_simple_function():
    code = '''
add: function integer (a: integer, b: integer) = {
    result: integer = a + b;
    return result;
}
'''
    return test_code("Función simple", code)

def test3_main_function():
    code = '''
main: function integer () = {
    x: integer = 5;
    y: integer = 10;
    z: integer = x + y;
    return z;
}
'''
    return test_code("Función main", code)

# =====================================================================
# NUEVAS PRUEBAS DE IF/ELSE
# =====================================================================

def test11_simple_if():
    code = '''
max: function integer (a: integer, b: integer) = {
    result: integer = a;
    if (a < b) {
        result = b;
    }
    return result;
}
'''
    return test_code("If simple", code)

def test12_if_else():
    code = '''
max: function integer (a: integer, b: integer) = {
    result: integer;
    if (a > b) {
        result = a;
    } else {
        result = b;
    }
    return result;
}
'''
    return test_code("If-else básico", code)

def test13_nested_if():
    code = '''
classify: function integer (x: integer) = {
    result: integer = 0;
    if (x > 0) {
        if (x > 10) {
            result = 2;
        } else {
            result = 1;
        }
    } else {
        result = -1;
    }
    return result;
}
'''
    return test_code("If anidado", code)

def test14_if_with_complex_condition():
    code = '''
check: function boolean (x: integer, y: integer) = {
    result: boolean = false;
    if (x > 0 && y > 0) {
        result = true;
    }
    return result;
}
'''
    return test_code("If con condición compleja", code)

def test15_if_else_chain():
    code = '''
grade: function integer (score: integer) = {
    result: integer;
    if (score >= 90) {
        result = 4;
    } else {
        if (score >= 80) {
            result = 3;
        } else {
            if (score >= 70) {
                result = 2;
            } else {
                result = 1;
            }
        }
    }
    return result;
}
'''
    return test_code("Cadena de if-else", code)

def test16_if_return():
    code = '''
abs: function integer (x: integer) = {
    if (x < 0) {
        return -x;
    }
    return x;
}
'''
    return test_code("If con return directo", code)

def test17_if_else_both_return():
    code = '''
sign: function integer (x: integer) = {
    if (x >= 0) {
        return 1;
    } else {
        return -1;
    }
}
'''
    return test_code("If-else ambos con return", code)

def test18_if_with_comparison():
    code = '''
compare: function integer (a: integer, b: integer) = {
    if (a == b) {
        return 0;
    }
    if (a > b) {
        return 1;
    }
    return -1;
}
'''
    return test_code("If con comparaciones", code)

def test19_if_with_boolean():
    code = '''
logic_test: function integer (flag: boolean) = {
    result: integer = 0;
    if (flag) {
        result = 1;
    } else {
        result = -1;
    }
    return result;
}
'''
    return test_code("If con booleano", code)

# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 PRUEBAS DEL GENERADOR DE IR CON IF/ELSE")
    print("=" * 70 + "\n")
    
    # Primero algunas pruebas básicas para asegurar que no rompimos nada
    print("\n🔹 PRUEBAS BÁSICAS (Verificación)")
    print("=" * 70)
    basic_tests = [
        ("Variables simples", test1_simple_variables),
        ("Función simple", test2_simple_function),
        ("Función main", test3_main_function),
    ]
    
    basic_passed = 0
    basic_failed = 0
    
    for name, test_func in basic_tests:
        try:
            result = test_func()
            if result:
                basic_passed += 1
            else:
                basic_failed += 1
        except Exception as e:
            print(f"❌ Excepción en {name}: {e}")
            import traceback
            traceback.print_exc()
            basic_failed += 1
        print("\n")
    
    print(f"Básicas: {basic_passed} ✅ / {basic_failed} ❌\n")
    
    # Ahora las pruebas de if/else
    print("\n🔹 PRUEBAS DE IF/ELSE")
    print("=" * 70)
    if_tests = [
        ("If simple", test11_simple_if),
        ("If-else básico", test12_if_else),
        ("If anidado", test13_nested_if),
        ("If con condición compleja", test14_if_with_complex_condition),
        ("Cadena if-else", test15_if_else_chain),
        ("If con return", test16_if_return),
        ("If-else ambos return", test17_if_else_both_return),
        ("If con comparaciones", test18_if_with_comparison),
        ("If con booleano", test19_if_with_boolean),
    ]
    
    if_passed = 0
    if_failed = 0
    
    for name, test_func in if_tests:
        try:
            result = test_func()
            if result:
                if_passed += 1
            else:
                if_failed += 1
        except Exception as e:
            print(f"❌ Excepción en {name}: {e}")
            import traceback
            traceback.print_exc()
            if_failed += 1
        
        print("\n" + "=" * 70 + "\n")
    
    # Resumen final
    total_passed = basic_passed + if_passed
    total_failed = basic_failed + if_failed
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL")
    print("=" * 70)
    print(f"Pruebas básicas: {basic_passed} ✅ / {basic_failed} ❌")
    print(f"Pruebas if/else:  {if_passed} ✅ / {if_failed} ❌")
    print("-" * 70)
    print(f"TOTAL:           {total_passed} ✅ / {total_failed} ❌")
    print("=" * 70 + "\n")