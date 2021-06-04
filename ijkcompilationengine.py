from lexer import IndentLexer
from vm import VMWriter
from ijktypes import *

binary_op_actions: Dict[str, str] = {
    '+': 'add',
    '-': 'sub',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2',
    '&': 'and',
    '|': 'or',
    '<': 'lt',
    '>': 'gt',
    '=': 'eq',
}


class IjkCompilationEngine(object):
    label_count: int = 0

    def __init__(self, istream, ostream) -> None:
        self.lexer: IndentLexer = IndentLexer()
        self.lexer.input(istream.read())
        self.vm: VMWriter = VMWriter(ostream)

    def show_tokens(self):
        while t := self.lexer.token():
            print(t)

    @classmethod
    def get_label(cls) -> str:
        label = f'L{cls.label_count}'
        cls.label_count += 1
        return label

    def compile_class(self) -> None:

        self.lexer.token()  # class

        class_name: str = self.lexer.token().value
        ijk_class: IjkClass = IjkClass(class_name)

        self.lexer.token()  # colon
        self.lexer.token()  # newline
        self.lexer.token()  # INDENT

        self._compile_class_vars(ijk_class)

        self._compile_class_subroutines(ijk_class)

        self.lexer.token()  # DEDENT
        
        print("Compilation Ended Successfully!")

    def _compile_class_vars(self, ijk_class: IjkClass) -> None:
        token = self.lexer.current_token()

        while token and token.type == 'KEYWORD' and token.value in ('static', 'field'):

            self.lexer.token()

            is_static: bool = token.value == 'static'

            var_type = self.lexer.token().value

            still_vars: bool = True
            while still_vars:
                var_name = self.lexer.token().value

                if is_static:
                    ijk_class.add_static(var_name, var_type)
                else:
                    ijk_class.add_field(var_name, var_type)

                token = self.lexer.token()

                still_vars = token and token.value == ','

            token = self.lexer.current_token()

    def _compile_class_subroutines(self, ijk_class: IjkClass) -> None:
        token = self.lexer.current_token()

        while token and token.type == 'KEYWORD' and token.value in ('init', 'fun', 'method'):
            subroutine_kind: str = self.lexer.token().value

            subroutine_name: str = self.lexer.token().value

            ijk_subroutine: IjkSubroutine = IjkSubroutine(subroutine_name, subroutine_kind, "None", ijk_class)

            self.lexer.token()  # LPAREN Open parameter list

            self._compile_parameter_list(ijk_subroutine)

            self.lexer.token()  # RPAREN Close parameter list
            self.lexer.token()  # ARROW

            subroutine_type: str = self.lexer.token().value

            ijk_subroutine.return_type = subroutine_type

            self._compile_subroutine_body(ijk_subroutine)

            token = self.lexer.current_token()

    def _compile_parameter_list(self, ijk_subroutine: IjkSubroutine) -> None:
        token = self.lexer.current_token()

        still_vars = token and token.type in ('KEYWORD', 'IDENTIFIER')

        while still_vars:
            token = self.lexer.token()
            parameter_type: str = token.value

            parameter_name: str = self.lexer.token().value

            ijk_subroutine.add_arg(parameter_name, parameter_type)

            token = self.lexer.current_token()

            if token and token.value == ',':
                self.lexer.token()

                token = self.lexer.current_token()

                still_vars = token and token.type in ('KEYWORD', 'IDENTIFIER')
            else:
                still_vars = False

    def _compile_subroutine_body(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # COLON
        self.lexer.token()  # newline
        self.lexer.token()  # INDENT

        self._compile_subroutine_vars(ijk_subroutine)

        self.vm.write_function(ijk_subroutine)

        if ijk_subroutine.subroutine_type == 'init':
            fields: int = ijk_subroutine.ijk_class.fields
            self.vm.write_push('constant', fields)
            self.vm.write_call('Memory', 'alloc', 1)
            self.vm.write_pop('pointer', 0)
        elif ijk_subroutine.subroutine_type == 'method':
            self.vm.write_push('argument', 0)
            self.vm.write_pop('pointer', 0)

        self._compile_statements(ijk_subroutine)

        self.lexer.token()  # DEDENT

    def _compile_subroutine_vars(self, ijk_subroutine: IjkSubroutine) -> None:

        token = self.lexer.current_token()

        while token and token.value == 'var':
            self.lexer.token()  # var

            var_type: str = self.lexer.token().value

            var_name: str = self.lexer.token().value

            ijk_subroutine.add_var(var_name, var_type)

            while self.lexer.token().value == ',':
                var_name = self.lexer.token().value
                ijk_subroutine.add_var(var_name, var_type)

            token = self.lexer.current_token()

    def _compile_statements(self, ijk_subroutine: IjkSubroutine) -> None:

        check_statements: bool = True
        while check_statements:
            token = self.lexer.current_token()

            if token and token.value == 'if':
                self._compile_statement_if(ijk_subroutine)
            elif token and token.value == 'while':
                self._compile_statement_while(ijk_subroutine)
            elif token and token.value == 'let':
                self._compile_statement_let(ijk_subroutine)
            elif token and token.value == 'do':
                self._compile_statement_do(ijk_subroutine)
            elif token and token.value == 'return':
                self._compile_statement_return(ijk_subroutine)
            else:
                check_statements = False

    def _compile_statement_if(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # if
        self.lexer.token()  # (

        self._compile_expression(ijk_subroutine)

        self.lexer.token()  # )
        self.lexer.token()  # COLON
        self.lexer.token()  # newline
        self.lexer.token()  # INDENT

        false_label = IjkCompilationEngine.get_label()
        end_label = IjkCompilationEngine.get_label()

        self.vm.write_if(false_label)

        self._compile_statements(ijk_subroutine)

        self.vm.write_goto(end_label)
        self.vm.write_label(false_label)

        self.lexer.token()  # DEDENT

        token = self.lexer.current_token()

        if token and token.value == 'else':
            self.lexer.token()  # else
            self.lexer.token()  # COLON
            self.lexer.token()  # newline
            self.lexer.token()  # INDENT

            self._compile_statements(ijk_subroutine)

            self.lexer.token()  # DEDENT

        self.vm.write_label(end_label)

    def _compile_statement_while(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # while
        self.lexer.token()  # (

        while_label: str = IjkCompilationEngine.get_label()
        false_label: str = IjkCompilationEngine.get_label()

        self.vm.write_label(while_label)
        self._compile_expression(ijk_subroutine)

        self.lexer.token()  # )
        self.lexer.token()  # COLON
        self.lexer.token()  # newline
        self.lexer.token()  # INDENT

        self.vm.write_if(false_label)

        self._compile_statements(ijk_subroutine)

        self.vm.write_goto(while_label)
        self.vm.write_label(false_label)

        self.lexer.token()  # DEDENT

    def _compile_statement_let(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # let
        var_name: str = self.lexer.token().value
        ijk_symbol: IjkSymbol = ijk_subroutine.get_symbol(var_name)

        token = self.lexer.current_token()

        is_array: bool = token and token.value == '['
        if is_array:
            self.lexer.token()  # [
            self._compile_expression(ijk_subroutine)
            self.lexer.token()  # ]
            self.lexer.token()  # =

            self.vm.write_push_symbol(ijk_symbol)
            self.vm.write('add')

            self._compile_expression(ijk_subroutine)
            self.vm.write_pop('temp', 0)
            self.vm.write_pop('pointer', 1)
            self.vm.write_push('temp', 0)
            self.vm.write_pop('that', 0)
        else:
            self.lexer.token()
            self._compile_expression(ijk_subroutine)
            self.vm.write_pop_symbol(ijk_symbol)
        self.lexer.token()  # newline

    def _compile_statement_do(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # do

        self._compile_term(ijk_subroutine)

        self.vm.write_pop('temp', 0)
        self.lexer.token()  # newline

    def _compile_statement_return(self, ijk_subroutine: IjkSubroutine) -> None:
        self.lexer.token()  # return
        token = self.lexer.current_token()

        if token and token.type != 'NEWLINE':
            self._compile_expression(ijk_subroutine)
        else:
            self.vm.write_int(0)

        self.vm.write_return()
        self.lexer.token()  # newline

    def _compile_expression_list(self, ijk_subroutine: IjkSubroutine) -> int:
        count: int = 0

        token = self.lexer.current_token()

        while token and token.value != ')':

            if token and token.value == ',':
                self.lexer.token()

            count += 1
            self._compile_expression(ijk_subroutine)
            token = self.lexer.current_token()

        return count

    def _compile_expression(self, ijk_subroutine: IjkSubroutine) -> None:
        self._compile_term(ijk_subroutine)

        token = self.lexer.current_token()

        while token and token.value and token.value in '+-*/&|<>=':
            binary_op: str = self.lexer.token().value

            self._compile_term(ijk_subroutine)

            self.vm.write(binary_op_actions[binary_op])

            token = self.lexer.current_token()

    def _compile_term(self, ijk_subroutine: IjkSubroutine) -> None:
        token = self.lexer.token()

        if token and token.value in ('-', '!'):
            self._compile_term(ijk_subroutine)
            if token and token.value == '-':
                self.vm.write('neg')
            elif token and token.value == '!':
                self.vm.write('not')
        elif token and token.value == '(':
            self._compile_expression(ijk_subroutine)
            self.lexer.token()  # )
        elif token and token.type == 'INTEGER_CONSTANT':
            self.vm.write_int(token.value)
        elif token and token.type == 'STRING_CONSTANT':
            self.vm.write_string(token.value)
        elif token and token.type == 'KEYWORD':
            if token.value == 'self':
                self.vm.write_push('pointer', 0)
            else:
                self.vm.write_int(0)
                if token.value == 'true':
                    self.vm.write('not')
        elif token and token.type == 'IDENTIFIER':
            id_name: str = token.value
            variable: IjkSymbol = ijk_subroutine.get_symbol(id_name)

            token = self.lexer.current_token()

            if token.value == '[':
                self.lexer.token()  # [
                self._compile_expression(ijk_subroutine)

                self.vm.write_push_symbol(variable)
                self.vm.write('add')

                self.vm.write_pop('pointer', 1)
                self.vm.write_push('that', 0)
                self.lexer.token()  # ]
            else:
                fun_name: str = id_name
                fun_class: str = ijk_subroutine.ijk_class.name

                default_call = True

                args: int = 0

                if token.value == '.':
                    self.lexer.token()  # .
                    default_call = False

                    fun_object: IjkSymbol = ijk_subroutine.get_symbol(id_name)
                    fun_name: str = self.lexer.token().value

                    if fun_object:
                        fun_class = variable.type
                        args = 1
                        self.vm.write_push_symbol(variable)
                    else:
                        fun_class = id_name
                    token = self.lexer.current_token()

                if token.value == '(':
                    if default_call:
                        args = 1
                        self.vm.write_push('pointer', 0)

                    self.lexer.token()  # (

                    args += self._compile_expression_list(ijk_subroutine)

                    self.vm.write_call(fun_class, fun_name, args)

                    self.lexer.token()  # )
                elif variable:
                    self.vm.write_push_symbol(variable)


