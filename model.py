# model.py
'''
AST Node classes for the bminor language
Actualizado para compatibilidad con el parser de SLY
'''

class Node:
    '''
    Base class for all AST nodes
    '''
    def __init__(self, lineno=0):
        self.lineno = lineno
    
    def accept(self, visitor, *args, **kwargs):
        '''
        Accept method for visitor pattern
        '''
        method_name = f'visit_{self.__class__.__name__}'
        method = getattr(visitor, method_name, None)
        if method:
            return method(self, *args, **kwargs)
        else:
            # Try generic visit method
            method = getattr(visitor, 'visit', None)
            if method:
                return method(self, *args, **kwargs)
            else:
                raise Exception(f"No visit method for {self.__class__.__name__}")

class Visitor:
    '''
    Base visitor class
    '''
    pass

class Program(Node):
    '''
    Root node of the program
    '''
    def __init__(self, body, lineno=0):
        super().__init__(lineno)
        self.body = body  # List of declarations

class VarDecl(Node):
    '''
    Variable declaration: name: type = value;
    '''
    def __init__(self, name, type, value=None, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.type = type
        self.value = value

class ArrayDecl(Node):
    '''
    Array declaration: name: array [size] type = {...};
    '''
    def __init__(self, name, element_type, dimensions, values=None, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.element_type = element_type
        self.dimensions = dimensions  # Lista de expresiones para cada dimensión
        self.values = values or []
        # Construir el tipo completo
        if isinstance(dimensions, list):
            size_str = ''.join([f'[{d}]' if isinstance(d, int) else '[?]' for d in dimensions])
        else:
            size_str = f'[{dimensions}]'
        self.type = f"array{size_str}{element_type}"

class FuncDecl(Node):
    '''
    Function declaration: name: function return_type (params) = { body }
    '''
    def __init__(self, name, return_type, parms, body, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.type = return_type  # Return type of function
        self.parms = parms       # List of parameters
        # Normalizamos a BlockStmt (acepta lista/nodo/None)
        self.body = ensure_blockstmt(body)

class VarParm(Node):
    '''
    Function parameter: name: type
    '''
    def __init__(self, name, type, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.type = type

class ArrayParm(Node):
    '''
    Array parameter: name: array [size] type
    '''
    def __init__(self, name, element_type, dimensions, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.element_type = element_type
        self.dimensions = dimensions
        # Construir el tipo completo
        if isinstance(dimensions, list):
            size_str = ''.join([f'[{d}]' if isinstance(d, int) else '[?]' for d in dimensions])
        else:
            size_str = f'[{dimensions}]'
        self.type = f"array{size_str}{element_type}"

class ArrayType(Node):
    '''
    Array type: array [size] element_type
    '''
    def __init__(self, size, element_type, lineno=0):
        super().__init__(lineno)
        self.size = size
        self.element_type = element_type
        self.type = f"array[{size}]{element_type}"

class FunctionType(Node):
    '''
    Function type: function return_type (param_types)
    '''
    def __init__(self, return_type, param_types=None, lineno=0):
        super().__init__(lineno)
        self.return_type = return_type
        self.param_types = param_types or []
        self.type = f"function_{return_type}"

# Statements
class ReturnStmt(Node):
    '''
    Return statement: return expr;
    '''
    def __init__(self, expr=None, lineno=0):
        super().__init__(lineno)
        self.expr = expr

class ExprStmt(Node):
    '''
    Expression statement
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr

class AssignStmt(Node):
    '''
    Assignment statement: location = expr;
    '''
    def __init__(self, location, expr, lineno=0):
        super().__init__(lineno)
        self.location = location
        self.expr = expr

# Alias para compatibilidad con el parser
Assignment = AssignStmt

class IfStmt(Node):
    '''
    If statement: if (condition) then_stmt else else_stmt
    '''
    def __init__(self, condition, then_stmt, else_stmt=None, lineno=0):
        super().__init__(lineno)
        self.condition = condition
        # Normalizamos ramas a BlockStmt
        self.then_stmt = ensure_blockstmt(then_stmt)
        self.else_stmt = ensure_blockstmt(else_stmt) if else_stmt is not None else None

class WhileStmt(Node):
    '''
    While statement: while (condition) stmt
    '''
    def __init__(self, condition, stmt, lineno=0):
        super().__init__(lineno)
        self.condition = condition
        # Normalizamos cuerpo a BlockStmt
        self.stmt = ensure_blockstmt(stmt)

class DoWhileStmt(Node):
    '''
    Do-While statement: do stmt while (condition);
    '''
    def __init__(self, stmt, condition, lineno=0):
        super().__init__(lineno)
        # Normalizamos cuerpo a BlockStmt
        self.stmt = ensure_blockstmt(stmt)
        self.condition = condition

class ForStmt(Node):
    '''
    For statement: for (init; condition; update) stmt
    '''
    def __init__(self, init, condition, update, stmt, lineno=0):
        super().__init__(lineno)
        self.init = init
        self.condition = condition
        self.update = update
        # Normalizamos cuerpo a BlockStmt
        self.stmt = ensure_blockstmt(stmt)

class BlockStmt(Node):
    '''
    Block statement: { statements }
    '''
    def __init__(self, statements, lineno=0):
        super().__init__(lineno)
        self.statements = statements

def ensure_blockstmt(x):
    """
    Normaliza x a BlockStmt:
    - BlockStmt -> tal cual
    - list -> BlockStmt(list)
    - None -> BlockStmt([])
    - nodo suelto -> BlockStmt([nodo])
    """
    if isinstance(x, BlockStmt):
        return x
    if isinstance(x, list):
        return BlockStmt(x)
    if x is None:
        return BlockStmt([])
    return BlockStmt([x])

class PrintStmt(Node):
    '''
    Print statement: print expr;
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr

# Expressions
class BinOper(Node):
    '''
    Binary operation: left oper right
    '''
    def __init__(self, oper, left, right, lineno=0):
        super().__init__(lineno)
        self.oper = oper
        self.left = left
        self.right = right
        self.type = None  # Will be set by type checker

class UnaryOper(Node):
    '''
    Unary operation: oper operand
    '''
    def __init__(self, oper, operand, lineno=0):
        super().__init__(lineno)
        self.oper = oper
        self.operand = operand
        self.type = None  # Will be set by type checker

class PreInc(Node):
    '''
    Pre-increment: ++expr
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr
        self.type = None

class PreDec(Node):
    '''
    Pre-decrement: --expr
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr
        self.type = None

class PostInc(Node):
    '''
    Post-increment: expr++
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr
        self.type = None

class PostDec(Node):
    '''
    Post-decrement: expr--
    '''
    def __init__(self, expr, lineno=0):
        super().__init__(lineno)
        self.expr = expr
        self.type = None

class FuncCall(Node):
    '''
    Function call: name(args)
    '''
    def __init__(self, name, args=None, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.args = args or []
        self.type = None  # Will be set by type checker

class VarLoc(Node):
    '''
    Variable location/reference
    '''
    def __init__(self, name, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.type = None  # Will be set by type checker

class ArrayLoc(Node):
    '''
    Array element access: array[index1][index2]...
    '''
    def __init__(self, name, indices, lineno=0):
        super().__init__(lineno)
        self.name = name
        self.indices = indices if isinstance(indices, list) else [indices]
        self.type = None  # Will be set by type checker

class ArrayLiteral(Node):
    '''
    Array literal: {expr1, expr2, ...}
    '''
    def __init__(self, elements, lineno=0):
        super().__init__(lineno)
        self.elements = elements
        self.type = None  # Will be set by type checker

# Literals
class IntegerLit(Node):
    '''
    Integer literal
    '''
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value
        self.type = 'integer'

class FloatLit(Node):
    '''
    Float literal
    '''
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value
        self.type = 'float'

class StringLit(Node):
    '''
    String literal
    '''
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value
        self.type = 'string'

class CharLit(Node):
    '''
    Character literal
    '''
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value
        self.type = 'char'

class BooleanLit(Node):
    '''
    Boolean literal
    '''
    def __init__(self, value, lineno=0):
        super().__init__(lineno)
        self.value = value
        self.type = 'boolean'

# Aliases para compatibilidad con el parser
Integer = IntegerLit
Float = FloatLit
String = StringLit
Char = CharLit
Boolean = BooleanLit
