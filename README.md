# Analizador Semántico para el Lenguaje bminor

Este proyecto implementa un analizador semántico completo para el lenguaje de programación bminor. El analizador valida la corrección de tipos, el uso de variables y funciones, y otras reglas semánticas del lenguaje.

## Estructura del Proyecto

### Archivos Principales

- **`model.py`**: Define las clases AST (Abstract Syntax Tree) para todos los nodos del lenguaje bminor
- **`Checker.py`**: Implementa el analizador semántico usando el patrón Visitor
- **`Symtab.py`**: Implementa la tabla de símbolos para manejo de scope y declaraciones
- **`Typesys.py`**: Define el sistema de tipos y operaciones permitidas
- **`errors.py`**: Sistema de manejo de errores

### Archivos de Prueba

- **`simple_test.py`**: Pruebas básicas del analizador (2 casos de prueba)
- **`comprehensive_test.py`**: Suite completa de pruebas (7 casos de prueba)
- **`test_runner.py`**: Ejecutor de pruebas con salida formateada (requiere rich)
- **`run_individual_tests.py`**: Ejecutor de pruebas individuales numeradas
- **`test_bad0.py`**: Prueba específica para el archivo bad0.bminor
- **`test_bminor_file.py`**: Probador genérico para archivos .bminor específicos

### Directorio de Pruebas

- **`typechecker/`**: Contiene archivos de prueba `.bminor`
  - `good*.bminor`: Programas semánticamente correctos
  - `bad*.bminor`: Programas con errores semánticos

## Características Implementadas

### Tipos de Datos Soportados

- `integer`: Números enteros
- `float`: Números de punto flotante
- `boolean`: Valores booleanos (true/false)
- `char`: Caracteres individuales
- `string`: Cadenas de texto
- `void`: Tipo para funciones sin retorno
- `array[n]type`: Arrays de tamaño fijo

### Validaciones Semánticas

1. **Verificación de Tipos**
   - Compatibilidad en asignaciones
   - Tipos correctos en operaciones binarias y unarias
   - Tipos de retorno de funciones

2. **Manejo de Variables**
   - Variables declaradas antes de uso
   - No redeclaración de variables en el mismo scope
   - Tipos consistentes en declaraciones

3. **Validación de Funciones**
   - Número correcto de argumentos en llamadas
   - Tipos correctos de argumentos
   - Funciones declaradas antes de uso
   - Tipos de retorno consistentes

4. **Operaciones Soportadas**
   - Aritméticas: `+`, `-`, `*`, `/`, `%`
   - Comparación: `<`, `<=`, `>`, `>=`, `==`, `!=`
   - Lógicas: `&&`, `||`, `!`
   - Unarias: `+`, `-`, `++`, `--`, `^`

## Uso del Analizador

### Ejemplo Básico

```python
from model import *
from Checker import Check
from errors import error_count, reset_errors

# Crear un programa AST
program = Program([
    VarDecl('x', 'integer', IntegerLit(42)),
    VarDecl('y', 'float', FloatLit(3.14))
])

# Ejecutar el analizador semántico
reset_errors()
env = Check.checker(program)

# Verificar errores
if error_count() == 0:
    print("Programa semánticamente correcto")
else:
    print(f"Se encontraron {error_count()} errores")
```

### Ejecutar Pruebas

#### Suites Completas de Pruebas

```bash
# Pruebas básicas (2 casos)
python3 simple_test.py

# Pruebas comprehensivas (7 casos)
python3 comprehensive_test.py

# Pruebas con formato avanzado (requiere pip install rich)
python3 test_runner.py
```

#### Pruebas Individuales Numeradas

```bash
# Ver menú de pruebas disponibles
python3 run_individual_tests.py

# Ejecutar una prueba específica (1-7)
python3 run_individual_tests.py 1    # Variables correctas
python3 run_individual_tests.py 2    # Variables incorrectas
python3 run_individual_tests.py 3    # Funciones correctas
python3 run_individual_tests.py 4    # Funciones incorrectas
python3 run_individual_tests.py 5    # Expresiones correctas
python3 run_individual_tests.py 6    # Expresiones incorrectas
python3 run_individual_tests.py 7    # Variables no definidas

# Ejecutar todas las pruebas individuales
python3 run_individual_tests.py all
```

