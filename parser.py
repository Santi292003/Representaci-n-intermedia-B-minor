#!/usr/bin/env python3
"""
Parser para el lenguaje BMinor
Implementa un analizador sintáctico usando SLY (Sly Lex Yacc)
CORREGIDO: Soporta funciones sin parámetros y literales float
"""

import sys
from sly import Lexer, Parser
from model import *
from errors import error, errors_detected

# =====================================================================
# LEXER
# =====================================================================

class BMinorLexer(Lexer):
    # Tokens
    tokens = {
        # Identificadores y literales
        'ID', 'INTEGER', 'FLOAT', 'CHAR', 'STRING', 'BOOLEAN',
        
        # Palabras reservadas
        'IF', 'ELSE', 'WHILE', 'DO', 'FOR', 'RETURN', 'PRINT',
        'FUNCTION', 'INTEGER_TYPE', 'BOOLEAN_TYPE', 'FLOAT_TYPE', 'CHAR_TYPE', 'STRING_TYPE', 'VOID',
        'TRUE', 'FALSE', 'ARRAY',
        
        # Operadores aritméticos
        'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
        
        # Operadores de comparación
        'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
        
        # Operadores lógicos
        'AND', 'OR', 'NOT',
        
        # Operadores de asignación
        'ASSIGN',
        
        # Operadores de incremento/decremento
        'INCREMENT', 'DECREMENT',
        
        # Símbolos especiales
        'SEMICOLON', 'COMMA', 'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
        'LBRACKET', 'RBRACKET', 'COLON', 'ARROW',
    }
    
    # Palabras reservadas
    keywords = {
        'if': 'IF', 'else': 'ELSE', 'while': 'WHILE', 'do': 'DO', 'for': 'FOR', 
        'return': 'RETURN', 'print': 'PRINT', 'function': 'FUNCTION', 
        'integer': 'INTEGER_TYPE', 'boolean': 'BOOLEAN_TYPE', 'float': 'FLOAT_TYPE', 
        'char': 'CHAR_TYPE', 'string': 'STRING_TYPE', 'void': 'VOID',
        'true': 'TRUE', 'false': 'FALSE', 'array': 'ARRAY'
    }
    
    # Ignorar espacios en blanco y comentarios
    ignore = ' \t\r\n'
    ignore_comment_line = r'//.*'
    ignore_comment_block = r'/\*.*?\*/'
    
    # Definiciones de tokens (orden importa - operadores más largos primero)
    INCREMENT = r'\+\+'
    DECREMENT = r'--'
    
    EQ = r'=='
    NE = r'!='
    LE = r'<='
    GE = r'>='
    
    AND = r'&&'
    OR = r'\|\|'
    
    PLUS = r'\+'
    MINUS = r'-'
    MULTIPLY = r'\*'
    DIVIDE = r'/'
    MODULO = r'%'
    
    NOT = r'!'
    LT = r'<'
    GT = r'>'
    
    ASSIGN = r'='
    
    SEMICOLON = r';'
    COMMA = r','
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'
    LBRACKET = r'\['
    RBRACKET = r'\]'
    COLON = r':'
    ARROW = r'=>'
    
    # Literales - IMPORTANTE: FLOAT debe ir ANTES de INTEGER
    # Si no, "2.0" se reconoce como INTEGER "2" y falla en "."
    @_(r'\d+\.\d+')
    def FLOAT(self, t):
        t.value = float(t.value)
        return t
    
    @_(r'\d+')
    def INTEGER(self, t):
        t.value = int(t.value)
        return t
    
    CHAR = r"'([^'\\]|\\.)'"
    STRING = r'"([^"\\]|\\.)*"'
    
    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        # Check if it's a keyword
        if t.value in self.keywords:
            t.type = self.keywords[t.value]
        return t
    
    def CHAR(self, t):
        # Remover las comillas y procesar escapes
        char_value = t.value[1:-1]
        if char_value == '\\n':
            t.value = '\n'
        elif char_value == '\\t':
            t.value = '\t'
        elif char_value == '\\r':
            t.value = '\r'
        elif char_value == '\\\\':
            t.value = '\\'
        elif char_value == "\\'":
            t.value = "'"
        elif char_value == '\\"':
            t.value = '"'
        else:
            t.value = char_value
        return t
    
    def STRING(self, t):
        # Remover las comillas y procesar escapes
        string_value = t.value[1:-1]
        # Procesar escapes básicos
        string_value = string_value.replace('\\n', '\n')
        string_value = string_value.replace('\\t', '\t')
        string_value = string_value.replace('\\r', '\r')
        string_value = string_value.replace('\\\\', '\\')
        string_value = string_value.replace('\\"', '"')
        t.value = string_value
        return t
    
    def error(self, t):
        error(f"Carácter ilegal '{t.value[0]}'", t.lineno)
        self.index += 1

