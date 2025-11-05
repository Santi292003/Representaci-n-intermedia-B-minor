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

def test20_while_basic():
    code = '''
main: function integer () = {
    i: integer = 3;
    acc: integer = 0;
    while (i > 0) {
        acc = acc + i;
        i = i - 1;
    }
    return acc;  // 3+2+1 = 6
}
'''
    return test_code("While básico", code)


def test21_short_circuit_logic():
    code = '''
check: function integer (a: integer, b: integer) = {
    x: integer = 0;

    if (a != 0 && (b / a) > 0) {
        x = 1;
    }

    if (a == 0 || (b / a) > 0) {
        x = 2;
    }

    return x;
}
'''
    return test_code("Short-circuit lógico (&& / ||)", code)

def test23_func_calls():
    code = '''
inc: function integer (x: integer) = {
    return x + 1;
}

sum2: function integer (a: integer, b: integer) = {
    return a + b;
}

main: function integer () = {
    t: integer = 0;
    t = inc(5);
    t = sum2(t, 10);
    return t;
}
'''
    return test_code("Llamadas a funcion (directas y con retorno)", code)

def test24_print_int_bool():
    code = '''
main: function integer () = {
    x: integer = 42;
    t: boolean = true;

    print x;      # 42
    print t;      # 1

    return 0;
}
'''
    code = code.replace('#', '//') 
    return test_code("print: integer y boolean", code)


def test25_print_char_string():
    code = '''
main: function integer () = {
    c: char = 'A';
    print c;          // A

    print "hello";    // hello

    return 0;
}
'''
    return test_code("print: char y string", code)

def test26_for_in_range_sum():
    code = '''
sum_range: function integer (a: integer, b: integer) = {
    s: integer = 0;
    i: integer = 0;
    i = a;

    # azúcar: for i in range(a, b) { s = s + i; }
    # si ya desazucaras en parser, solo escribe ese for; si no, usa ForStmt C-like.

    for (i = a; i < b; i = i + 1) {
        s = s + i;
    }

    return s;
}
'''
    code = code.replace('#', '//')  # si tu lexer no soporta '#'
    return test_code("for in range (desazucar a while)", code)


def test27_for_c_like():
    code = '''
main: function integer () = {
    i: integer = 0;
    acc: integer = 0;

    for (i = 1; i <= 4; i = i + 1) {
        acc = acc + i;
    }

    return acc;  // 1+2+3+4 = 10
}
'''
    return test_code("for C-like", code)


def test28_preinc_assign_value():
    code = '''
main: function integer () = {
    x: integer = 1;
    y: integer = ++x;   // x=2, y=2
    return x + y;       // 4
}
'''
    return test_code("++x (pre): actualiza y retorna nuevo", code)

def test29_postdec_assign_value():
    code = '''
main: function integer () = {
    x: integer = 3;
    y: integer = x--;   // y=3, x=2
    return x + y;       // 5
}
'''
    return test_code("x-- (post): actualiza y retorna viejo", code)

def test30_pre_post_mix_no_stmt():
    code = '''
main: function integer () = {
    i: integer = 0;
    tmp1: integer = ++i;   // i=1, tmp1=1
    tmp2: integer = i++;   // tmp2=1, i=2
    return i;              // 2
}
'''
    return test_code("Mezcla pre/post ++ (sin ++i; como stmt)", code)

def test31_array_local_sum():
    code = '''
main: function integer () = {
    a: array[5] integer;
    i: integer = 0;
    sum: integer = 0;

    a[0] = 10;
    a[1] = 20;
    a[2] = 30;

    sum = a[0] + a[1] + a[2];
    return sum;  // 60
}

'''
    code = code.replace('#', '//')
    return test_code("Arreglo local 1D: stores/loads y sumatoria", code)

def test32_array_global_and_index():
    code = '''
a: array[3] integer;

main: function integer () = {
    a[0] = 7;
    a[1] = 8;
    a[2] = 9;

    i: integer = 1;
    x: integer = a[i];
    y: integer = a[i + 1];

    return x + y;  // 17
}

'''
    return test_code("Arreglo global 1D: loads con indice expresion", code)

def test33_print_all_types():
    code = '''
main: function integer () = {
    print "hello";   // hello
    c: char = 'A';
    print c;         // A
    x: integer = 42;
    print x;         // 42
    t: boolean = true;
    print t;         // 1
    return 0;
}
'''
    return test_code("print: string, char, integer y boolean", code)



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
        ("While básico", test20_while_basic),
        ("Short-circuit lógico", test21_short_circuit_logic),
        ("Llamadas a función", test23_func_calls),
        ("print: integer y boolean", test24_print_int_bool),
        ("print: char y string", test25_print_char_string),
        ("++x (pre): actualiza y retorna nuevo", test28_preinc_assign_value),
        ("x-- (post): actualiza y retorna viejo", test29_postdec_assign_value),
        ("Mezcla pre/post ++", test30_pre_post_mix_no_stmt),
        ("Arreglo local 1D", test31_array_local_sum),
        ("Arreglo global 1D", test32_array_global_and_index),
        ("print: todos los tipos", test33_print_all_types),
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