from typing import List, Optional, Tuple, Iterator, Dict
import ply.lex as lex
from more_itertools import peekable

# Define Literals
literals: List[str] = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '!']

# Define tokens
tokens: Tuple[str, ...] = (
    'KEYWORD',
    'INTEGER_CONSTANT',
    'IDENTIFIER',
    'ARROW',
    'SYMBOL',
    'COLON',
    'STRING_CONSTANT',
    'WS',
    'NEWLINE',
)

RESERVED: Dict[str, str] = {
    'class':    'KEYWORD',
    'method':   'KEYWORD',
    'init':     'KEYWORD',
    'fun':      'KEYWORD',
    'field':    'KEYWORD',
    'static':   'KEYWORD',
    'var':      'KEYWORD',
    'num':      'KEYWORD',
    'char':     'KEYWORD',
    'bool':     'KEYWORD',
    'void':     'KEYWORD',
    'true':     'KEYWORD',
    'false':    'KEYWORD',
    'none':     'KEYWORD',
    'self':     'KEYWORD',
    'let':      'KEYWORD',
    'do':       'KEYWORD',
    'if':       'KEYWORD',
    'else':     'KEYWORD',
    'while':    'KEYWORD',
    'return':   'KEYWORD',
}

# Regular expressions for simple Tokens
t_COLON: str = r'\:'


def t_ARROW(t: lex.LexToken) -> lex.LexToken:
    r'->'
    return t


# Regular expressions for complex Tokens
def t_INTEGER_CONSTANT(t: lex.LexToken) -> lex.LexToken:
    r'\d+'
    t.value = int(t.value)
    t.type = "INTEGER_CONSTANT"
    return t


def t_SYMBOL(t: lex.LexToken) -> lex.LexToken:
    r'\(|\)|\[|\]|\.|,|\+|-|\*|/|&|\||\<|\>|=|!'
    t.type = "SYMBOL"
    return t


def t_IDENTIFIER(t: lex.LexToken) -> lex.LexToken:
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = RESERVED.get(t.value, "IDENTIFIER")
    return t


def t_STRING_CONSTANT(t):
    r'\"(.*)\"'
    t.type = "STRING_CONSTANT"
    return t


def t_WS(t: lex.LexToken) -> Optional[lex.LexToken]:
    r'[ ]+'
    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        return t


def t_newline(t: lex.LexToken) -> Optional[lex.LexToken]:
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    if t.lexer.paren_count == 0:
        return t


def t_comment(t: lex.LexToken) -> None:
    r'[ ]*\043[^\n]*'


def t_error(t: lex.LexToken) -> None:
    print(f"=> Illegal character '{t.value[0]}' at line {t.lineno}, position {t.lexpos}")
    print("Skiping character")
    t.lexer.skip(1)


# Indent Magic

# Based on: https://github.com/google/nixysa/blob/master/third_party/ply-3.1/example/GardenSnake/GardenSnake.py

NO_INDENT: int = 0
MAY_INDENT: int = 1
MUST_INDENT: int = 2


def track_tokens_filter(lexer: lex.Lexer, tokens: Iterator[lex.LexToken]) -> Iterator[lex.LexToken]:
    lexer.at_line_start = at_line_start = True
    indent: int = NO_INDENT

    for token in tokens:
        token.at_line_start = at_line_start

        if token.type == "COLON":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False
        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False
        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False
        else:
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT
        yield token
        lexer.at_line_start = at_line_start


def _new_token(type: str, lineno: int) -> lex.LexToken:
    tok: lex.LexToken = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = -1
    return tok


def DEDENT(lineno: int) -> lex.LexToken:
    return _new_token("DEDENT", lineno)


def INDENT(lineno: int) -> lex.LexToken:
    return _new_token("INDENT", lineno)


def indentation_filter(tokens: Iterator[lex.LexToken]) -> Iterator[lex.LexToken]:
    levels: List[int] = [0]
    token: Optional[lex.LexToken] = None
    depth: int = 0
    prev_was_ws: bool = False

    for token in tokens:
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            continue
        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                continue
            yield token
            continue

        prev_was_ws = False
        if token.must_indent:
            if not (depth > levels[-1]):
                raise IndentationError("Expected an indented block")
            levels.append(depth)
            yield INDENT(token.lineno)
        elif token.at_line_start:
            if depth == levels[-1]:
                pass
            elif depth > levels[-1]:
                raise IndentationError("Indentation increased but not in new block")
            else:
                try:
                    i: int = levels.index(depth)
                except ValueError:
                    raise IndentationError("Inconsistent indentation")
                for _ in range(i + 1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()
        yield token

    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)


def filter(lexer: lex.Lexer, add_endmarker: bool = True) -> Iterator[lex.LexToken]:
    token: Optional[lex.LexToken] = None
    tokens: Iterator[lex.LexToken] = track_tokens_filter(lexer, iter(lexer.token, None))

    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno)


class IndentLexer(object):
    def __init__(self, debug: int = 0, optimize: int = 0, lextab: str = 'lextab', reflags: int = 0) -> None:
        self.lexer = lex.lex(debug=debug, optimize=optimize, lextab=lextab, reflags=reflags)
        self.token_stream: Optional[peekable[lex.LexToken]] = None
        self.ct = None

    def input(self, s: str, add_endmarker: bool = False) -> None:
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = peekable(filter(self.lexer, add_endmarker))

    def token(self) -> Optional[lex.LexToken]:
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

    def current_token(self) -> Optional[lex.LexToken]:
        try:
            self.ct = self.token_stream.peek()
            return self.token_stream.peek()
        except StopIteration:
            return None
