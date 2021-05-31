from typing import Dict


class IjkSymbol(object):
    def __init__(self, kind: str, type: str, id: int) -> None:
        self.kind: str = kind
        self.type: str = type
        self.id: int = id

    def __repr__(self) -> str:
        return f"Symbol({self.kind}, {self.type}, {self.id})"


class IjkClass(object):

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.symbols: Dict[str, IjkSymbol] = {}

        self.statics: int = 0
        self.fields: int = 0

    def add_field(self, name: str, var_type: str) -> None:
        self.symbols[name] = IjkSymbol('field', var_type, self.fields)
        self.fields += 1

    def add_static(self, name: str, var_type: str) -> None:
        self.symbols[name] = IjkSymbol('static', var_type, self.statics)
        self.statics += 1

    def get_symbol(self, name: str) -> IjkSymbol:
        return self.symbols.get(name)

    def __repr__(self) -> str:
        return f"Class({self.name})"


class IjkSubroutine(object):
    def __init__(self, name: str, subroutine_type: str, return_type: str, ijk_class: IjkClass) -> None:
        self.name: str = name
        self.subroutine_type: str = subroutine_type
        self.return_type: str = return_type
        self.ijk_class: IjkClass = ijk_class

        self.symbols: Dict[str, IjkSymbol] = {}
        self.args: int = 0
        self.vars: int = 0

        if subroutine_type == 'method':
            self.add_arg('this', self.ijk_class.name)

    def add_arg(self, name: str, var_type: str) -> None:
        self.symbols[name] = IjkSymbol('arg', var_type, self.args)
        self.args += 1

    def add_var(self, name, var_type: str) -> None:
        self.symbols[name] = IjkSymbol('var', var_type, self.vars)
        self.vars += 1

    def get_symbol(self, name: str) -> IjkSymbol:
        s = self.symbols.get(name)
        return s if s else self.ijk_class.get_symbol(name)

    def __repr__(self):
        return f"Subroutine({self.subroutine_type} {self.name}({self.args}) -> {self.return_type})"
