from minipar.lexer import LexerImpl

if __name__ == '__main__':
    path_to_source = './examples/minipar/ex9.minipar'

    with open(path_to_source, 'r', encoding='utf-8') as f:
        source = f.read()
        lexer = LexerImpl(source)
        lexer_generator = lexer.scan()

        keep_going = True
        i = 0
        while keep_going:
            try:
                lookahead, line = next(lexer_generator)
                print(f'{line}: {lookahead}')
            except StopIteration:
                keep_going = False