#### Pruebas de Archivos .bminor Específicos

```bash
# Ver archivos disponibles
python3 test_bminor_file.py

# Probar archivos específicos del directorio typechecker/
python3 test_bminor_file.py bad0     # Probar bad0.bminor
python3 test_bminor_file.py bad1     # Probar bad1.bminor
python3 test_bminor_file.py good0    # Probar good0.bminor
python3 test_bminor_file.py good1    # Probar good1.bminor

# Prueba específica solo para bad0.bminor
python3 test_bad0.py
```

## Ejemplos de Salida de Pruebas

### Ejemplo: Prueba Exitosa (good0.bminor)

```bash
$ python3 test_bminor_file.py good0
=== Probando good0.bminor ===
Archivo: typechecker/good0.bminor
Resultado esperado: PASAR

Programa creado con 6 declaraciones

Ejecutando analizador semántico...

=== RESULTADOS ===
Errores detectados: 0
✓ CORRECTO - No se detectaron errores (como se esperaba)

🎉 Prueba de good0.bminor completada exitosamente
```

### Ejemplo: Prueba con Errores (bad0.bminor)

```bash
$ python3 test_bminor_file.py bad0
=== Probando bad0.bminor ===
Archivo: typechecker/bad0.bminor
Resultado esperado: FALLAR

Programa creado con 6 declaraciones

Ejecutando analizador semántico...

=== RESULTADOS ===
Errores detectados: 6
✓ CORRECTO - Se detectaron errores (como se esperaba)

🎉 Prueba de bad0.bminor completada exitosamente
Error en línea 3: En asignación de 'a', no coincide los tipos: esperado 'integer', obtenido 'float'
Error en línea 4: En asignación de 'b', no coincide los tipos: esperado 'float', obtenido 'integer'
Error en línea 7: En asignación de 'e', no coincide los tipos: esperado 'integer', obtenido 'string'
...
```

### Ejemplo: Suite Completa

```bash
$ python3 comprehensive_test.py
=== Analizador Semántico - Pruebas Comprehensivas ===

Running test: Variables válidas
  ✓ PASS - No errors detected

Running test: Variables con tipos incorrectos
  ✓ PASS - 4 errors detected as expected

Running test: Funciones válidas
  ✓ PASS - No errors detected

...

=== Resultado Final ===
Pruebas pasadas: 7/7
🎉 ¡Todas las pruebas pasaron! El analizador semántico está funcionando correctamente.
```

## Casos de Uso Específicos

### Para Desarrollo y Debugging

```bash
# Probar un caso específico mientras desarrollas
python3 run_individual_tests.py 2

# Probar solo los casos que fallan
python3 test_bminor_file.py bad0
python3 test_bminor_file.py bad1

# Verificar que los casos buenos siguen funcionando
python3 test_bminor_file.py good0
python3 test_bminor_file.py good1
```

### Para Validación Completa

```bash
# Ejecutar todas las pruebas disponibles
python3 comprehensive_test.py
python3 run_individual_tests.py all

# Verificar archivos específicos del directorio typechecker/
for file in bad0 bad1 good0 good1; do
    python3 test_bminor_file.py $file
done
```

## Ejemplos de Validación

### Programa Correcto

```bminor
a: integer = 42;
b: float = 3.14;
sum: function integer (x: integer, y: integer) = {
    return x + y;
}
result: integer = sum(a, 10);
```

### Programa con Errores

```bminor
a: integer = 3.14;        // Error: tipo incorrecto
b: float = undefined_var; // Error: variable no definida
sum: function integer (x: integer) = {
    return "hello";       // Error: tipo de retorno incorrecto
}
result: integer = sum();  // Error: argumentos faltantes
```

## Arquitectura

### Patrón Visitor

El analizador usa el patrón Visitor para recorrer el AST:

- Cada nodo AST tiene un método `accept(visitor, env)`
- El visitor (`Check`) tiene métodos `visit_NodeType` para cada tipo de nodo
- Se mantiene un entorno (`Symtab`) para el manejo de scope

### Sistema de Tipos

