class JackTokenizer:
    def __init__(self, filePath):
        self.tokens = self.div_tokens(filePath)
        self.current_token_index = 0

    def symbol_list(self):
        return ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                '/', '&', '|', '<', '>', '=', '~']

    def keyword_list(self):
        return ['class', 'constructor', 'function', 'method', 'field', 'static',
                'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null',
                'this', 'let', 'do', 'if', 'else', 'while', 'return']

    def div_tokens(self, filePath):
        file = open(filePath, 'r')
        lines_org = file.readlines()
        file.close()
        temp_tokens = []
        tokens = []

        # コメント削除
        lines_no_comment = self.remove_comments(lines_org)

        # 空白でトークンに分割
        temp_tokens = self.split_lines(lines_no_comment)

        # シンボルを1つのトークンに分割
        tokens = self.split_symbols(temp_tokens)

        return tokens

    def remove_comments(self, _lines):
        in_comment = False
        lines = []

        for line in _lines:
            if '*/' in line:
                in_comment = False
                line = line.split('*/')[1]
            if in_comment:  # コメント内ならスキップ
                continue
            if not line:  # 空行をスキップ
                continue
            if line.startswith('//'):  # コメント行をスキップ
                continue
            if '/*' in line:
                in_comment = True
                line = line.split('/*')[0]
            line = line.split('//')[0]  # 行中のコメントを削除
            line = line.strip()
            if line:
                lines.append(line)
        return lines

    def split_lines(self, lines):
        tokens = []
        for line in lines:
            tokens.extend(self.split_line(line))
        return tokens

    def split_line(self, line):
        tokens = []
        current_token = []
        in_string = False

        for char in line:
            if char == '"':
                in_string = not in_string
                current_token.append(char)
            elif char == ' ' and not in_string:
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
            else:
                current_token.append(char)
        if current_token:
            tokens.append(''.join(current_token))
        return tokens

    def split_symbols(self, _tokens):
        tokens = []
        current_token = []
        in_string = False
        for token in _tokens:
            for char in token:
                if char == '"':
                    in_string = not in_string
                    current_token.append(char)
                elif char in self.symbol_list() and not in_string:
                    if current_token:
                        tokens.append(''.join(current_token))
                        current_token = []
                    tokens.append(char)
                else:
                    current_token.append(char)
            if current_token:
                tokens.append(''.join(current_token))
                current_token = []
        return tokens

    def get_tokens(self):
        return self.tokens

    def has_more_tokens(self):
        return self.current_token_index < len(self.tokens)

    def advance(self):
        self.current_token_index += 1

    def token_type(self):
        token = self.tokens[self.current_token_index]
        if token in self.keyword_list():
            return 'KEYWORD'
        elif token in self.symbol_list():
            return 'SYMBOL'
        elif token.isdigit():
            return 'INT_CONST'
        elif token.startswith('"') and token.endswith('"'):
            return 'STRING_CONST'
        else:
            return 'IDENTIFIER'

    def keyword(self):
        return self.tokens[self.current_token_index]

    def symbol(self):
        return self.tokens[self.current_token_index]

    def identifier(self):
        return self.tokens[self.current_token_index]

    def int_val(self):
        return int(self.tokens[self.current_token_index])

    def string_val(self):
        return self.tokens[self.current_token_index][1:-1]

    def output_xml(self, filePath):
        file = open(filePath, 'w')
        file.write('<tokens>\n')
        while self.has_more_tokens():
            token_type = self.token_type()
            if token_type == 'KEYWORD':
                file.write(f'<keyword> {self.keyword()} </keyword>\n')
            elif token_type == 'SYMBOL':
                if self.symbol() == '<':
                    file.write('<symbol> &lt; </symbol>\n')
                elif self.symbol() == '>':
                    file.write('<symbol> &gt; </symbol>\n')
                elif self.symbol() == '&':
                    file.write('<symbol> &amp; </symbol>\n')
                else:
                    file.write(f'<symbol> {self.symbol()} </symbol>\n')
            elif token_type == 'IDENTIFIER':
                file.write(f'<identifier> {self.identifier()} </identifier>\n')
            elif token_type == 'INT_CONST':
                file.write(f'<integerConstant> {self.int_val()} </integerConstant>\n')
            elif token_type == 'STRING_CONST':
                file.write(f'<stringConstant> {self.string_val()} </stringConstant>\n')
            self.advance()
        file.write('</tokens>\n')
        file.close()
