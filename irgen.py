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
        # Visitar todas las declaraciones globales
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
        
        # Obtener tipos de parámetros
        param_types = [self.get_llvm_type(p.type) for p in n.parms]
        
        # Crear tipo de función
        func_type = ir.FunctionType(return_type, param_types)
        
        # Crear función en el módulo
        func = ir.Function(self.module, func_type, name=n.name)
        
        # Crear bloque básico de entrada
        block = func.append_basic_block(name="entry")
        
        # Crear builder para esta función
        self.builder = ir.IRBuilder(block)
        self.current_function = func
        
        # Nuevo scope de variables para esta función
        old_vars = self.vars
        self.vars = {}
        
        # Crear allocas para parámetros y copiar valores
        for i, (parm, arg) in enumerate(zip(n.parms, func.args)):
            arg.name = parm.name
            # Crear alloca para el parámetro
            alloca = self.builder.alloca(self.get_llvm_type(parm.type), name=parm.name)
            self.builder.store(arg, alloca)
            self.vars[parm.name] = alloca
        
        # Visitar el cuerpo de la función
        self._gen_stmt_or_list(n.body, env)
        
        # Si la función no terminó con return, agregar return apropiado
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
                # Operaciones lógicas
                if n.oper == '&&':
                    return self.builder.and_(left, right, name='andtmp')
                elif n.oper == '||':
                    return self.builder.or_(left, right, name='ortmp')
                elif n.oper == '==':
                    return self.builder.icmp_signed('==', left, right, name='cmptmp')
                elif n.oper == '!=':
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

