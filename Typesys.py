# typesys.py
'''
Sistema de tipos
================
Este archivo implementa las características básicas del sistema de tipos. Existe
mucha flexibilidad, pero la mejor estrategia podría ser no darle demasiadas
vueltas al problema. Al menos no al principio. Estos son los requisitos
básicos mínimos:

1. Los tipos tienen identidad (p. ej., al menos un nombre como 'integer', 'float', 'char', 'string').
2. Los tipos deben ser comparables (p. ej., integer != float).
3. Los tipos admiten diferentes operadores (p. ej., +, -, *, /, etc.).
Una forma de lograr todos estos objetivos es comenzar con algún tipo de
enfoque basado en tablas. No es lo más sofisticado, pero funcionará
como punto de partida. Puede volver a refactorizar el sistema de tipos
más adelante.
'''

class CheckError(Exception):
	pass
	
	
typenames = { 'integer', 'float', 'char', 'boolean', 'string', 'void' }

# Capabilities
_bin_ops = {
	# Integer operations
	('integer', '+', 'integer') : 'integer',
	('integer', '-', 'integer') : 'integer',
	('integer', '*', 'integer') : 'integer',
	('integer', '/', 'integer') : 'integer',
	('integer', '%', 'integer') : 'integer',

	('integer', '=', 'integer') : 'integer',

	('integer', '<', 'integer')  : 'boolean',
	('integer', '<=', 'integer') : 'boolean',
	('integer', '>', 'integer')  : 'boolean',
	('integer', '>=', 'integer') : 'boolean',
	('integer', '==', 'integer') : 'boolean',
	('integer', '!=', 'integer') : 'boolean',

	# Float operations
	('float', '+', 'float') : 'float',
	('float', '-', 'float') : 'float',
	('float', '*', 'float') : 'float',
	('float', '/', 'float') : 'float',

	('float', '=', 'float') : 'float',

	('float', '<', 'float')  : 'boolean',
	('float', '<=', 'float') : 'boolean',
	('float', '>', 'float')  : 'boolean',
	('float', '>=', 'float') : 'boolean',
	('float', '==', 'float') : 'boolean',
	('float', '!=', 'float') : 'boolean',

	# Bools
	('boolean', '&&', 'boolean') : 'boolean',
	('boolean', '||', 'boolean') : 'boolean',
	('boolean', '==', 'boolean') : 'boolean',
	('boolean', '!=', 'boolean') : 'boolean',

	# Char
	('char', '=', 'char')  : 'char',

	('char', '<', 'char')  : 'boolean',
	('char', '<=', 'char') : 'boolean',
	('char', '>', 'char')  : 'boolean',
	('char', '>=', 'char') : 'boolean',
	('char', '==', 'char') : 'boolean',
	('char', '!=', 'char') : 'boolean',

	# Strings
	('string', '+', 'string')  : 'string',		# Concatenar

	('string', '=', 'string')  : 'string',

	('string', '<', 'string')  : 'boolean',
	('string', '<=', 'string') : 'boolean',
	('string', '>', 'string')  : 'boolean',
	('string', '>=', 'string') : 'boolean',
	('string', '==', 'string') : 'boolean',
	('string', '!=', 'string') : 'boolean',
}

_unary_ops = {
	('+', 'integer') : 'integer',
	('-', 'integer') : 'integer',
	('^', 'integer') : 'integer',
	('++', 'integer') : 'integer',
	('--', 'integer') : 'integer',

	('+', 'float') : 'float',
	('-', 'float') : 'float',
	('++', 'float') : 'float',
	('--', 'float') : 'float',

	('!', 'boolean') : 'boolean',
}

# Check if a binary operator is supported. Returns the
# result type or None (if not supported). Type checker
# uses this function.

def loockup_type(name):
	'''
	Dado el nombre de un tipo primitivo, se busca el objeto "type" apropiado.
	Para empezar, los tipos son solo nombres, pero mas adelante pueden ser
	objetos mas avanzados.
	'''
	if name in typenames:
		return name
	else:
		return None
		
def check_binop(op, left_type, right_type):
	return _bin_ops.get((left_type, op, right_type))

def check_unaryop(op, operand_type):
	return _unary_ops.get((op, operand_type))

def is_array_type(type_name):
	'''
	Check if a type is an array type
	'''
	return isinstance(type_name, str) and type_name.startswith('array[')

def get_array_element_type(array_type):
	'''
	Extract the element type from an array type string
	'''
	if is_array_type(array_type):
		# Extract element type from "array[size]element_type"
		bracket_end = array_type.find(']')
		if bracket_end != -1:
			return array_type[bracket_end + 1:]
	return None

def is_compatible_type(type1, type2):
	'''
	Check if two types are compatible for assignment
	'''
	# Exact type match required
	return type1 == type2

