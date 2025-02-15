import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.jack_tokenizer import JackTokenizer


def test_div_tokens():
    # テスト用の入力ファイルを作成
    test_input = """// This is a comment
    class Main {
        function void main() {
            var int x; // variable declaration
            let x = 2; /* multi-line
            comment */
            do Output.printInt(x);
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
        'class', 'Main', '{',
        'function', 'void', 'main', '(', ')', '{',
        'var', 'int', 'x', ';',
        'let', 'x', '=', '2', ';',
        'do', 'Output', '.', 'printInt', '(', 'x', ')', ';',
        'return', ';',
        '}',
        '}'
    ]

    # トークンが期待されるものと一致するか確認
    assert expected_tokens == tokens

    # テスト用の入力ファイルを削除
    # import os
    # os.remove('test_input.jack')


if __name__ == "__main__":
    pytest.main()
