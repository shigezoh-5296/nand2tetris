class CompilationEngine:
    def __init__(self, tokenizer, symbol_table, vm_writer):
        self.tokenizer = tokenizer
        self.symbol_table = symbol_table
        self.vm_writer = vm_writer
        self.class_name = None
        self.if_label_cnt = 0
        self.while_label_cnt = 0

    def compile(self):
        self.compile_class()

    def compile_class(self):
        self.expect_token('class')  # class
        self.class_name = self.tokenizer.get_current_token()  # className
        self.tokenizer.advance()
        self.expect_token('{')  # {

        while self.tokenizer.has_more_tokens():
            if self.tokenizer.get_current_token() in ['static', 'field']:
                self.compile_class_var_dec()
            elif self.tokenizer.get_current_token() in ['constructor', 'function', 'method']:
                self.compile_subroutine()
            elif self.tokenizer.get_current_token() == '}':
                break
            else:
                raise ValueError(f'Unexpected token: {self.tokenizer.get_current_token()}')

        self.expect_token('}')  # }

    def compile_class_var_dec(self):
        kind = self.tokenizer.get_current_token()  # static or field
        self.tokenizer.advance()
        variable_type = self.tokenizer.get_current_token()  # type
        self.tokenizer.advance()
        name = self.tokenizer.get_current_token()  # varName
        self.symbol_table.define(name, variable_type, kind)
        self.tokenizer.advance()
        while self.tokenizer.get_current_token() != ';':
            self.expect_token(',')  # ,
            name = self.tokenizer.get_current_token()  # varName
            self.symbol_table.define(name, variable_type, kind)
            self.tokenizer.advance()

        self.expect_token(';')  # ;

    def compile_subroutine(self):
        self.symbol_table.start_subroutine()

        subroutine_type = self.tokenizer.get_current_token()  # constructor, function, or method
        self.tokenizer.advance()
        self.tokenizer.advance()  # returnType (void or type)
        subroutine_name = self.tokenizer.get_current_token()
        self.tokenizer.advance()

        if subroutine_type == 'method':
            self.symbol_table.define('this', self.class_name, 'argument')
        self.compile_parameter_list()
        self.expect_token('{')  # {
        self.compile_var_dec()
        num_locals = self.symbol_table.var_count('var')
        self.vm_writer.write_function(f'{self.class_name}.{subroutine_name}', num_locals)
        if subroutine_type == 'constructor':
            num_fields = self.symbol_table.var_count('field')
            self.vm_writer.write_push('constant', num_fields)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('pointer', 0)  # this
        elif subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)  # this
        elif subroutine_type == 'function':
            pass
        else:
            raise ValueError(f'Unexpected subroutine type: {subroutine_type}')

        self.compile_statements()

        self.expect_token('}')  # }

    def compile_parameter_list(self):
        self.expect_token('(')  # (
        if self.tokenizer.get_current_token() != ')':
            variable_type = self.tokenizer.get_current_token()
            self.tokenizer.advance()
            name = self.tokenizer.get_current_token()
            self.symbol_table.define(name, variable_type, 'argument')
            self.tokenizer.advance()
            while self.tokenizer.get_current_token() != ')':
                self.expect_token(',')  # ,
                variable_type = self.tokenizer.get_current_token()
                self.tokenizer.advance()
                name = self.tokenizer.get_current_token()
                self.symbol_table.define(name, variable_type, 'argument')
                self.tokenizer.advance()
        self.expect_token(')')  # )

    def compile_var_dec(self):
        if self.tokenizer.get_current_token() != 'var':
            print("No variable declaration found.")
            return

        while self.tokenizer.get_current_token() == 'var':
            self.expect_token('var')  # var
            variable_type = self.tokenizer.get_current_token()
            self.tokenizer.advance()
            name = self.tokenizer.get_current_token()
            self.symbol_table.define(name, variable_type, 'var')
            print(f"Defining variable: {name}, type: {variable_type}, kind: 'var'")
            self.tokenizer.advance()
            while self.tokenizer.get_current_token() == ',':
                self.expect_token(',')  # ,
                name = self.tokenizer.get_current_token()
                self.symbol_table.define(name, variable_type, 'var')
                print(f"Defining variable: {name}, type: {variable_type}, kind: 'var'")
                self.tokenizer.advance()
            self.expect_token(';')  # ;

    def compile_statements(self):
        while self.tokenizer.has_more_tokens():
            token = self.tokenizer.get_current_token()
            if token == 'let':
                self.compile_let()
            elif token == 'if':
                self.compile_if()
            elif token == 'while':
                self.compile_while()
            elif token == 'do':
                self.compile_do()
            elif token == 'return':
                self.compile_return()
            else:
                break

    def compile_let(self):
        self.expect_token('let')  # let
        var_name = self.tokenizer.get_current_token()
        var_kind = self.symbol_table.kind_of(var_name)
        var_index = self.symbol_table.index_of(var_name)
        segment = self.convert_var_kind(var_kind)  # 変換関数を使用
        self.tokenizer.advance()
        if self.tokenizer.get_current_token() == '[':
            self.expect_token('[')  # [
            self.compile_expression()
            self.expect_token(']')  # ]
            self.vm_writer.write_push(segment, var_index)
            self.vm_writer.write_arithmetic('add')
            self.expect_token('=')  # =
            self.compile_expression()
            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            self.expect_token('=')  # =
            self.compile_expression()
            self.vm_writer.write_pop(segment, var_index)
        self.expect_token(';')  # ;

    def compile_if(self):
        """
        # ifのケース
            if-goto IF_TRUE0
            goto IF_FALSE0
            label IF_TRUE0
            (条件Trueの場合の処理)
            label IF_FALSE0

        # if-elseのケース
            (条件)
            if-goto IF_TRUE1
            goto IF_FALSE1
            label IF_TRUE1
            (条件Trueの場合の処理)
            goto IF_END1
            label IF_FALSE1
            (条件Falseの場合の処理)
            label IF_END1
        """
        local_if_label_cnt = self.if_label_cnt
        self.if_label_cnt += 1

        self.expect_token('if')
        self.expect_token('(')
        self.compile_expression()
        self.expect_token(')')
        self.expect_token('{')
        self.vm_writer.write_if(f'IF_TRUE{local_if_label_cnt}')
        self.vm_writer.write_goto(f'IF_FALSE{local_if_label_cnt}')
        self.vm_writer.write_label(f'IF_TRUE{local_if_label_cnt}')
        self.compile_statements()
        self.expect_token('}')
        if self.tokenizer.get_current_token() == 'else':
            self.vm_writer.write_goto(f'IF_END{local_if_label_cnt}')
            self.vm_writer.write_label(f'IF_FALSE{local_if_label_cnt}')
            self.expect_token('else')
            self.expect_token('{')
            self.compile_statements()
            self.expect_token('}')
            self.vm_writer.write_label(f'IF_END{local_if_label_cnt}')
        else:
            self.vm_writer.write_label(f'IF_FALSE{local_if_label_cnt}')

    def compile_while(self):
        """
        label WHILE_EXP0
        (条件)
        if-goto WHILE_TRUE0
        goto WHILE_FALSE0
        label WHILE_TRUE0
        (条件Trueの場合の処理)
        goto WHILE_EXP0
        label WHILE_FALSE0
        """
        # ↑サンプルコード(条件を反転させることでラベルを減らしている)とは異なっているが、これでも問題ないはず
        local_while_label_cnt = self.while_label_cnt
        self.while_label_cnt += 1

        self.expect_token('while')
        self.expect_token('(')
        self.vm_writer.write_label(f'WHILE_EXP{local_while_label_cnt}')
        self.compile_expression()
        self.expect_token(')')
        self.vm_writer.write_if(f'WHILE_TRUE{local_while_label_cnt}')
        self.vm_writer.write_goto(f'WHILE_FALSE{local_while_label_cnt}')
        self.vm_writer.write_label(f'WHILE_TRUE{local_while_label_cnt}')
        self.expect_token('{')
        self.compile_statements()
        self.expect_token('}')
        self.vm_writer.write_goto(f'WHILE_EXP{local_while_label_cnt}')
        self.vm_writer.write_label(f'WHILE_FALSE{local_while_label_cnt}')

    def compile_do(self):
        self.expect_token('do')
        self.compile_subroutine_call()
        self.vm_writer.write_pop('temp', 0)
        self.expect_token(';')

    def compile_return(self):
        """
        # 戻り値なしの場合
            push constant 0
            return
        # 戻り値ありの場合
            (式)
            return
        """
        self.expect_token('return')
        if self.tokenizer.get_current_token() == ';':
            self.vm_writer.write_push('constant', 0)
        else:
            self.compile_expression()
        self.vm_writer.write_return()
        self.expect_token(';')

    def compile_expression(self):
        """
        # 式の構文解析
        # term (op term)*
        """
        self.compile_term()
        while self.tokenizer.get_current_token() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            op = self.tokenizer.get_current_token()
            self.tokenizer.advance()
            self.compile_term()
            if op == '+':
                self.vm_writer.write_arithmetic('add')
            elif op == '-':
                self.vm_writer.write_arithmetic('sub')
            elif op == '*':
                self.vm_writer.write_call('Math.multiply', 2)
            elif op == '/':
                self.vm_writer.write_call('Math.divide', 2)
            elif op == '&':
                self.vm_writer.write_arithmetic('and')
            elif op == '|':
                self.vm_writer.write_arithmetic('or')
            elif op == '<':
                self.vm_writer.write_arithmetic('lt')
            elif op == '>':
                self.vm_writer.write_arithmetic('gt')
            elif op == '=':
                self.vm_writer.write_arithmetic('eq')

    def compile_term(self):
        """
        # termの構文解析
        ・integerConstant
        ・stringConstant
        ・keywordConstant (true, false, null, this)
        ・varName
        ・varName[expression]
        ・subroutineCall
        ・(expression)
        ・unaryOp term
        """
        current_token_type = self.tokenizer.token_type()  # ローカル変数に代入

        if current_token_type == 'INT_CONST':
            # 整数定数
            self.vm_writer.write_push('constant', self.tokenizer.int_val())
            self.tokenizer.advance()

        elif current_token_type == 'STRING_CONST':
            # 文字列定数
            string_value = self.tokenizer.string_val()
            self.vm_writer.write_push('constant', len(string_value))
            self.vm_writer.write_call('String.new', 1)
            for char in string_value:
                self.vm_writer.write_push('constant', ord(char))
                self.vm_writer.write_call('String.appendChar', 2)
            self.tokenizer.advance()

        elif current_token_type == 'KEYWORD':
            # キーワード定数
            keyword = self.tokenizer.keyword()
            if keyword == 'true':
                self.vm_writer.write_push('constant', 1)
                self.vm_writer.write_arithmetic('neg')
            elif keyword in ['false', 'null']:
                self.vm_writer.write_push('constant', 0)
            elif keyword == 'this':
                self.vm_writer.write_push('pointer', 0)
            else:
                raise ValueError(f'Unexpected keyword: {keyword}')
            self.tokenizer.advance()

        elif current_token_type == 'IDENTIFIER':
            # 識別子 (varName, varName[expression], subroutineCall)
            identifier = self.tokenizer.get_current_token()
            self.tokenizer.advance()  # 識別子の次のトークンに進める

            # 次のトークンを確認するために先読み（get_current_tokenは状態を変えない）
            next_token = self.tokenizer.get_current_token()

            if next_token == '[':
                # varName[expression]
                var_kind = self.symbol_table.kind_of(identifier)
                var_index = self.symbol_table.index_of(identifier)
                segment = self.convert_var_kind(var_kind)
                self.vm_writer.write_push(segment, var_index)
                self.expect_token('[')
                self.compile_expression()
                self.expect_token(']')
                self.vm_writer.write_arithmetic('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)

            elif next_token in ['(', '.']:
                # subroutineCall
                # compile_subroutine_call が識別子から処理を始める必要があるため、
                # 一つ前に戻す（tokenizer.advance() を取り消す）
                self.tokenizer.retreat()
                self.compile_subroutine_call()

            else:
                # varName (識別子の後に他のトークンが続く場合、またはファイルの終端)
                var_kind = self.symbol_table.kind_of(identifier)
                var_index = self.symbol_table.index_of(identifier)
                segment = self.convert_var_kind(var_kind)
                self.vm_writer.write_push(segment, var_index)
                # ここでは tokenizer.advance() は不要（識別子の処理は完了）

        elif current_token_type == 'SYMBOL':
            # (expression) または 単項演算子
            symbol = self.tokenizer.symbol()  # symbol もローカル変数に
            if symbol == '(':
                # (expression)
                self.expect_token('(')
                self.compile_expression()
                self.expect_token(')')
            elif symbol in ['-', '~']:
                # 単項演算子
                unary_op = symbol
                self.tokenizer.advance()  # 単項演算子を消費
                self.compile_term()  # 後続の term をコンパイル
                if unary_op == '-':
                    self.vm_writer.write_arithmetic('neg')
                elif unary_op == '~':
                    self.vm_writer.write_arithmetic('not')
                # else: # ここでのエラーチェックは不要 (elif でチェック済み)
                #     raise ValueError(f'Unexpected unary operator: {unary_op}')
            else:
                raise ValueError(f'Unexpected symbol: {symbol}')

        else:
            raise ValueError(f'Unexpected token type: {current_token_type}')

    def compile_subroutine_call(self):
        """
        # subroutineCallの構文解析
        # subroutineName '(' expressionList ')'
        # className '.' subroutineName '(' expressionList ')'
        # varName '.' subroutineName '(' expressionList ')'
        """
        first_token = self.tokenizer.get_current_token()
        self.tokenizer.advance()
        if self.tokenizer.get_current_token() == '(':
            # subroutineName '(' expressionList ')' -> 現在のオブジェクトに対するメソッド呼び出し
            subroutine_name = first_token
            # メソッド呼び出しの引数の前に 'this' ポインタ (pointer 0) をプッシュ
            self.vm_writer.write_push('pointer', 0)
            num_args = self.compile_expression_list()
            # 'this' のために num_args + 1 でメソッドを呼び出す
            self.vm_writer.write_call(f'{self.class_name}.{subroutine_name}', num_args + 1)  # 'this' のために 1 を追加
        elif self.tokenizer.get_current_token() == '.':
            # className '.' subroutineName '(' expressionList ')' または
            # varName '.' subroutineName '(' expressionList ')'
            self.expect_token('.')
            identifier = first_token  # className または varName
            subroutine_name = self.tokenizer.get_current_token()
            self.tokenizer.advance()

            # className と varName を区別
            if self.symbol_table.kind_of(identifier) is None:
                # className の場合 (静的/コンストラクタ呼び出し)
                class_name = identifier
                num_args = self.compile_expression_list()
                self.vm_writer.write_call(f'{class_name}.{subroutine_name}', num_args)  # 'this' は不要
            else:
                # varName の場合 (オブジェクトに対するメソッド呼び出し)
                var_kind = self.symbol_table.kind_of(identifier)
                var_index = self.symbol_table.index_of(identifier)
                segment = self.convert_var_kind(var_kind)
                # 引数の前にオブジェクトのアドレス (varName) をプッシュ
                self.vm_writer.write_push(segment, var_index)
                num_args = self.compile_expression_list()
                # プッシュされたオブジェクトのアドレスのために num_args + 1 でメソッドを呼び出す
                self.vm_writer.write_call(f'{self.symbol_table.type_of(identifier)}.{subroutine_name}', num_args + 1)  # 'this' のために 1 を追加
        else:
            raise ValueError(f'Unexpected token: {self.tokenizer.get_current_token()}')

    def compile_expression_list(self):
        """
        # 式リストの構文解析
        # (expression (',' expression)*)
        """
        num_args = 0
        self.expect_token('(')
        while self.tokenizer.get_current_token() != ')':
            self.compile_expression()
            num_args += 1
            if self.tokenizer.get_current_token() == ',':
                self.expect_token(',')
        self.expect_token(')')
        return num_args

    def expect_token(self, expected_token):
        """
        現在のトークンが期待されるトークンと一致するか確認し、一致していればトークンを進める。
        一致しない場合はエラーをスローする。
        """
        if self.tokenizer.get_current_token() == expected_token:
            self.tokenizer.advance()
        else:
            raise ValueError(f"Expected '{expected_token}', but found '{self.tokenizer.get_current_token()}'")

    def convert_var_kind(self, var_kind):
        """
        var_kind を適切な VM セグメント名に変換する関数。
        """
        kind_map = {
            'field': 'this',
            'var': 'local',
            'argument': 'argument',
            'static': 'static',
        }
        if var_kind not in kind_map:
            raise ValueError(f"Unexpected var_kind: {var_kind}")
        return kind_map[var_kind]
