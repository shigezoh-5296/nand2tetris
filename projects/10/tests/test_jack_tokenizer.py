import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.jack_tokenizer import JackTokenizer


def test_split_line():
    with open('test_input.jack', 'w') as f:
        f.write("")
    # JackTokenizerを初期化
    tokenizer = JackTokenizer('test_input.jack')
    # split_lineメソッドのテスト
    line = 'let str = "Hello, World!";'
    tokens = tokenizer.split_line(line)
    expected_tokens = ['let', 'str', '=', '"Hello, World!";']
    assert tokens == expected_tokens
    line = 'let x = 2;'
    tokens = tokenizer.split_line(line)
    expected_tokens = ['let', 'x', '=', '2;']
    assert tokens == expected_tokens
    line = 'do Output.printInt(x);'
    tokens = tokenizer.split_line(line)
    expected_tokens = ['do', 'Output.printInt(x);']
    assert tokens == expected_tokens
    line = 'let str = "Hello,World!";' 
    tokens = tokenizer.split_line(line)
    expected_tokens = ['let', 'str', '=', '"Hello,World!";']
    assert tokens == expected_tokens
    line = 'let str = "Hello,  World!";' 
    tokens = tokenizer.split_line(line)
    expected_tokens = ['let', 'str', '=', '"Hello,  World!";']
    assert tokens == expected_tokens


def test_split_symbols():
    with open('test_input.jack', 'w') as f:
        f.write("")
    # JackTokenizer
    tokenizer = JackTokenizer('test_input.jack')
    # split_symbolsメソッドのテスト
    temp_tokens = ['let', 'str', '=', '"Hello, World!";']
    tokens = tokenizer.split_symbols(temp_tokens)
    expected_tokens = ['let', 'str', '=', '"Hello, World!"', ';']
    assert tokens == expected_tokens
    temp_tokens = ['let', 'str="Hello, World!";']
    tokens = tokenizer.split_symbols(temp_tokens)
    expected_tokens = ['let', 'str', '=', '"Hello, World!"', ';']
    assert tokens == expected_tokens


def test_div_tokens():
    # テスト用の入力ファイルを作成
    test_input = """// This is a comment
    class Main {
        function void main() {
            var int x; // variable declaration
            var String str; // variable declaration
            let x = 2; /* multi-line
            comment */
            let str = "Hello, World!"; // string literal
            do Output.printInt(x);
            do Output.printString(str);
            return;
        }
    }
    """
    with open('test_input.jack', 'w') as f:
        f.write(test_input)
    # JackTokenizerを初期化
    tokenizer = JackTokenizer('test_input.jack')
    tokens = tokenizer.get_tokens()

    # 期待されるトークンのリスト
    expected_tokens = [
        'class', 'Main', '{', 'function', 'void', 'main', '(', ')', '{',
        'var', 'int', 'x', ';', 'var', 'String', 'str', ';', 'let', 'x',
        '=', '2', ';', 'let', 'str', '=', '"Hello, World!"', ';', 'do',
        'Output', '.', 'printInt', '(', 'x', ')', ';', 'do', 'Output', '.',
        'printString', '(', 'str', ')', ';', 'return', ';', '}', '}'
    ]

    # トークンが期待されるものと一致するか確認
    assert expected_tokens == tokens

    # テスト用の入力ファイルを削除
    # import os
    # os.remove('test_input.jack')


if __name__ == "__main__":
    pytest.main()
