class CompilationEngine:
    def __init__(self, tokenizer, output_file):
        self.tokenizer = tokenizer
        self.output_file = output_file
        self.indentation = 0

    def compile(self):
        self.compile_class()

    def compile_class(self):
        self.write('<class>')
        self.indentation += 1

        self.write_token()  # 'class'
        self.write_token()  # className
        self.write_token()  # '{'

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() in ['static', 'field']:
                self.compile_class_var_dec()
            elif self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() in ['constructor', 'function', 'method']:
                self.compile_subroutine()
            elif self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '}':
                break
            else:
                # 想定外のケース
                print(f'Unexpected token: {self.tokenizer.tokens[self.tokenizer.current_token_index]}')
                self.tokenizer.advance

        self.write_token()  # '}'

        self.indentation -= 1
        self.write('</class>')

    def compile_class_var_dec(self):
        self.write('<classVarDec>')
        self.indentation += 1

        self.write_token()  # 'static' or 'field'
        self.write_token()  # type
        self.write_token()  # varName

        while self.tokenizer.symbol() != ';':
            self.write_token()  # ',' or varName

        self.write_token()  # ';'

        self.indentation -= 1
        self.write('</classVarDec>')

    def compile_subroutine(self):
        self.write('<subroutineDec>')
        self.indentation += 1

        self.write_token()  # 'constructor', 'function', or 'method'
        self.write_token()  # 'void' or type
        self.write_token()  # subroutineName
        self.write_token()  # '('

        self.compile_parameter_list()

        self.write_token()  # ')'

        self.write('<subroutineBody>')
        self.indentation += 1

        self.write_token()  # '{'

        while self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() == 'var':
            self.compile_var_dec()

        self.compile_statements()

        self.write_token()  # '}'

        self.indentation -= 1
        self.write('</subroutineBody>')

        self.indentation -= 1
        self.write('</subroutineDec>')

    def compile_parameter_list(self):
        self.write('<parameterList>')
        self.indentation += 1

        while self.tokenizer.symbol() != ')':
            self.write_token()

        self.indentation -= 1
        self.write('</parameterList>')

    def compile_var_dec(self):
        self.write('<varDec>')
        self.indentation += 1

        self.write_token()  # 'var'
        self.write_token()  # type
        self.write_token()  # varName

        while self.tokenizer.symbol() != ';':
            self.write_token()  # ',' or varName

        self.write_token()  # ';'

        self.indentation -= 1
        self.write('</varDec>')

    def compile_statements(self):
        self.write('<statements>')
        self.indentation += 1

        while self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() in ['let', 'if', 'while', 'do', 'return']:
            if self.tokenizer.keyword() == 'let':
                self.compile_let()
            elif self.tokenizer.keyword() == 'if':
                self.compile_if()
            elif self.tokenizer.keyword() == 'while':
                self.compile_while()
            elif self.tokenizer.keyword() == 'do':
                self.compile_do()
            elif self.tokenizer.keyword() == 'return':
                self.compile_return()

        self.indentation -= 1
        self.write('</statements>')

    def compile_let(self):
        self.write('<letStatement>')
        self.indentation += 1

        self.write_token()  # 'let'
        self.write_token()  # varName

        if self.tokenizer.symbol() == '[':
            self.write_token()  # '['
            self.compile_expression()
            self.write_token()  # ']'

        self.write_token()  # '='
        self.compile_expression()
        self.write_token()  # ';'

        self.indentation -= 1
        self.write('</letStatement>')

    def compile_if(self):
        self.write('<ifStatement>')
        self.indentation += 1

        self.write_token()  # 'if'
        self.write_token()  # '('
        self.compile_expression()
        self.write_token()  # ')'
        self.write_token()  # '{'
        self.compile_statements()
        self.write_token()  # '}'

        if self.tokenizer.token_type() == 'KEYWORD' and self.tokenizer.keyword() == 'else':
            self.write_token()  # 'else'
            self.write_token()  # '{'
            self.compile_statements()
            self.write_token()  # '}'

        self.indentation -= 1
        self.write('</ifStatement>')

    def compile_while(self):
        self.write('<whileStatement>')
        self.indentation += 1

        self.write_token()  # 'while'
        self.write_token()  # '('
        self.compile_expression()
        self.write_token()  # ')'
        self.write_token()  # '{'
        self.compile_statements()
        self.write_token()  # '}'

        self.indentation -= 1
        self.write('</whileStatement>')

    def compile_do(self):
        self.write('<doStatement>')
        self.indentation += 1

        self.write_token()  # 'do'
        self.compile_subroutine_call()
        self.write_token()  # ';'

        self.indentation -= 1
        self.write('</doStatement>')

    def compile_return(self):
        self.write('<returnStatement>')
        self.indentation += 1

        self.write_token()  # 'return'

        if self.tokenizer.token_type() != 'SYMBOL' or self.tokenizer.symbol() != ';':
            self.compile_expression()

        self.write_token()  # ';'

        self.indentation -= 1
        self.write('</returnStatement>')

    def compile_expression(self):
        self.write('<expression>')
        self.indentation += 1

        self.compile_term()

        while self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.write_token()  # op
            self.compile_term()

        self.indentation -= 1
        self.write('</expression>')

    def compile_term(self):
        self.write('<term>')
        self.indentation += 1

        if self.tokenizer.token_type() == 'INT_CONST':
            self.write_token()  # intVal
        elif self.tokenizer.token_type() == 'STRING_CONST':
            self.write_token()  # stringVal
        elif self.tokenizer.token_type() == 'KEYWORD':
            self.write_token()  # keywordConstant
        elif self.tokenizer.token_type() == 'IDENTIFIER':
            self.tokenizer.advance()
            if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '[':
                self.tokenizer.retreat()
                self.write_token()  # varName
                self.write_token()  # '['
                self.compile_expression()
                self.write_token()  # ']'
            elif self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '(':
                self.tokenizer.retreat()
                self.compile_subroutine_call()
            elif self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '.':
                self.tokenizer.retreat()
                self.compile_subroutine_call()
            else:
                self.tokenizer.retreat()
                self.write_token()  # varName
        elif self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() in ['(', '-', '~']:
            self.write_token()  # '(' or unaryOp
            self.compile_term()

        self.indentation -= 1
        self.write('</term>')

    def compile_subroutine_call(self):
        self.write_token()  # subroutineName or className or varName
        if self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == '.':
            self.write_token()  # '.'
            self.write_token()  # subroutineName
        self.write_token()  # '('
        self.compile_expression_list()
        self.write_token()  # ')'

    def compile_expression_list(self):
        self.write('<expressionList>')
        self.indentation += 1

        if self.tokenizer.token_type() != 'SYMBOL' or self.tokenizer.symbol() != ')':
            self.compile_expression()
            while self.tokenizer.token_type() == 'SYMBOL' and self.tokenizer.symbol() == ',':
                self.write_token()  # ','
                self.compile_expression()

        self.indentation -= 1
        self.write('</expressionList>')

    def write_token(self):
        token_type = self.tokenizer.token_type()
        if token_type == 'KEYWORD':
            self.write(f'<keyword> {self.tokenizer.keyword()} </keyword>')
        elif token_type == 'SYMBOL':
            symbol = self.tokenizer.symbol()
            if symbol == '<':
                symbol = '&lt;'
            elif symbol == '>':
                symbol = '&gt;'
            elif symbol == '&':
                symbol = '&amp;'
            self.write(f'<symbol> {symbol} </symbol>')
        elif token_type == 'IDENTIFIER':
            self.write(f'<identifier> {self.tokenizer.identifier()} </identifier>')
        elif token_type == 'INT_CONST':
            self.write(f'<integerConstant> {self.tokenizer.int_val()} </integerConstant>')
        elif token_type == 'STRING_CONST':
            self.write(f'<stringConstant> {self.tokenizer.string_val()} </stringConstant>')
        self.tokenizer.advance()

    def write(self, content):
        self.output_file.write('  ' * self.indentation + content + '\n')
