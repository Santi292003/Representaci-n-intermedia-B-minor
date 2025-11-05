# checker.py
'''
Chequeo semántico y de tipos para B-Minor
'''

from model   import *
from Symtab  import Symtab
from Typesys import (
    typenames, check_binop, check_unaryop, CheckError,
    is_array_type, get_array_element_type, is_compatible_type
)
from errors  import error, errors_detected


class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        """
        1. Crear la tabla de símbolos global
        2. Visitar todas las declaraciones en n.body
        """
        checker = cls()
        env = Symtab('global')
        for decl in n.body:
            decl.accept(checker, env)
        return env
    
    def _check_incdec_operand(self, n, env):
        """
        Verifica que n.expr sea un lvalue entero (por ahora VarLoc).
        Fija n.type = 'integer'.
        """
        target = n.expr
        if not isinstance(target, VarLoc):
            error("El operador ++/-- requiere una variable (lvalue)", n.lineno)
            n.type = None
            return

        target.accept(self, env)  # fija tipo de la variable
        if target.type != 'integer':
            error(f"El operador ++/-- requiere 'integer', obtenido '{target.type}'", n.lineno)
            n.type = None
            return

        n.type = 'integer'  # el valor de la expresión ++/-- es entero
    
    def visit_PreInc(self, n: PreInc, env: Symtab):
        self._check_incdec_operand(n, env)

    def visit_PreDec(self, n: PreDec, env: Symtab):
        self._check_incdec_operand(n, env)

    def visit_PostInc(self, n: PostInc, env: Symtab):
        self._check_incdec_operand(n, env)

    def visit_PostDec(self, n: PostDec, env: Symtab):
        self._check_incdec_operand(n, env)


    # --------------------------
    # Declaraciones / parámetros
    # --------------------------

    def visit_VarDecl(self, n: VarDecl, env: Symtab):
        """
        VarDecl: chequear inicializador (si existe) y registrar símbolo.
        """
        if n.value is not None:
            n.value.accept(self, env)
            if not is_compatible_type(n.type, n.value.type):
                error(
                    f"En asignación de '{n.name}', no coincide los tipos: "
                    f"esperado '{n.type}', obtenido '{n.value.type}'",
                    n.lineno
                )
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            error(f"La variable '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"La variable '{n.name}' ya declarada", n.lineno)

    def visit_FuncDecl(self, n: FuncDecl, env: Symtab):
        """
        Registrar función, abrir scope propio, registrar parámetros,
        y visitar el cuerpo (BlockStmt garantizado).
        """
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError:
            error(f"La función '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"La función '{n.name}' ya declarada", n.lineno)

        # Nuevo scope de función
        fenv = Symtab(n.name, env)

        # Registrar parámetros como variables (para que VarLoc los resuelva)
        for parm in n.parms:
            parm.accept(self, fenv)

        # Cuerpo: ahora SIEMPRE es BlockStmt
        n.body.accept(self, fenv)

    def visit_VarParm(self, n: VarParm, env: Symtab):
        """
        Registrar parámetro como si fuera una variable local (VarDecl sintético).
        """
        pseudo_decl = VarDecl(n.name, n.type, value=None, lineno=n.lineno)
        try:
            env.add(n.name, pseudo_decl)
        except Symtab.SymbolConflictError:
            error(f"El parámetro '{n.name}' ya declarada y con tipo diferente", n.lineno)
        except Symtab.SymbolDefinedError:
            error(f"El parámetro '{n.name}' ya declarada", n.lineno)

    # -------------
    # Sentencias
    # -------------

    def visit_BlockStmt(self, n: BlockStmt, env: Symtab):
        """
        Crear nuevo scope de bloque y visitar sentencias.
        """
        benv = Symtab(f"block_{id(n)}", env)
        for stmt in (n.statements or []):
            stmt.accept(self, benv)

    def visit_ReturnStmt(self, n: ReturnStmt, env: Symtab):
        """
        - Verificar que esté dentro de una función
        - Verificar tipo de retorno
        """
        if env.name == 'global':
            error("La instrucción return está por fuera de una función", n.lineno)
            return

        func = env.get(env.name)  # busca la FuncDecl en el scope padre
        if n.expr is not None:
            n.expr.accept(self, env)
            if func and func.type != n.expr.type:
                error(f"La función '{func.name}' retorna un tipo diferente", n.lineno)
        else:
            # Si tu lenguaje permite 'return;' solo en void, valida aquí si quieres
            if func and func.type != 'void':
                error(f"La función '{func.name}' requiere un valor de retorno", n.lineno)

    def visit_AssignStmt(self, n: AssignStmt, env: Symtab):
        n.location.accept(self, env)
        n.expr.accept(self, env)
        if not is_compatible_type(n.location.type, n.expr.type):
            error(f"Asignación incompatible: '{n.location.type}' = '{n.expr.type}'", n.lineno)

    def visit_ExprStmt(self, n: ExprStmt, env: Symtab):
        n.expr.accept(self, env)

    def visit_IfStmt(self, n: IfStmt, env: Symtab):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"Condición if debe ser booleana, obtenido '{n.condition.type}'", n.lineno)
        n.then_stmt.accept(self, env)
        if n.else_stmt is not None:
            n.else_stmt.accept(self, env)

    def visit_WhileStmt(self, n: WhileStmt, env: Symtab):
        n.condition.accept(self, env)
        if n.condition.type != 'boolean':
            error(f"Condición while debe ser booleana, obtenido '{n.condition.type}'", n.lineno)
        n.stmt.accept(self, env)

    # -------------
    # Expresiones
    # -------------

    def visit_BinOper(self, n: BinOper, env: Symtab):
        n.left.accept(self, env)
        n.right.accept(self, env)
        n.type = check_binop(n.oper, n.left.type, n.right.type)
        if n.type is None:
            error(f"En '{n.oper}', no coincide los tipos", n.lineno)

    def visit_UnaryOper(self, n: UnaryOper, env: Symtab):
        n.operand.accept(self, env)
        n.type = check_unaryop(n.oper, n.operand.type)
        if n.type is None:
            error(f"Operación unaria '{n.oper}' no permitida para tipo '{n.operand.type}'", n.lineno)

    def visit_FuncCall(self, n: FuncCall, env: Symtab):
        """
        - Buscar la función
        - Chequear número/tipos de args
        - Fijar n.type al tipo de retorno
        """
        func_decl = env.get(n.name)
        if func_decl is None:
            error(f"La función '{n.name}' no está definida", n.lineno)
            n.type = None
            return

        for arg in n.args:
            arg.accept(self, env)

        if len(n.args) != len(func_decl.parms):
            error(
                f"La función '{n.name}' espera {len(func_decl.parms)} argumentos, "
                f"se proporcionaron {len(n.args)}",
                n.lineno
            )
            n.type = func_decl.type
            return

        for i, (arg, parm) in enumerate(zip(n.args, func_decl.parms), start=1):
            if not is_compatible_type(parm.type, arg.type):
                error(
                    f"Argumento {i} de función '{n.name}': "
                    f"esperado '{parm.type}', obtenido '{arg.type}'",
                    n.lineno
                )
        n.type = func_decl.type

    def visit_VarLoc(self, n: VarLoc, env: Symtab):
        decl = env.get(n.name)
        if decl is None:
            error(f"La variable '{n.name}' no está definida", n.lineno)
            n.type = None
        else:
            n.type = decl.type

    def visit_ArrayLoc(self, n: ArrayLoc, env: Symtab):
        """
        ArrayLoc(name, indices):
        - Buscar 'name' en la tabla
        - Chequear que sea array
        - Cada índice debe ser integer
        - El tipo resultante es el elemento tras aplicar todos los índices
        """
        decl = env.get(n.name)
        if decl is None:
            error(f"El arreglo '{n.name}' no está definido", n.lineno)
            n.type = None
            return

        # Tipo actual del símbolo (puede ser array[array[...]elem]])
        curr_type = getattr(decl, 'type', None)

        # Visitar y chequear cada índice
        for idx_expr in (n.indices or []):
            idx_expr.accept(self, env)
            if idx_expr.type != 'integer':
                error(f"Índice de array debe ser entero, obtenido '{idx_expr.type}'", n.lineno)
            if not is_array_type(curr_type):
                error(f"Intento de indexar un no-array de tipo '{curr_type}'", n.lineno)
                n.type = None
                return
            # Bajar un nivel de array
            curr_type = get_array_element_type(curr_type)

        n.type = curr_type

    def visit_ArrayLiteral(self, n: ArrayLiteral, env: Symtab):
        if not n.elements:
            error("Array literal vacío", n.lineno)
            n.type = None
            return

        n.elements[0].accept(self, env)
        elem_t = n.elements[0].type

        for i, e in enumerate(n.elements[1:], start=2):
            e.accept(self, env)
            if not is_compatible_type(elem_t, e.type):
                error(f"Elemento {i} del array: esperado '{elem_t}', obtenido '{e.type}'", n.lineno)

        n.type = f"array[{len(n.elements)}]{elem_t}"

    def visit_PrintStmt(self, n: PrintStmt, env: Symtab):
        """
        print expr;
        - Visita la expresión para fijar su tipo.
        - Opcional: valida que sea un tipo imprimible.
        """
        n.expr.accept(self, env)
        t = getattr(n.expr, "type", None)
        # Por ahora aceptamos estos (enteros/boolean ya, char/string/float listos para cuando los uses)
        imprimibles = {"integer", "boolean", "char", "string", "float"}
        if t not in imprimibles:
            error(f"print: tipo no soportado '{t}'", n.lineno)

    def visit_ForStmt(self, n: ForStmt, env: Symtab):
        """
        Maneja 'for (init; condition; update) stmt' con un scope propio.
        - init puede ser VarDecl o AssignStmt o None.
        - condition debe ser booleana (o None si se permite 'for(;;)').
        - update puede ser AssignStmt o ExprStmt o None.
        - stmt es siempre BlockStmt (gracias a ensure_blockstmt).
        """
        fenv = Symtab(f"for_{id(n)}", env)

        if n.init is not None:
            n.init.accept(self, fenv)

        if n.condition is not None:
            n.condition.accept(self, fenv)
            if n.condition.type != 'boolean':
                error(f"Condición for debe ser booleana, obtenido '{n.condition.type}'", n.lineno)

        # cuerpo
        n.stmt.accept(self, fenv)

        # update se chequea al final del ciclo
        if n.update is not None:
            n.update.accept(self, fenv)

    


    # -------------
    # Literales
    # -------------

    def visit_IntegerLit(self, n: IntegerLit, env: Symtab): pass
    def visit_FloatLit(self, n: FloatLit, env: Symtab): pass
    def visit_StringLit(self, n: StringLit, env: Symtab): pass
    def visit_CharLit(self, n: CharLit, env: Symtab): pass
    def visit_BooleanLit(self, n: BooleanLit, env: Symtab): pass
    
