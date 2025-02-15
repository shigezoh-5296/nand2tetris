class JackTokenizer:
    def __init__(self, filePath):
        self.tokens = self.div_tokens(filePath)
        self.current_token_index = 0

    def symbol_list(self):
        return ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*',
                '/', '&', '|', '<', '>', '=', '~']

    def div_tokens(self, filePath):
        file = open(filePath, 'r')
        lines = file.readlines()
        file.close()
        in_comment = False
        temp_tokens = []
        tokens = []

        # コメント削除してトークンに分割
        for line in lines:
            line = line.strip()
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
            if line:
                temp_tokens.extend(line.split())

        # シンボルを1つのトークンにする
        for token in temp_tokens:
            start = 0
            while start < len(token):
                if token[start] in self.symbol_list():
                    tokens.append(token[start])
                    start += 1
                else:
                    end = start
                    while end < len(token) and token[end] not in self.symbol_list():
                        end += 1
                    tokens.append(token[start:end])
                    start = end

        return tokens

    def get_tokens(self):
        return self.tokens

    def has_more_tokens(self):
        return self.current_token_index < len(self.tokens)

    def advance(self):
        self.current_token_index += 1