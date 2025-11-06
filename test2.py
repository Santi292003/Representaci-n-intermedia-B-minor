'''
Script de prueba del generador de IR usando el parser real
Guarda los resultados de cada prueba en archivos .ll dentro de resultados_ir/
'''

import os
from parser import parse_string
from Checker import Check
from irgen import IRGenerator
from errors import errors_detected, reset_errors

# Crear carpeta de salida si no existe
OUTPUT_DIR = "resultados_ir"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def test_code(description, code, filename_hint=None):
    '''
    Ejecuta una prueba completa (parseo, análisis, IR)
    y guarda el IR en resultados_ir/{nombre}.ll
    '''
    print("=" * 70)
    print(f"PRUEBA: {description}")
    print("=" * 70)
    print("\n📄 Código B-Minor:")
    print("-" * 70)
    print(code)
    print("-" * 70)
    
    reset_errors()

    print("\n🔍 Parseando...")
    ast = parse_string(code)
    if ast is None or errors_detected():
        print(" Error en el parsing")
        return False
    print("✅ Parsing exitoso")

    print("\n🔍 Análisis semántico...")
    env = Check.checker(ast)
    if errors_detected():
        print(" Errores en análisis semántico")
        return False
    print("✅ Análisis semántico exitoso")

    print("\n Generando IR...")
    try:
        module = IRGenerator.generate(ast, env)
        print(" IR generado exitosamente")

        ir_text = str(module)
        print("\n Código LLVM IR:")
        print("-" * 70)
        print(ir_text)
        print("-" * 70)

        # Guardar el IR en archivo
        safe_name = (filename_hint or description).lower().replace(" ", "_").replace("/", "_")
        filename = os.path.join(OUTPUT_DIR, f"{safe_name}.ll")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"; {description}\n\n{ir_text}\n")
        print(f" Guardado en: {filename}\n")

        return True
    except Exception as e:
        print(f" Error generando IR: {e}")
        import traceback
        traceback.print_exc()
        return False

# =====================================================================
# PRUEBAS MEDIAS (una por característica)
# =====================================================================

def test01_vars_arith_unary():
    code = '''
main: function integer () = {
    a: integer = 10;
    b: integer = 3;
    c: integer = a * b - (a / b) + (-b);
    return c;
}
'''
    return test_code("Aritmética + unario (-)", code, "01_aritmetica")

def test02_if_else_nested():
    code = '''
main: function integer () = {
    x: integer = 7;
    y: integer = 10;
    r: integer = 0;
    if (x < y) {
        if (x * 2 == y - (x - 4)) {
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
    return test_code("If/else anidado + comparaciones", code, "02_if_else")

def test03_while_sum_evens():
    code = '''
main: function integer () = {
    n: integer = 8;
    i: integer = 1;
    acc: integer = 0;
    while (i <= n) {
        if ((i % 2) == 0) {
            acc = acc + i;
        }
        i = i + 1;
    }
    return acc;
}
'''
    return test_code("While + if interno", code, "03_while")

def test04_short_circuit():
    code = '''
main: function integer () = {
    a: integer = 0;
    b: integer = 5;
    x: integer = 0;
    if (a == 0 || (b / a) > 0) {
        x = x + 1;
    }
    if (a != 0 && (b / a) > 0) {
        x = x + 10;
    }
    return x;
}
'''
    return test_code("Short-circuit lógico", code, "04_short_circuit")

def test05_func_calls():
    code = '''
inc: function integer (x: integer) = { return x + 1; }
main: function integer () = {
    t: integer = 10;
    t = inc(t);
    return t;
}
'''
    return test_code("Llamadas a función simples", code, "05_func_calls")

def test06_print_all_types():
    code = '''
main: function integer () = {
    print "B-Minor OK";
    c: char = 'Z';
    print c;
    x: integer = 42;
    print x;
    t: boolean = (x > 0);
    print t;
    return 0;
}
'''
    return test_code("print: string/char/int/bool", code, "06_print")

def test07_inc_dec_mix():
    code = '''
main: function integer () = {
    i: integer = 2;
    a: integer = ++i;
    b: integer = i++;
    c: integer = --i;
    d: integer = i--;
    return a + b + c + d + i;
}
'''
    return test_code("++/-- pre y post mix", code, "07_incdec")

def test08_array_local():
    code = '''
main: function integer () = {
    a: array[5] integer;
    i: integer = 0;
    sum: integer = 0;
    a[0] = 5; a[1] = 7; a[2] = 9;
    i = 1;
    sum = a[0] + a[i] + a[i + 1];
    return sum;
}
'''
    return test_code("Arreglo local 1D", code, "08_array_local")

def test09_array_global():
    code = '''
a: array[4] integer;
main: function integer () = {
    a[0] = 2; a[1] = 4; a[2] = 6; a[3] = 8;
    i: integer = 2;
    x: integer = a[i];
    y: integer = a[i - 1];
    return x + y;
}
'''
    return test_code("Arreglo global 1D", code, "09_array_global")

def test10_for_in_range():
    code = '''
main: function integer () = {
    sum: integer = 0;
    for i in range(1, 6) {
        sum = sum + i;
    }
    return sum;
}
'''
    return test_code("for in range desazucarado", code, "10_for_range")

def test11_comparisons():
    code = '''
main: function integer () = {
    a: integer = 5;
    b: integer = 5;
    c: integer = 7;
    r: integer = 0;
    if (a == b && c != b && c >= a && a <= b) {
        r = 10;
    }
    return r;
}
'''
    return test_code("Comparaciones combinadas", code, "11_comparaciones")

def test12_float_ops():
    code = '''
main: function integer () = {
    a: float = 2.0;
    b: float = 3.0;
    r: integer = 0;
    if ((a * b) > 5.0) {
        r = 1;
    }
    return r;
}
'''
    return test_code("Float: operaciones y comparación", code, "12_float")

# =====================================================================
# MAIN
# =====================================================================

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print(" PRUEBAS DEL GENERADOR DE IR (con export a .ll)")
    print("=" * 70 + "\n")
    
    tests = [
        test01_vars_arith_unary,
        test02_if_else_nested,
        test03_while_sum_evens,
        test04_short_circuit,
        test05_func_calls,
        test06_print_all_types,
        test07_inc_dec_mix,
        test08_array_local,
        test09_array_global,
        test10_for_in_range,
        test11_comparisons,
        test12_float_ops
    ]

    passed = 0
    failed = 0

    for t in tests:
        try:
            if t():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f" Excepción: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print("\n" + "=" * 70 + "\n")

    print("\n" + "=" * 70)
    print(" RESUMEN FINAL")
    print("=" * 70)
    print(f"Total: {passed}  / {failed} ")
    print(f"IRs guardados en carpeta: {OUTPUT_DIR}/")
    print("=" * 70 + "\n")
