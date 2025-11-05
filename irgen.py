# irgen.py
'''
Generador de código intermedio LLVM IR para B-Minor
Versión 1: Variables, literales y aritmética básica
'''

from llvmlite import ir
from model import *
from Symtab import Symtab

class IRGenerator(Visitor):
    def __init__(self):
        # Módulo LLVM principal
        self.module = ir.Module(name="bminor_program")
        
        # Builder para generar instrucciones (se asigna por función)
        self.builder = None
        
        # Función actual en la que estamos generando código
        self.current_function = None
        
        # Mapeo de nombres de variables a sus punteros LLVM (allocas)
        # Estructura: {'variable_name': llvm_pointer}
        self.vars = {}
        
        # Mapeo de tipos B-Minor a tipos LLVM
        self.type_map = {
            'integer': ir.IntType(32),      # i32
            'float': ir.DoubleType(),       # double (64-bit)
            'boolean': ir.IntType(1),       # i1
            'char': ir.IntType(8),          # i8
            'void': ir.VoidType(),          # void
        }

        self._str_const_count = 0

    def _declare_printf(self):
        """Declara printf si no existe y lo retorna."""
        printf = self.module.globals.get("printf")
        if not isinstance(printf, ir.Function):
            fnty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
            printf = ir.Function(self.module, fnty, name="printf")
        return printf

    def _cstr(self, s: str, name_hint="fmt"):
        """
        Crea una constante global terminada en '\0' y retorna i8* al inicio.
        Útil para formatos: "%d\\n", "%f\\n", etc.
        """
        self._str_const_count += 1
        name = f"{name_hint}_{self._str_const_count}"

        data = bytearray(s.encode("utf8")) + b"\x00"
        arr_ty = ir.ArrayType(ir.IntType(8), len(data))
        const = ir.Constant(arr_ty, data)

        g = ir.GlobalVariable(self.module, arr_ty, name=name)
        g.linkage = 'internal'
        g.global_constant = True
        g.initializer = const

        zero = ir.Constant(ir.IntType(32), 0)
        ptr = self.builder.gep(g, [zero, zero], inbounds=True)  # i8*
        return ptr

    def _string_literal_ptr(self, s: str, name_hint="str"):
        """
        Como _cstr, pero pensado para StringLit: retorna i8* a una
        constante global con '\0' final.
        """
        return self._cstr(s, name_hint=name_hint)



    def _as_bool(self, val):
        """
        Normaliza cualquier valor a i1 para usar en cbranch.
        - Si ya es i1, lo devuelve.
        - Si es i32, compara != 0.
        - Si es double, compara != 0.0.
        """
        if isinstance(val.type, ir.IntType) and val.type.width == 1:
            return val
        if isinstance(val.type, ir.IntType):
            zero = ir.Constant(val.type, 0)
            return self.builder.icmp_signed('!=', val, zero)
        if isinstance(val.type, ir.DoubleType):
            zero = ir.Constant(val.type, 0.0)
            return self.builder.fcmp_ordered('!=', val, zero)
        raise Exception(f"No puedo convertir a booleano: {val.type}")
    
    def _gen_stmt_or_list(self, x, env):
        if x is None:
            return
        if isinstance(x, BlockStmt):
            x.accept(self, env)
            return
        # ¿lista de statements?
        if isinstance(x, list):
            for s in x:
                s.accept(self, env)
            return
        # nodo suelto
        x.accept(self, env)

    def _gen_incdec_varloc(self, varloc: VarLoc, delta: int, return_old: bool):
        """
        Implementa:
        old = load var
        new = old (+/-) 1
        store new -> var
        return old (post) o new (pre)
        """
        # Debe ser variable local (alloca) o global (puntero)
        var_ptr = self.vars[varloc.name]
        oldv = self.builder.load(var_ptr, name=f"{varloc.name}.ld")
        one  = ir.Constant(ir.IntType(32), 1)

        if delta == +1:
            newv = self.builder.add(oldv, one, name=f"{varloc.name}.inc")
        else:
            newv = self.builder.sub(oldv, one, name=f"{varloc.name}.dec")

        self.builder.store(newv, var_ptr)
        return oldv if return_old else newv


    
    
    @classmethod
    def generate(cls, ast, env):
        '''
        Método principal para generar IR desde un AST
        '''
        generator = cls()
        ast.accept(generator, env)
        return generator.module
    
    def get_llvm_type(self, bminor_type):
        '''
        Convierte un tipo de B-Minor a tipo LLVM
        '''
        if bminor_type in self.type_map:
            return self.type_map[bminor_type]
        else:
            raise Exception(f"Tipo desconocido: {bminor_type}")
    
    def visit_Program(self, n: Program, env: Symtab):
        '''
        Genera código para todo el programa
        '''
        for decl in n.body:
            if isinstance(decl, FuncDecl):
                ret_ty = self.get_llvm_type(decl.type)
                param_tys = [self.get_llvm_type(p.type) for p in decl.parms]
                self._get_or_declare_function(decl.name, ret_ty, param_tys)

    
        for decl in n.body:
            decl.accept(self, env)


    
    def visit_VarDecl(self, n: VarDecl, env: Symtab):
        '''
        Genera código para declaración de variable
        
        Si estamos dentro de una función: crea alloca (variable local)
        Si estamos en scope global: crea variable global
        '''
        llvm_type = self.get_llvm_type(n.type)
        
        if self.current_function is None:
            # Variable global
            # En LLVM, las variables globales deben tener un inicializador
            if n.value:
                # Si hay valor inicial, lo evaluamos después
                # Por ahora, inicializamos con 0
                global_var = ir.GlobalVariable(self.module, llvm_type, name=n.name)
                
                if n.type == 'integer':
                    global_var.initializer = ir.Constant(llvm_type, 0)
                elif n.type == 'float':
                    global_var.initializer = ir.Constant(llvm_type, 0.0)
                elif n.type == 'boolean':
                    global_var.initializer = ir.Constant(llvm_type, 0)
                
                self.vars[n.name] = global_var
            else:
                # Sin valor inicial, inicializar con 0
                global_var = ir.GlobalVariable(self.module, llvm_type, name=n.name)
                
                if n.type == 'integer':
                    global_var.initializer = ir.Constant(llvm_type, 0)
                elif n.type == 'float':
                    global_var.initializer = ir.Constant(llvm_type, 0.0)
                elif n.type == 'boolean':
                    global_var.initializer = ir.Constant(llvm_type, 0)
                
                self.vars[n.name] = global_var
        else:
            # Variable local dentro de una función
            # Usar alloca para reservar espacio en el stack
            alloca = self.builder.alloca(llvm_type, name=n.name)
            self.vars[n.name] = alloca
            
            # Si hay valor inicial, evaluarlo y guardarlo
            if n.value:
                init_value = n.value.accept(self, env)
                self.builder.store(init_value, alloca)
    
    def visit_FuncDecl(self, n: FuncDecl, env: Symtab):
        '''
        Genera código para declaración de función
        '''
        # Obtener tipo de retorno
        return_type = self.get_llvm_type(n.type)
        param_types = [self.get_llvm_type(p.type) for p in n.parms]

        # Recuperar o declarar (si alguien llama a esta antes)
        func = self._get_or_declare_function(n.name, return_type, param_types)

        # Bloque de entrada y builder
        entry = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry)
        self.current_function = func

        # Nuevo "scope" de variables locales
        old_vars = self.vars
        self.vars = {}

        # Nombrar args y alloca + store
        for parm, arg in zip(n.parms, func.args):
            arg.name = parm.name
            alloca = self.builder.alloca(self.get_llvm_type(parm.type), name=parm.name)
            self.builder.store(arg, alloca)
            self.vars[parm.name] = alloca

        # Cuerpo (ya es BlockStmt)
        n.body.accept(self, env)

        # Epílogo si no hay return explícito
        if not self.builder.block.is_terminated:
            if n.type == 'void':
                self.builder.ret_void()
            elif n.type == 'integer':
                self.builder.ret(ir.Constant(ir.IntType(32), 0))
            elif n.type == 'boolean':
                self.builder.ret(ir.Constant(ir.IntType(1), 0))

        # Restaurar contexto
        self.vars = old_vars
        self.current_function = None
        self.builder = None
    
    def visit_ReturnStmt(self, n: ReturnStmt, env: Symtab):
        '''
        Genera código para return
        '''
        if n.expr:
            # Evaluar expresión de retorno
            return_value = n.expr.accept(self, env)
            self.builder.ret(return_value)
        else:
            # Return sin valor (void)
            self.builder.ret_void()
    
    def visit_AssignStmt(self, n: AssignStmt, env: Symtab):
        '''
        Genera código para asignación
        '''
        # Evaluar la expresión del lado derecho
        value = n.expr.accept(self, env)
        
        # Obtener el puntero de la variable (lado izquierdo)
        if isinstance(n.location, VarLoc):
            var_ptr = self.vars[n.location.name]
            self.builder.store(value, var_ptr)
    
    def visit_ExprStmt(self, n: ExprStmt, env: Symtab):
        '''
        Genera código para una expresión como statement
        '''
        n.expr.accept(self, env)
    
    def visit_BinOper(self, n: BinOper, env: Symtab):
        '''
        Genera código para operaciones binarias
        '''
        # Evaluar operandos
        left = n.left.accept(self, env)
        right = n.right.accept(self, env)
        
        # Determinar el tipo de operación
        if n.type == 'integer':
            # Operaciones aritméticas con enteros
            if n.oper == '+':
                return self.builder.add(left, right, name='addtmp')
            elif n.oper == '-':
                return self.builder.sub(left, right, name='subtmp')
            elif n.oper == '*':
                return self.builder.mul(left, right, name='multmp')
            elif n.oper == '/':
                return self.builder.sdiv(left, right, name='divtmp')
            elif n.oper == '%':
                return self.builder.srem(left, right, name='modtmp')
        
        elif n.type == 'float':
            # Operaciones aritméticas con floats
            if n.oper == '+':
                return self.builder.fadd(left, right, name='faddtmp')
            elif n.oper == '-':
                return self.builder.fsub(left, right, name='fsubtmp')
            elif n.oper == '*':
                return self.builder.fmul(left, right, name='fmultmp')
            elif n.oper == '/':
                return self.builder.fdiv(left, right, name='fdivtmp')
        
        elif n.type == 'boolean':
            # Operaciones de comparación
            if n.left.type == 'integer':
                # Comparaciones con enteros
                if n.oper == '<':
                    return self.builder.icmp_signed('<', left, right, name='cmptmp')
                elif n.oper == '<=':
                    return self.builder.icmp_signed('<=', left, right, name='cmptmp')
                elif n.oper == '>':
                    return self.builder.icmp_signed('>', left, right, name='cmptmp')
                elif n.oper == '>=':
                    return self.builder.icmp_signed('>=', left, right, name='cmptmp')
                elif n.oper == '==':
                    return self.builder.icmp_signed('==', left, right, name='cmptmp')
                elif n.oper == '!=':
                    return self.builder.icmp_signed('!=', left, right, name='cmptmp')
            
            elif n.left.type == 'float':
                # Comparaciones con floats
                if n.oper == '<':
                    return self.builder.fcmp_ordered('<', left, right, name='fcmptmp')
                elif n.oper == '<=':
                    return self.builder.fcmp_ordered('<=', left, right, name='fcmptmp')
                elif n.oper == '>':
                    return self.builder.fcmp_ordered('>', left, right, name='fcmptmp')
                elif n.oper == '>=':
                    return self.builder.fcmp_ordered('>=', left, right, name='fcmptmp')
                elif n.oper == '==':
                    return self.builder.fcmp_ordered('==', left, right, name='fcmptmp')
                elif n.oper == '!=':
                    return self.builder.fcmp_ordered('!=', left, right, name='fcmptmp')
            
            elif n.left.type == 'boolean':
                # LÓGICAS CON CORTOCIRCUITO
                if n.oper == '&&':
                    return self._short_circuit_and(n.left, n.right, env)
                elif n.oper == '||':
                    return self._short_circuit_or(n.left, n.right, env)
                # Igualdad/Desigualdad entre booleanos
                elif n.oper == '==':
                    left  = n.left.accept(self, env)
                    right = n.right.accept(self, env)
                    return self.builder.icmp_signed('==', left, right, name='cmptmp')
                elif n.oper == '!=':
                    left  = n.left.accept(self, env)
                    right = n.right.accept(self, env)
                    return self.builder.icmp_signed('!=', left, right, name='cmptmp')
        
        raise Exception(f"Operación binaria no soportada: {n.oper} con tipo {n.type}")
    
    def visit_UnaryOper(self, n: UnaryOper, env: Symtab):
        '''
        Genera código para operaciones unarias
        '''
        operand = n.operand.accept(self, env)
        
        if n.type == 'integer':
            if n.oper == '-':
                # Negación: 0 - operand
                zero = ir.Constant(ir.IntType(32), 0)
                return self.builder.sub(zero, operand, name='negtmp')
            elif n.oper == '+':
                # Unario + no hace nada
                return operand
        
        elif n.type == 'float':
            if n.oper == '-':
                # Negación float: 0.0 - operand
                zero = ir.Constant(ir.DoubleType(), 0.0)
                return self.builder.fsub(zero, operand, name='fnegtmp')
            elif n.oper == '+':
                return operand
        
        elif n.type == 'boolean':
            if n.oper == '!':
                # Negación lógica: xor con 1
                one = ir.Constant(ir.IntType(1), 1)
                return self.builder.xor(operand, one, name='nottmp')
        
        raise Exception(f"Operación unaria no soportada: {n.oper} con tipo {n.type}")
    
    def visit_VarLoc(self, n: VarLoc, env: Symtab):
        '''
        Genera código para acceso a variable (load)
        '''
        var_ptr = self.vars[n.name]
        return self.builder.load(var_ptr, name=n.name)
    
    # Literales
    def visit_IntegerLit(self, n: IntegerLit, env: Symtab):
        '''
        Genera código para literal entero
        '''
        return ir.Constant(ir.IntType(32), n.value)
    
    def visit_FloatLit(self, n: FloatLit, env: Symtab):
        '''
        Genera código para literal float
        '''
        return ir.Constant(ir.DoubleType(), n.value)
    
    def visit_BooleanLit(self, n: BooleanLit, env: Symtab):
        '''
        Genera código para literal booleano
        '''
        value = 1 if n.value else 0
        return ir.Constant(ir.IntType(1), value)
    
    def visit_CharLit(self, n: CharLit, env: Symtab):
        '''
        Genera código para literal char
        '''
        return ir.Constant(ir.IntType(8), ord(n.value))
    
    def visit_BlockStmt(self, n: BlockStmt, env: Symtab):
        # Guardar contexto de variables (sombras de bloque)
        old_vars = self.vars
        self.vars = dict(self.vars)  # capa nueva

        for stmt in (n.statements or []):
            stmt.accept(self, env)

        # Restaurar
        self.vars = old_vars

    def visit_IfStmt(self, n: IfStmt, env: Symtab):
        # 1) Condición
        cond_val = n.condition.accept(self, env)
        cond_i1  = self._as_bool(cond_val)

        # 2) Bloques
        then_bb  = self.current_function.append_basic_block(name="if.then")
        merge_bb = self.current_function.append_basic_block(name="if.end")
        else_bb  = self.current_function.append_basic_block(name="if.else") if n.else_stmt else None

        # 3) Branch condicional
        if else_bb:
            self.builder.cbranch(cond_i1, then_bb, else_bb)
        else:
            self.builder.cbranch(cond_i1, then_bb, merge_bb)

        # 4) THEN
        self.builder.position_at_end(then_bb)
        self._gen_stmt_or_list(n.then_stmt, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(merge_bb)

        # 5) ELSE (si existe)
        if else_bb:
            self.builder.position_at_end(else_bb)
            self._gen_stmt_or_list(n.else_stmt, env)
            if not self.builder.block.is_terminated:
                self.builder.branch(merge_bb)

        # 6) MERGE
        self.builder.position_at_end(merge_bb)

    def visit_WhileStmt(self, n: WhileStmt, env):
        """
        while (cond) body
        CFG:
        br cond_bb
        cond_bb:
        cond = ...
        cbr cond, body_bb, end_bb
        body_bb:
        ...body...
        br cond_bb
        end_bb:
        (continuación)
        """
        func = self.current_function

        cond_bb = func.append_basic_block("while.cond")
        body_bb = func.append_basic_block("while.body")
        end_bb  = func.append_basic_block("while.end")

        # Saltamos a la evaluación de la condición
        self.builder.branch(cond_bb)

        # Condición
        self.builder.position_at_end(cond_bb)
        cond_val = n.condition.accept(self, env)
        cond_i1  = self._as_bool(cond_val)
        self.builder.cbranch(cond_i1, body_bb, end_bb)

        # Cuerpo (siempre BlockStmt)
        self.builder.position_at_end(body_bb)
        n.stmt.accept(self, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)

        # Merge / salida del while
        self.builder.position_at_end(end_bb)

    def _short_circuit_and(self, left_node, right_node, env):
        """
        Genera:
        left = ...
        cbr left, rhs_bb, end_bb
        rhs_bb:
        right = ...
        br end_bb
        end_bb:
        phi [0, from_left_bb], [right, rhs_bb]
        """
        func = self.current_function

        # Evalúa left y guarda bloque actual (desde donde saltan las ramas)
        left_val = left_node.accept(self, env)
        left_i1  = self._as_bool(left_val)
        from_left_bb = self.builder.block

        rhs_bb  = func.append_basic_block("and.rhs")
        end_bb  = func.append_basic_block("and.end")

        # Si left es true -> evaluar right, si no -> resultado false
        self.builder.cbranch(left_i1, rhs_bb, end_bb)

        # RHS: evalúa el derecho sólo si hizo falta
        self.builder.position_at_end(rhs_bb)
        right_i1 = self._as_bool(right_node.accept(self, env))
        self.builder.branch(end_bb)
        from_rhs_bb = self.builder.block

        # END: une resultados con PHI
        self.builder.position_at_end(end_bb)
        phi = self.builder.phi(ir.IntType(1), name="andtmp")
        phi.add_incoming(ir.Constant(ir.IntType(1), 0), from_left_bb)  # left==false -> false
        phi.add_incoming(right_i1, from_rhs_bb)                        # left==true -> right
        return phi

    def _short_circuit_or(self, left_node, right_node, env):
        """
        Genera:
        left = ...
        cbr left, end_bb, rhs_bb
        rhs_bb:
        right = ...
        br end_bb
        end_bb:
        phi [1, from_left_bb], [right, rhs_bb]
        """
        func = self.current_function

        left_val = left_node.accept(self, env)
        left_i1  = self._as_bool(left_val)
        from_left_bb = self.builder.block

        rhs_bb  = func.append_basic_block("or.rhs")
        end_bb  = func.append_basic_block("or.end")

        # Si left es true -> ya es true (no evalúa right). Si no -> evalúa right
        self.builder.cbranch(left_i1, end_bb, rhs_bb)

        # RHS
        self.builder.position_at_end(rhs_bb)
        right_i1 = self._as_bool(right_node.accept(self, env))
        self.builder.branch(end_bb)
        from_rhs_bb = self.builder.block

        # END (PHI)
        self.builder.position_at_end(end_bb)
        phi = self.builder.phi(ir.IntType(1), name="ortmp")
        phi.add_incoming(ir.Constant(ir.IntType(1), 1), from_left_bb)  # left==true -> true
        phi.add_incoming(right_i1, from_rhs_bb)                        # left==false -> right
        return phi
    
    def _get_or_declare_function(self, name, ret_ty, param_tys):
        """
        Devuelve (o declara si no existe) una ir.Function con firma (ret_ty, param_tys).
        """
        existing = self.module.globals.get(name)
        if isinstance(existing, ir.Function):
            return existing
        fnty = ir.FunctionType(ret_ty, param_tys)
        func = ir.Function(self.module, fnty, name=name)
        return func
    
    def visit_FuncCall(self, n: FuncCall, env: Symtab):
        # Buscar la función en el módulo
        callee = self.module.globals.get(n.name)
        if not isinstance(callee, ir.Function):
            raise Exception(f"Func '{n.name}' no declarada en IR")

        # Evaluar argumentos
        llvm_args = [arg.accept(self, env) for arg in n.args]

        # Emitir llamada
        return self.builder.call(callee, llvm_args, name=(n.name + ".call"))
    
    def visit_PrintStmt(self, n: PrintStmt, env: Symtab):
        printf = self._declare_printf()
        val = n.expr.accept(self, env)

        # INT32: %d
        if isinstance(val.type, ir.IntType) and val.type.width == 32:
            fmt = self._cstr("%d\n", "fmt_int")
            self.builder.call(printf, [fmt, val])
            return

        # BOOL (i1) -> promover a i32 y usar %d
        if isinstance(val.type, ir.IntType) and val.type.width == 1:
            fmt = self._cstr("%d\n", "fmt_bool")
            i32 = self.builder.zext(val, ir.IntType(32))  # promoción varargs
            self.builder.call(printf, [fmt, i32])
            return

        # FLOAT (double): %f  (si lo quieres ya)
        if isinstance(val.type, ir.DoubleType):
            fmt = self._cstr("%f\n", "fmt_float")
            self.builder.call(printf, [fmt, val])
            return

        # CHAR (i8) -> promover a i32 y usar %c
        if isinstance(val.type, ir.IntType) and val.type.width == 8:
            fmt = self._cstr("%c\n", "fmt_char")
            i32 = self.builder.zext(val, ir.IntType(32))
            self.builder.call(printf, [fmt, i32])
            return

        # STRING (i8*): %s
        if isinstance(val.type, ir.PointerType) and isinstance(val.type.pointee, ir.IntType) and val.type.pointee.width == 8:
            fmt = self._cstr("%s\n", "fmt_str")
            self.builder.call(printf, [fmt, val])
            return

        raise Exception(f"print: tipo no soportado {val.type}")
    
    def visit_StringLit(self, n: StringLit, env: Symtab):
        # Retorna i8* a una constante global con el contenido del literal
        return self._string_literal_ptr(n.value, name_hint="strlit")
    
    def visit_ForStmt(self, n: ForStmt, env):
        """
        Desazucar a CFG de while:
        init;
        br cond_bb
        cond_bb:
        cond = ... (si no hay cond, usamos true)
        cbr cond, body_bb, end_bb
        body_bb:
        body...
        br upd_bb
        upd_bb:
        update...
        br cond_bb
        end_bb:
        ...
        """
        func = self.current_function

        # init
        if n.init is not None:
            n.init.accept(self, env)

        cond_bb = func.append_basic_block("for.cond")
        body_bb = func.append_basic_block("for.body")
        upd_bb  = func.append_basic_block("for.update")
        end_bb  = func.append_basic_block("for.end")

        # saltar a condición
        self.builder.branch(cond_bb)

        # condición
        self.builder.position_at_end(cond_bb)
        if n.condition is not None:
            cond_val = n.condition.accept(self, env)
            cond_i1  = self._as_bool(cond_val)
        else:
            # for(;;) equivalente a cond true
            cond_i1 = ir.Constant(ir.IntType(1), 1)
        self.builder.cbranch(cond_i1, body_bb, end_bb)

        # cuerpo
        self.builder.position_at_end(body_bb)
        n.stmt.accept(self, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(upd_bb)

        # update
        self.builder.position_at_end(upd_bb)
        if n.update is not None:
            n.update.accept(self, env)
        if not self.builder.block.is_terminated:
            self.builder.branch(cond_bb)

        # fin
        self.builder.position_at_end(end_bb)

    def visit_PreInc(self, n: PreInc, env):
        # ++x  -> devuelve valor nuevo
        if not isinstance(n.expr, VarLoc):
            raise Exception("++ requiere variable (lvalue)")
        return self._gen_incdec_varloc(n.expr, +1, return_old=False)

    def visit_PreDec(self, n: PreDec, env):
        # --x  -> devuelve valor nuevo
        if not isinstance(n.expr, VarLoc):
            raise Exception("-- requiere variable (lvalue)")
        return self._gen_incdec_varloc(n.expr, -1, return_old=False)

    def visit_PostInc(self, n: PostInc, env):
        # x++  -> devuelve valor antiguo
        if not isinstance(n.expr, VarLoc):
            raise Exception("++ requiere variable (lvalue)")
        return self._gen_incdec_varloc(n.expr, +1, return_old=True)

    def visit_PostDec(self, n: PostDec, env):
        # x--  -> devuelve valor antiguo
        if not isinstance(n.expr, VarLoc):
            raise Exception("-- requiere variable (lvalue)")
        return self._gen_incdec_varloc(n.expr, -1, return_old=True)









    
    
    

