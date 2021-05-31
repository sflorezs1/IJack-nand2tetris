from typing import Dict

from ijktypes import IjkSubroutine, IjkSymbol

kinds: Dict[str, str] = {
    'static':   'static',
    'field':    'this',
    'arg':      'argument',
    'var':      'local',
}


class VMWriter(object):
    def __init__(self, ostream) -> None:
        self.ostream = ostream
        self.label_count: int = 0

    def write_if(self, label: str) -> None:
        self.ostream.write('not\n')
        self.ostream.write(f'if-goto {label}\n')

    def write_goto(self, label: str) -> None:
        self.ostream.write(f'goto {label}\n')

    def write_label(self, label: str) -> None:
        self.ostream.write(f'label {label}\n')

    def write_function(self, fun: IjkSubroutine) -> None:
        self.ostream.write(f'function {fun.ijk_class.name}.{fun.name} {fun.vars}\n')

    def write_return(self) -> None:
        self.ostream.write(f'return\n')

    def write_call(self, class_name: str, fun_name: str, args: int) -> None:
        self.ostream.write(f'call {class_name}.{fun_name} {args}\n')

    def write_pop(self, segment: str, offset: int) -> None:
        self.ostream.write(f'pop {segment} {offset}\n')

    def write_push(self, segment: str, offset: int) -> None:
        self.ostream.write(f'push {segment} {offset}\n')

    def write_pop_symbol(self, symbol: IjkSymbol) -> None:
        self.write_pop(kinds[symbol.kind], symbol.id)

    def write_push_symbol(self, symbol: IjkSymbol) -> None:
        self.write_push(kinds[symbol.kind], symbol.id)

    def write(self, action: str) -> None:
        self.ostream.write(f'{action}\n')

    def write_int(self, n: int) -> None:
        self.write_push('constant', n)

    def write_string(self, s: str) -> None:
        s = s[1:-1]
        self.write_int(len(s))  # TODO
        self.write_call('String', 'new', 1)
        for c in s:
            self.write_int(ord(c))
            self.write_call('String', 'appendChar', 2)