# =====================================================================
# PARSER
# =====================================================================

class BMinorParser(Parser):
    tokens = BMinorLexer.tokens
    
    # Precedencia de operadores
    precedence = (
        ('right', 'ASSIGN'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NE'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE', 'MODULO'),
        ('right', 'NOT', 'INCREMENT', 'DECREMENT'),
        ('left', 'LPAREN', 'LBRACKET'),
    )
    
    def __init__(self):
        self.lexer = BMinorLexer()
    
    # =====================================================================
    # Programa principal
    # =====================================================================
    
    @_('declarations')
    def program(self, p):
        return Program(p.declarations)
    
    @_('declarations declaration')
    def declarations(self, p):
        return p.declarations + [p.declaration]
    
    @_('declaration')
    def declarations(self, p):
        return [p.declaration]
    
    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    @_('var_decl',
       'array_decl',
       'func_decl',
       'while_stmt',
       'do_while_stmt',
       'if_stmt',
       'for_stmt',
       'return_stmt',
       'print_stmt',
       'assignment')
    def declaration(self, p):
        return p[0]
    
    @_('ID COLON type SEMICOLON')
    def var_decl(self, p):
        return VarDecl(p.ID, p.type)
    
    @_('ID COLON type ASSIGN expr SEMICOLON')
    def var_decl(self, p):
        return VarDecl(p.ID, p.type, p.expr)
    
    @_('ID COLON array_type SEMICOLON')
    def array_decl(self, p):
        return ArrayDecl(p.ID, p.array_type[0], p.array_type[1])
    
    @_('ID COLON array_type ASSIGN LBRACE expr_list RBRACE SEMICOLON')
    def array_decl(self, p):
        return ArrayDecl(p.ID, p.array_type[0], p.array_type[1], p.expr_list)
    
    @_('ID COLON FUNCTION type LPAREN param_list RPAREN ASSIGN LBRACE stmt_list RBRACE')
    def func_decl(self, p):
        return FuncDecl(p.ID, p.type, p.param_list, p.stmt_list)
    
    # =====================================================================
    # Tipos
    # =====================================================================
    
    @_('INTEGER_TYPE',
       'BOOLEAN_TYPE',
       'FLOAT_TYPE',
       'CHAR_TYPE',
       'STRING_TYPE',
       'VOID')
    def type(self, p):
        return p[0]
    
    @_('ARRAY LBRACKET dimensions RBRACKET type')
    def array_type(self, p):
        return (p.type, p.dimensions)
    
    @_('dimensions LBRACKET expr RBRACKET')
    def dimensions(self, p):
        return p.dimensions + [p.expr]
    
    @_('LBRACKET expr RBRACKET')
    def dimensions(self, p):
        return [p.expr]
    
    # =====================================================================
    # Lista de parámetros - CORREGIDO: ahora acepta lista vacía
    # =====================================================================
    
    @_('param_list COMMA param')
    def param_list(self, p):
        return p.param_list + [p.param]
    
    @_('param')
    def param_list(self, p):
        return [p.param]
    
    @_('')  # <--- NUEVO: Lista vacía de parámetros
    def param_list(self, p):
        return []
    
    @_('ID COLON type')
    def param(self, p):
        return VarParm(p.ID, p.type)
    
    @_('ID COLON array_type')
    def param(self, p):
        return ArrayParm(p.ID, p.array_type[0], p.array_type[1])
    
    # =====================================================================
    # Lista de declaraciones
    # =====================================================================
    
    @_('stmt_list stmt')
    def stmt_list(self, p):
        return p.stmt_list + [p.stmt]
    
    @_('stmt')
    def stmt_list(self, p):
        return [p.stmt]
    
    # =====================================================================
    # Declaraciones
    # =====================================================================
    
    @_('var_decl',
       'array_decl',
       'if_stmt',
       'while_stmt',
       'do_while_stmt',
       'for_stmt',
       'return_stmt',
       'print_stmt',
       'assignment',
       'block')
    def stmt(self, p):
        return p[0]
    
    @_('LBRACE stmt_list RBRACE')
    def block(self, p):
        return p.stmt_list
    
    @_('IF LPAREN expr RPAREN stmt ELSE stmt')
    def if_stmt(self, p):
        return IfStmt(p.expr, p.stmt0, p.stmt1)
    
    @_('IF LPAREN expr RPAREN stmt')
    def if_stmt(self, p):
        return IfStmt(p.expr, p.stmt)
    
    @_('WHILE LPAREN expr RPAREN stmt')
    def while_stmt(self, p):
        return WhileStmt(p.expr, p.stmt)
    
    @_('DO stmt WHILE LPAREN expr RPAREN SEMICOLON')
    def do_while_stmt(self, p):
        return DoWhileStmt(p.stmt, p.expr)
    
    @_('FOR LPAREN stmt expr SEMICOLON stmt RPAREN stmt')
    def for_stmt(self, p):
        return ForStmt(p.stmt0, p.expr, p.stmt1, p.stmt2)
    
    @_('RETURN expr SEMICOLON')
    def return_stmt(self, p):
        return ReturnStmt(p.expr)
    
    @_('RETURN SEMICOLON')
    def return_stmt(self, p):
        return ReturnStmt()
    
    @_('PRINT expr SEMICOLON')
    def print_stmt(self, p):
        return PrintStmt(p.expr)
    
    @_('location ASSIGN expr SEMICOLON')
    def assignment(self, p):
        return Assignment(p.location, p.expr)
    
    # =====================================================================
    # Expresiones
    # =====================================================================
    
    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr MULTIPLY expr',
       'expr DIVIDE expr',
       'expr MODULO expr')
    def expr(self, p):
        return BinOper(p[1], p.expr0, p.expr1)
    
    @_('expr EQ expr',
       'expr NE expr',
       'expr LT expr',
       'expr LE expr',
       'expr GT expr',
       'expr GE expr')
    def expr(self, p):
        return BinOper(p[1], p.expr0, p.expr1)
    
    @_('expr AND expr',
       'expr OR expr')
    def expr(self, p):
        return BinOper(p[1], p.expr0, p.expr1)
    
    @_('NOT expr',
       'MINUS expr')
    def expr(self, p):
        return UnaryOper(p[0], p.expr)
    
    # Operadores de incremento/decremento prefijos
    @_('INCREMENT expr')
    def expr(self, p):
        return PreInc(p.expr)
    
    @_('DECREMENT expr')
    def expr(self, p):
        return PreDec(p.expr)
    
    # Operadores de incremento/decremento postfijos
    @_('expr INCREMENT')
    def expr(self, p):
        return PostInc(p.expr)
    
    @_('expr DECREMENT')
    def expr(self, p):
        return PostDec(p.expr)
    
    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr
    
    @_('literal',
       'location',
       'func_call')
    def expr(self, p):
        return p[0]
    
    # =====================================================================
    # Literales
    # =====================================================================
    
    @_('INTEGER')
    def literal(self, p):
        return Integer(p.INTEGER)
    
    @_('FLOAT')
    def literal(self, p):
        return Float(p.FLOAT)
    
    @_('CHAR')
    def literal(self, p):
        return Char(p.CHAR)
    
    @_('STRING')
    def literal(self, p):
        return String(p.STRING)
    
    @_('TRUE')
    def literal(self, p):
        return Boolean(True)
    
    @_('FALSE')
    def literal(self, p):
        return Boolean(False)
    
    # =====================================================================
    # Ubicaciones
    # =====================================================================
    
    @_('ID')
    def location(self, p):
        return VarLoc(p.ID)
    
    @_('ID LBRACKET expr_list RBRACKET')
    def location(self, p):
        return ArrayLoc(p.ID, p.expr_list)
    
    # =====================================================================
    # Llamadas de función
    # =====================================================================
    
    @_('ID LPAREN RPAREN')
    def func_call(self, p):
        return FuncCall(p.ID)
    
    @_('ID LPAREN expr_list RPAREN')
    def func_call(self, p):
        return FuncCall(p.ID, p.expr_list)
    
    # =====================================================================
    # Lista de expresiones
    # =====================================================================
    
    @_('expr_list COMMA expr')
    def expr_list(self, p):
        return p.expr_list + [p.expr]
    
    @_('expr')
    def expr_list(self, p):
        return [p.expr]
    
    # =====================================================================
    # Manejo de errores
    # =====================================================================
    
    def error(self, p):
        if p:
            error(f"Error de sintaxis en '{p.value}'", p.lineno)
        else:
            error("Error de sintaxis: final inesperado de entrada")

# =====================================================================
# Función principal
# =====================================================================

def parse_file(filename):
    """Parse a BMinor file and return the AST"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        return parse_string(source)
    except FileNotFoundError:
        error(f"Archivo no encontrado: {filename}")
        return None
    except Exception as e:
        error(f"Error al leer archivo: {e}")
        return None

def parse_string(source):
    """Parse a BMinor source string and return the AST"""
    lexer = BMinorLexer()
    parser = BMinorParser()
    
    try:
        ast = parser.parse(lexer.tokenize(source))
        return ast
    except Exception as e:
        error(f"Error de parsing: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parser.py <archivo.bminor>")
        sys.exit(1)
    
    filename = sys.argv[1]
    ast = parse_file(filename)
    
    if ast and not errors_detected():
        print("Parsing exitoso!")
        print("\nAST generado:")
        from rich.console import Console
        console = Console()
        console.print(ast.pretty())
    else:
        print("Errores encontrados durante el parsing.")
        sys.exit(1)