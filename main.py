from lexer import IndentLexer


def main():
    lexer = IndentLexer()
    with open("Examples/Pong/Vector.ijk", "r") as code:
        lexer.input(code.read())
        while t := lexer.token():
            print(t)


if __name__ == '__main__':
    main()
