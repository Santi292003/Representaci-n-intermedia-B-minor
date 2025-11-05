# 🧠 Compilador B-Minor (con LLVM IR y SLY)

Proyecto académico de compiladores que implementa el lenguaje **B-Minor**, un lenguaje educativo con tipado estático y soporte de estructuras comunes de programación.  
El compilador realiza **análisis léxico, sintáctico, semántico** y genera **código intermedio LLVM IR** utilizando **llvmlite**.

---

## 🚀 Características implementadas

### ✅ Léxico y Sintaxis
- Basado en **SLY** (Python Lex-Yacc)
- Soporte de:
  - Variables (`int`, `float`, `boolean`, `char`, `string`)
  - Operadores aritméticos, relacionales y lógicos
  - Estructuras de control: `if`, `else`, `while`, `do while`, `for`
  - `for i in range(a, b)` desazucarado a `while`
  - Incremento y decremento (`++`, `--`, pre y post)
  - Funciones con parámetros y retorno
  - `print` usando `printf`
  - Arreglos 1D (globales y locales)
  - Strings como constantes globales (`[N x i8]`)
  - Literales `true`/`false`, caracteres y cadenas
  - Comentarios `//` y `/* ... */`

---

## ⚙️ Etapas del compilador

| Etapa | Archivo | Descripción |
|-------|----------|-------------|
| **Léxico / Sintaxis** | `parser.py` | Define tokens, gramática y generación del AST usando SLY |
| **Modelo del AST** | `model.py` | Clases para representar nodos del árbol sintáctico |
| **Tabla de símbolos** | `Symtab.py` | Manejo de entornos y alcances |
| **Chequeo semántico** | `checker.py` | Verificación de tipos, ámbitos, y compatibilidad |
| **Sistema de tipos** | `Typesys.py` | Reglas de compatibilidad entre tipos y operadores |
| **Generación de código intermedio (IR)** | `irgen.py` | Traducción del AST a LLVM IR (usando `llvmlite`) |
| **Pruebas** | `test_with_parser.py` | Ejecuta casos de prueba de cada característica |

---

## 🧩 Estructura de carpetas

📦 Representacion_intermedia/
┣ 📜 parser.py
┣ 📜 checker.py
┣ 📜 irgen.py
┣ 📜 model.py
┣ 📜 Symtab.py
┣ 📜 Typesys.py
┣ 📜 errors.py
┣ 📜 test_with_parser.py
┗ 📜 README.md


---

## 🧰 Requisitos

- Python 3.10 o superior  
- Paquetes:
  ```bash
  pip install sly llvmlite rich



📜 Licencia

Este proyecto se distribuye bajo la licencia MIT.
Eres libre de usarlo y modificarlo con fines académicos o de investigación.