- Verificación estricta de tipos (no hay conversiones implícitas)
- Tabla de operaciones permitidas para cada combinación de tipos
- Soporte para tipos compuestos (arrays, funciones)

### Manejo de Errores

- Recolección de todos los errores (no se detiene en el primero)
- Mensajes de error informativos con números de línea
- Contador global de errores para validación

## Extensiones Futuras

- Soporte para estructuras (structs)
- Inferencia de tipos
- Conversiones de tipo explícitas
- Análisis de flujo de control
- Optimizaciones semánticas

## Dependencias

- Python 3.6+
- rich (opcional, para salida formateada)

## Guía de Ejecución Rápida

### Verificación Inicial

```bash
# Verificar que todo funciona correctamente
python3 comprehensive_test.py
```

### Comandos Más Utilizados

```bash
# Para desarrollo y debugging
python3 run_individual_tests.py        # Ver menú de pruebas
python3 run_individual_tests.py 1      # Probar caso específico
python3 test_bminor_file.py bad0       # Probar archivo específico

# Para validación completa
python3 comprehensive_test.py          # Suite completa (recomendado)
python3 run_individual_tests.py all    # Todas las pruebas individuales
```

### Estructura de Comandos

| Comando | Propósito | Casos de Prueba |
|---------|-----------|-----------------|
| `simple_test.py` | Pruebas básicas | 2 casos básicos |
| `comprehensive_test.py` | **Suite completa** | **7 casos comprehensivos** |
| `run_individual_tests.py N` | Prueba individual | 1 caso específico (N=1-7) |
| `test_bminor_file.py FILE` | Archivo específico | 1 archivo .bminor |
| `test_bad0.py` | Solo bad0.bminor | 1 archivo específico |

### Resolución de Problemas

Si alguna prueba falla:

1. **Ejecutar prueba individual**: `python3 run_individual_tests.py N`
2. **Ver errores específicos**: `python3 test_bminor_file.py badN`
3. **Verificar implementación**: Revisar mensajes de error detallados

## Estado del Proyecto

✅ **Completamente Funcional**: El analizador semántico está implementado y validado

✅ **Todas las Pruebas Pasan**: 7/7 casos de prueba exitosos

✅ **Archivos .bminor Soportados**: bad0, bad1, good0, good1 validados

✅ **Listo para Uso**: Puede validar programas bminor según especificaciones

---

## Referencia Rápida de Comandos

### 🚀 Comandos Principales

```bash
# Verificación completa (RECOMENDADO)
python3 comprehensive_test.py

# Pruebas básicas
python3 simple_test.py

# Ver menú de opciones
python3 run_individual_tests.py
python3 test_bminor_file.py
```

### 🎯 Pruebas Específicas

```bash
# Pruebas individuales (1-7)
python3 run_individual_tests.py 1    # Variables correctas
python3 run_individual_tests.py 2    # Variables incorrectas  
python3 run_individual_tests.py 3    # Funciones correctas
python3 run_individual_tests.py 4    # Funciones incorrectas
python3 run_individual_tests.py 5    # Expresiones correctas
python3 run_individual_tests.py 6    # Expresiones incorrectas
python3 run_individual_tests.py 7    # Variables no definidas

# Archivos .bminor específicos
python3 test_bminor_file.py bad0     # Tipos incorrectos
python3 test_bminor_file.py bad1     # Funciones incorrectas
python3 test_bminor_file.py good0    # Variables válidas
python3 test_bminor_file.py good1    # Funciones válidas

# Prueba específica para bad0
python3 test_bad0.py
```

### 📊 Comandos por Caso de Uso

| **Caso de Uso** | **Comando** | **Descripción** |
|------------------|-------------|-----------------|
| **Verificación inicial** | `python3 comprehensive_test.py` | Ejecutar todas las pruebas |
| **Debugging específico** | `python3 run_individual_tests.py N` | Probar caso individual |
| **Validar archivo** | `python3 test_bminor_file.py FILE` | Probar archivo .bminor |
| **Desarrollo iterativo** | `python3 simple_test.py` | Pruebas rápidas |
| **Ver opciones** | `python3 SCRIPT.py` | Mostrar menú de ayuda |

**¡El analizador semántico está completamente implementado y listo para usar!** 🎉
