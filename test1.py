'''
Script de prueba del generador de IR usando el parser real
Cobertura de generación: aritmética, comparaciones, if/else, while,
short-circuit, llamadas a función, print, arreglos 1D, ++/-- pre/post,
for i in range (desazucarado), strings y floats (sin print).
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
    print("\n Código B-Minor:")
    print("-" * 70)
    print(code)
    print("-" * 70)
    
    # Reset errors
    reset_errors()
    
    # Parse
    print("\n Parseando...")
    ast = parse_string(code)
    
    if ast is None or errors_detected():
        print(" Error en el parsing")
        return False
    
    print(" Parsing exitoso")
    
    # Semantic check
    print("\n Análisis semántico...")
    env = Check.checker(ast)
    
    if errors_detected():
        print(" Errores en análisis semántico")
        return False
    
    print(" Análisis semántico exitoso")
    
    # Generate IR
    print("\n Generando IR...")
    try:
        module = IRGenerator.generate(ast, env)
        print(" IR generado exitosamente")
        
        print("\n Código LLVM IR:")
        print("-" * 70)
        print(str(module))
        print("-" * 70)
        print()
        return True
    except Exception as e:
        print(f" Error generando IR: {e}")
        import traceback
        traceback.print_exc()
        return False

# =====================================================================
# PRUEBAS
# =====================================================================

def test01_vars_arith_unary():
    code = '''
main: function integer () = {
    a: integer = 10;
    b: integer = 3;
    c: integer = a * b - (a / b) + (-b);   // 10*3 - 10/3 + (-3) = 30 - 3 + (-3) = 24
    return c;
}
'''
    return test_code("Aritmética + unario (-) + asignación", code)

def test02_if_else_nested_medium():
    code = '''
main: function integer () = {
    x: integer = 7;
    y: integer = 10;
    r: integer = 0;

    if (x < y) {
        if (x * 2 == y -  (x - 4)) {
            r = 1;
        } else {
            r = 2;
        }
    } else {
        r = 3;
    }

    return r;
}
'''
    return test_code("If/else anidado + comparaciones", code)

def test03_while_sum_evens():
    code = '''
main: function integer () = {
    n: integer = 8;
    i: integer = 1;
    acc: integer = 0;

    while (i <= n) {
        if ((i % 2) == 0) {
            acc = acc + i;   // suma pares hasta 8: 2+4+6+8 = 20
        }
        i = i + 1;
    }
    return acc;
}
'''
    return test_code("While + % + if interno", code)

def test04_short_circuit_guard_div():
    code = '''
main: function integer () = {
    a: integer = 0;
    b: integer = 5;
    x: integer = 0;

    if (a == 0 || (b / a) > 0) {
        x = x + 1;  // debe entrar por el primer término del OR sin dividir
    }

    if (a != 0 && (b / a) > 0) {
        x = x + 10; // no debe ejecutarse el segundo término del AND
    }

    return x;   // 1
}
'''
    return test_code("Short-circuit (|| y &&) evitando división", code)

def test05_func_calls_and_return():
    code = '''
inc: function integer (x: integer) = {
    return x + 1;
}

mix: function integer (p: integer, q: integer) = {
    if (p > q) { return p - q; }
    else { return q - p; }
}

main: function integer () = {
    t: integer = 10;
    t = inc(t);             // 11
    t = mix(t, 7);          // 4
    return t;               // 4
}
'''
    return test_code("Llamadas a función + retorno", code)

def test06_print_all_supported():
    code = '''
main: function integer () = {
    print "B-Minor OK";   // string
    c: char = 'Z';
    print c;              // char
    x: integer = 42;
    print x;              // int
    t: boolean = (x > 0);
    print t;              // bool -> 1
    return 0;
}
'''
    return test_code("print: string, char, integer, boolean", code)

def test07_inc_dec_pre_post_mix():
    code = '''
main: function integer () = {
    i: integer = 2;
    a: integer = ++i;   // i=3, a=3
    b: integer = i++;   // b=3, i=4
    c: integer = --i;   // i=3, c=3
    d: integer = i--;   // d=3, i=2
    return a + b + c + d + i; // 3+3+3+3+2 = 14
}
'''
    return test_code("++/-- pre y post, mezcla con asignaciones", code)

def test08_array_local_expr_index():
    code = '''
main: function integer () = {
    a: array[5] integer;
    i: integer = 0;
    sum: integer = 0;

    a[0] = 5;
    a[1] = 7;
    a[2] = 9;

    i = 1;
    sum = a[0] + a[i] + a[i + 1]; // 5 + 7 + 9 = 21

    return sum;
}
'''
    return test_code("Arreglo local 1D: stores/loads + índice expresión", code)

def test09_array_global_expr_index():
    code = '''
a: array[4] integer;

main: function integer () = {
    a[0] = 2;
    a[1] = 4;
    a[2] = 6;
    a[3] = 8;

    i: integer = 2;
    x: integer = a[i];      // 6
    y: integer = a[i - 1];  // 4

    return x + y;           // 10
}
'''
    return test_code("Arreglo global 1D: loads con índice expresión", code)

def test10_for_in_range_desugar():
    code = '''
main: function integer () = {
    sum: integer = 0;
    for i in range(1, 6) {
        sum = sum + i;   // 1+2+3+4+5 = 15
    }
    return sum;
}
'''
    return test_code("for i in range(a,b) desazucarado a while", code)

def test11_comparisons_combo():
    code = '''
main: function integer () = {
    a: integer = 5;
    b: integer = 5;
    c: integer = 7;
    r: integer = 0;

    if (a == b && c != b && c >= a && a <= b) {
        r = 10;
    }
    return r; // 10
}
'''
    return test_code("Comparaciones combinadas (==, !=, >=, <=) + &&", code)

def test12_floats_ops_only():
    code = '''
main: function integer () = {
    // No imprimimos float (solo cálculo y decisión)
    a: float = 2.0;
    b: float = 3.0;
    // Si a*b > 5.0 entonces 1, si no 0
    r: integer = 0;
    if ( (a * b) > 5.0 ) {
        r = 1;
    }
    return r; // 1
}
'''
    return test_code("Float: operaciones y comparación (sin print)", code)

# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print(" PRUEBAS DEL GENERADOR DE IR (COBERTURA MEDIA)")
    print("=" * 70 + "\n")
    
    tests = [
        ("Aritmética + unario", test01_vars_arith_unary),
        ("If/else anidado", test02_if_else_nested_medium),
        ("While + % + if", test03_while_sum_evens),
        ("Short-circuit (|| y &&)", test04_short_circuit_guard_div),
        ("Llamadas a función", test05_func_calls_and_return),
        ("print: string/char/int/bool", test06_print_all_supported),
        ("++/-- pre y post", test07_inc_dec_pre_post_mix),
        ("Arreglo local 1D", test08_array_local_expr_index),
        ("Arreglo global 1D", test09_array_global_expr_index),
        ("for in range desazucarado", test10_for_in_range_desugar),
        ("Comparaciones combinadas", test11_comparisons_combo),
        ("Float (sin print)", test12_floats_ops_only),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f" Excepción en {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        
        print("\n" + "=" * 70 + "\n")
    
    print("\n" + "=" * 70)
    print(" RESUMEN FINAL")
    print("=" * 70)
    print(f"Total: {passed} Exitoso  / {failed} Fallos ")
    print("=" * 70 + "\n")
