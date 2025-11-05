# checker.py
'''
Este archivo contendrá la parte de verificación/validación de tipos de 
datos del compilador. Hay varios aspectos que deben gestionarse para que
esto funcione. 
Primero, debe tener una noción de "tipo" en su compilador.
Segundo, debe administrar los entornos (symtab) y el alcance para manejar
los nombres de las definiciones (variables, funciones, etc.)

Una clave para esta parte del proyecto es realizar pruebas adecuadas.
A medida que agregue código, piense en cómo podría probarlo.
'''
# from rich    import print
from typing  import Union, List

from errors  import error, errors_detected
from model   import *
from Symtab  import Symtab
from Typesys import typenames, check_binop, check_unaryop, CheckError, is_array_type, get_array_element_type, is_compatible_type


class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        '''
        1. Crear la tabla de simbol global
        2. Visitar todas las declaraciones en n.body
        '''
        checker = cls()
        env = Symtab('global')
        for decl in n.body:
            decl.accept(checker, env)

        return env
    
    def _visit_stmt_list(self, stmts, env):
        """Visita una lista de statements evitando VarDecl duplicadas
        (mismo nombre y misma línea) que vengan por duplicidad del AST."""
        seen_decls = set()
        for stmt in (stmts or []):
            if isinstance(stmt, VarDecl):
                key = (stmt.name, stmt.lineno)
                if key in seen_decls:
                    # Evita levantar error doble por la misma VarDecl
                    continue
                seen_decls.add(key)
            stmt.accept(self, env)

    
    def _visit_stmt_or_list(self, x, env):
        if x is None:
            return
        if isinstance(x, list):
            for s in x:
                s.accept(self, env)
        else:
            x.accept(self, env)


    def _visit_stmt_list(self, stmts, env):
        """Visita una lista de statements evitando VarDecl duplicadas por (nombre, lineno)."""
        seen_decls = set()
        for stmt in (stmts or []):
            if isinstance(stmt, VarDecl):
                key = (stmt.name, stmt.lineno)
                if key in seen_decls:
                    continue
                seen_decls.add(key)
            stmt.accept(self, env)


    def visit_VarDecl(self, n: VarDecl, env: Symtab):
        '''
        1. Si n.value es diferente de None, verifica que el tipo de datos sea igual al
           de la variable
        2. Agregar 'n' a la tabla de Simbol actual
        '''
        if n.value:
            # Visit the value expression to set its type
            n.value.accept(self, env)
            # Check type compatibility
            if not is_compatible_type(n.type, n.value.type):
                error(f"En asignación de '{n.name}', no coincide los tipos: esperado '{n.type}', obtenido '{n.value.type}'", n.lineno)
        
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            error(f"La variable '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"La variable '{n.name}' ya declarada", n.lineno)

    def visit_FuncDecl(self, n: FuncDecl, env: Symtab):
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            error(f"La función '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"La función '{n.name}' ya declarada", n.lineno)

        env = Symtab(n.name, env)

        for parm in n.parms:
            parm.accept(self, env)


        # n.body es lista según tu model.py
        self._visit_stmt_list(n.body, env)

    def visit_VarParm(self, n: VarParm, env: Symtab):
        """
        Registrar el parámetro en la tabla de símbolos como una variable
        (VarDecl) para que VarLoc lo resuelva igual que a cualquier local.
        """
        pseudo_decl = VarDecl(n.name, n.type, value=None, lineno=n.lineno)
        try:
            env.add(n.name, pseudo_decl)
        except Symtab.SymbolConflictError:
            error(f"El parámetro '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"El parámetro '{n.name}' ya declarada", n.lineno)


    def visit_ReturnStmt(self, n: ReturnStmt, env: Symtab):
        '''
        1. Verificar que el return este dentro de una función.
        2. Visitar n.expr, si existe
        3. Verificar que tipo de n.expr sea igual al tipo de retorno de la función
        '''
        if env.name == 'global':
            error("La instrucción Return esta por fuera de uan función", n.lineno)
        
        func = env.get(env.name)
        if n.expr:
            n.expr.accept(self, env)
            if func.type != n.expr.type:
                error(f"La función '{func.name}' retorna un tipo diferente", n.lineno)

    def visit_BinOper(self, n: BinOper, env: Symtab):
        '''
        1. Visitar el n.left y n.right
        2. Revisar si n.oper es permitida
        '''
        n.left.accept(self, env)
        n.right.accept(self, env)

        n.type = check_binop(n.oper, n.left.type, n.right.type)

        if n.type is None:
            error(f"En '{n.oper}', no coincide los tipos", n.lineno)

    def visit_VarLoc(self, n: VarLoc, env: Symtab):
        '''
        1. Buscar en Symtab la variable n.name y guardar su tipo
        '''
        var_decl = env.get(n.name)

        if var_decl is None:
            error(f"La variable '{n.name}' no está definida", n.lineno)
            n.type = None
        else:
            n.type = var_decl.type

    def visit_UnaryOper(self, n: UnaryOper, env: Symtab):
        '''
        1. Visitar el operando
        2. Revisar si la operación unaria es permitida
        '''
        n.operand.accept(self, env)
        n.type = check_unaryop(n.oper, n.operand.type)
        
        if n.type is None:
            error(f"Operación unaria '{n.oper}' no permitida para tipo '{n.operand.type}'", n.lineno)

    def visit_FuncCall(self, n: FuncCall, env: Symtab):
        '''
        1. Buscar la función en la tabla de símbolos
        2. Visitar todos los argumentos
        3. Verificar que el número y tipos de argumentos coincidan
        '''
        func_decl = env.get(n.name)
        
        if func_decl is None:
            error(f"La función '{n.name}' no está definida", n.lineno)
            n.type = None
            return
        
        # Visit all arguments
        for arg in n.args:
            arg.accept(self, env)
        
        # Check argument count
        if len(n.args) != len(func_decl.parms):
            error(f"La función '{n.name}' espera {len(func_decl.parms)} argumentos, se proporcionaron {len(n.args)}", n.lineno)
            n.type = func_decl.type
            return
        
        # Check argument types
        for i, (arg, parm) in enumerate(zip(n.args, func_decl.parms)):
            if not is_compatible_type(parm.type, arg.type):
                error(f"Argumento {i+1} de función '{n.name}': esperado '{parm.type}', obtenido '{arg.type}'", n.lineno)
        
        n.type = func_decl.type

    def visit_ArrayLoc(self, n: ArrayLoc, env: Symtab):
        '''
        1. Visitar el array y el índice
        2. Verificar que el array sea de tipo array
        3. Verificar que el índice sea entero
        '''
        n.array.accept(self, env)
        n.index.accept(self, env)
        
        if not is_array_type(n.array.type):
            error(f"Intento de indexar un no-array de tipo '{n.array.type}'", n.lineno)
            n.type = None
        elif n.index.type != 'integer':
            error(f"Índice de array debe ser entero, obtenido '{n.index.type}'", n.lineno)
            n.type = None
        else:
            n.type = get_array_element_type(n.array.type)

    def visit_ArrayLiteral(self, n: ArrayLiteral, env: Symtab):
        '''
        1. Visitar todos los elementos
        2. Verificar que todos tengan el mismo tipo
        '''
        if not n.elements:
            error("Array literal vacío", n.lineno)
            n.type = None
            return
        
        # Visit first element to get base type
        n.elements[0].accept(self, env)
        element_type = n.elements[0].type
        
        # Visit remaining elements and check types
        for i, elem in enumerate(n.elements[1:], 1):
            elem.accept(self, env)
            if not is_compatible_type(element_type, elem.type):
                error(f"Elemento {i+1} del array: esperado '{element_type}', obtenido '{elem.type}'", n.lineno)
        
        n.type = f"array[{len(n.elements)}]{element_type}"

    def visit_AssignStmt(self, n: AssignStmt, env: Symtab):
        '''
        1. Visitar la ubicación y la expresión
        2. Verificar compatibilidad de tipos
        '''
        n.location.accept(self, env)
        n.expr.accept(self, env)
        
        if not is_compatible_type(n.location.type, n.expr.type):
            error(f"Asignación incompatible: '{n.location.type}' = '{n.expr.type}'", n.lineno)

    def visit_ExprStmt(self, n: ExprStmt, env: Symtab):
        '''
        1. Visitar la expresión
        '''
        n.expr.accept(self, env)

    def visit_IfStmt(self, n: IfStmt, env: Symtab):
        '''
        1. Visitar la condición
        2. Verificar que la condición sea booleana
        3. Visitar las declaraciones then y else
        '''
        n.condition.accept(self, env)
        
        if n.condition.type != 'boolean':
            error(f"Condición if debe ser booleana, obtenido '{n.condition.type}'", n.lineno)
        
        self._visit_stmt_or_list(n.then_stmt, env)
        if n.else_stmt is not None:
            self._visit_stmt_or_list(n.else_stmt, env)

    def visit_WhileStmt(self, n: WhileStmt, env: Symtab):
        '''
        1. Visitar la condición
        2. Verificar que la condición sea booleana
        3. Visitar el cuerpo
        '''
        n.condition.accept(self, env)
        
        if n.condition.type != 'boolean':
            error(f"Condición while debe ser booleana, obtenido '{n.condition.type}'", n.lineno)
        
        n.stmt.accept(self, env)

    def visit_BlockStmt(self, n: BlockStmt, env: Symtab):
        '''
        1. Crear nuevo scope
        2. Visitar todas las declaraciones
        '''
        # Create new scope for block
        block_env = Symtab(f"block_{id(n)}", env)
        self._visit_stmt_list(n.statements, block_env)

        
    # Literal visitors
    def visit_IntegerLit(self, n: IntegerLit, env: Symtab):
        # Type already set in constructor
        pass

    def visit_FloatLit(self, n: FloatLit, env: Symtab):
        # Type already set in constructor
        pass

    def visit_StringLit(self, n: StringLit, env: Symtab):
        # Type already set in constructor
        pass

    def visit_CharLit(self, n: CharLit, env: Symtab):
        # Type already set in constructor
        pass

    def visit_BooleanLit(self, n: BooleanLit, env: Symtab):
        # Type already set in constructor
        pass