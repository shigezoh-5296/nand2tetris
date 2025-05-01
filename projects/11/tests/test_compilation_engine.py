import pytest
from unittest.mock import MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))


@pytest.fixture
def setup_engine():
    tokenizer = MagicMock()
    symbol_table = MagicMock()
    vm_writer = MagicMock()
    from src.compilation_engine import CompilationEngine
    engine = CompilationEngine(tokenizer, symbol_table, vm_writer)

    # トークンのリスト定義
    token_list = []

    # tokenizer.get_current_token()は現トークンを返すのみ
    def get_current_token_side_effect():
        return token_list[0] if token_list else None

    tokenizer.get_current_token.side_effect = get_current_token_side_effect

    # tokenizer.advance()は現トークンを一つ進める
    def advance_side_effect():
        if token_list:
            token_list.pop(0)

    tokenizer.advance.side_effect = advance_side_effect

    return engine, tokenizer, symbol_table, vm_writer, token_list


def test_compile_class(setup_engine):
    engine, tokenizer, symbol_table, _, token_list = setup_engine

    # トークンのリスト定義
    token_list.extend([
        'class', 'MyClass', '{', 'static', 'int', 'x', ';', 'field', 'boolean', 'y', ';', '}', None
    ])

    engine.compile_class()

    assert engine.class_name == 'MyClass'
    symbol_table.define.assert_any_call('x', 'int', 'static')
    symbol_table.define.assert_any_call('y', 'boolean', 'field')


def test_compile_class_var_dec(setup_engine):
    engine, tokenizer, symbol_table, _, token_list = setup_engine

    # テストケース１：Static変数宣言(2つの変数)
    token_list.extend([
        'static', 'int', 'x', ',', 'y', ';', 'dummy'
    ])

    engine.compile_class_var_dec()

    symbol_table.define.assert_any_call('x', 'int', 'static')
    symbol_table.define.assert_any_call('y', 'int', 'static')
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    symbol_table.reset_mock()

    # テストケース２：Field変数宣言(1つの変数)
    token_list.clear()
    token_list.extend([
        'field', 'int', 'x', ';', 'dummy'
    ])

    engine.compile_class_var_dec()

    symbol_table.define.assert_any_call('x', 'int', 'field')
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_subroutine(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # テストケース１：コンストラクタ
    token_list.extend([
        'constructor', 'MyClass', 'new', '(', ')', '{', '}', 'dummy'
    ])

    engine.class_name = 'MyClass'
    symbol_table.var_count.return_value = 1
    engine.compile_subroutine()

    vm_writer.write_function.assert_any_call('MyClass.new', 1)
    vm_writer.write_push.assert_any_call('constant', 1)
    vm_writer.write_call.assert_any_call('Memory.alloc', 1)
    vm_writer.write_pop.assert_any_call('pointer', 0)
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース２：メソッド
    token_list.clear()
    token_list.extend([
        'method', 'void', 'myMethod', '(', 'int', 'a', ')', '{', '}', 'dummy'
    ])

    engine.class_name = 'MyClass'
    symbol_table.var_count.return_value = 2
    engine.compile_subroutine()

    vm_writer.write_function.assert_any_call('MyClass.myMethod', 2)
    vm_writer.write_push.assert_any_call('argument', 0)
    vm_writer.write_pop.assert_any_call('pointer', 0)
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_parameter_list(setup_engine):
    engine, tokenizer, symbol_table, _, token_list = setup_engine

    # テストケース１：引数なし
    token_list.extend(['(', ')', 'dummy'])

    engine.compile_parameter_list()

    assert tokenizer.get_current_token() == 'dummy'
    symbol_table.define.assert_not_called()

    # 呼び出し履歴を初期化
    symbol_table.reset_mock()

    # テストケース２：引数1つ
    token_list.clear()
    token_list.extend(['(', 'int', 'a', ')', 'dummy'])

    engine.compile_parameter_list()

    symbol_table.define.assert_any_call('a', 'int', 'argument')
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    symbol_table.reset_mock()

    # テストケース３：引数2つ
    token_list.clear()
    token_list.extend(['(', 'int', 'b', ',', 'boolean', 'c', ')', 'dummy'])

    engine.compile_parameter_list()

    symbol_table.define.assert_any_call('b', 'int', 'argument')
    symbol_table.define.assert_any_call('c', 'boolean', 'argument')
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_var_dec(setup_engine):
    engine, tokenizer, symbol_table, _, token_list = setup_engine

    # テストケース１：１行で複数の変数宣言
    token_list.extend([
        'var', 'int', 'a', ',', 'b', ';', 'dummy'
    ])

    engine.compile_var_dec()

    symbol_table.define.assert_any_call('a', 'int', 'var')
    symbol_table.define.assert_any_call('b', 'int', 'var')
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    symbol_table.reset_mock()

    # テストケース２：複数行で複数の変数宣言
    token_list.clear()
    token_list.extend([
        'var', 'boolean', 'c', ',', 'd', ';', 'var', 'int', 'e', ';', 'dummy'
    ])

    engine.compile_var_dec()

    symbol_table.define.assert_any_call('c', 'boolean', 'var')
    symbol_table.define.assert_any_call('d', 'boolean', 'var')
    symbol_table.define.assert_any_call('e', 'int', 'var')
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_let(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression をモック化
    def mock_compile_expression():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_expression = mock_compile_expression

    # テストケース１：変数に定数を代入
    token_list.extend([
        'let', 'a', '=', '5', ';', 'dummy'
    ])

    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 0
    engine.compile_let()

    vm_writer.write_pop.assert_any_call('local', 0)
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース２：配列に定数を代入
    token_list.clear()
    token_list.extend([
        'let', 'a', '[', '5', ']', '=', '10', ';', 'dummy'
    ])

    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 1
    engine.compile_let()

    vm_writer.write_push.assert_any_call('local', 1)
    vm_writer.write_arithmetic.assert_any_call('add')
    vm_writer.write_pop.assert_any_call('temp', 0)
    vm_writer.write_pop.assert_any_call('pointer', 1)
    vm_writer.write_push.assert_any_call('temp', 0)
    vm_writer.write_pop.assert_any_call('that', 0)
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_if(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression をモック化
    def mock_compile_expression():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_expression = mock_compile_expression

    # テストケース１：if文
    token_list.extend([
        'if', '(', 'a', ')', '{', 'let', 'b', '=', '5', ';', '}', 'dummy'
    ])

    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 0
    engine.compile_if()

    vm_writer.write_if.assert_any_call('IF_TRUE0')
    vm_writer.write_goto.assert_any_call('IF_FALSE0')
    vm_writer.write_label.assert_any_call('IF_TRUE0')
    vm_writer.write_label.assert_any_call('IF_FALSE0')
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース２：if-else文
    token_list.clear()
    token_list.extend([
        'if', '(', 'a', ')', '{', 'let', 'b', '=', '5', ';', '}',
        'else', '{', 'let', 'c', '=', '10', ';', '}', 'dummy'
    ])

    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 0
    engine.compile_if()

    vm_writer.write_if.assert_any_call('IF_TRUE1')
    vm_writer.write_goto.assert_any_call('IF_FALSE1')
    vm_writer.write_label.assert_any_call('IF_TRUE1')
    vm_writer.write_goto.assert_any_call('IF_END1')
    vm_writer.write_label.assert_any_call('IF_FALSE1')
    vm_writer.write_label.assert_any_call('IF_END1')
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_while(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression をモック化
    def mock_compile_expression():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_expression = mock_compile_expression

    # テストケース
    token_list.extend([
        'while', '(', 'a', ')', '{', 'let', 'b', '=', '5', ';', '}', 'dummy'
    ])

    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 0
    engine.compile_while()

    vm_writer.write_label.assert_any_call('WHILE_EXP0')
    vm_writer.write_if.assert_any_call('WHILE_TRUE0')
    vm_writer.write_goto.assert_any_call('WHILE_FALSE0')
    vm_writer.write_label.assert_any_call('WHILE_TRUE0')
    vm_writer.write_label.assert_any_call('WHILE_FALSE0')
    assert tokenizer.get_current_token() == 'dummy'


def test_complile_return(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression をモック化
    def mock_compile_expression():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_expression = mock_compile_expression

    # テストケース１：値なし
    token_list.extend(['return', ';', 'dummy'])

    engine.compile_return()

    vm_writer.write_push.assert_any_call('constant', 0)
    vm_writer.write_return.assert_any_call()
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース２：値あり
    token_list.clear()
    token_list.extend(['return', 'a', ';', 'dummy'])

    engine.compile_return()

    vm_writer.write_return.assert_any_call()
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_do(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression_list をモック化 (引数なしの場合 0 を返し、括弧を消費)
    def mock_compile_expression_list():
        engine.expect_token('(')  # '(' を消費
        count = 0
        if tokenizer.get_current_token() != ')':
            # このテストケースでは引数がないので、ここは実行されない想定
            # 必要であれば引数ありのケースも考慮したモックにする
            # engine.compile_expression() # 引数があれば呼ぶ
            # while tokenizer.get_current_token() == ',':
            #     engine.expect_token(',')
            #     engine.compile_expression()
            #     count += 1
            pass
        engine.expect_token(')')  # ')' を消費
        return count

    # compile_expression のモック (引数ありの場合に備える)
    def mock_compile_expression():
        tokenizer.advance()  # 引数トークンを消費

    engine.compile_expression_list = mock_compile_expression_list
    engine.compile_expression = mock_compile_expression

    # テストケース: className.subroutineName()
    token_list.extend([
        'do', 'MyClass', '.', 'myMethod', '(', ')', ';', 'dummy'  # トークンを分割
    ])

    # 'MyClass' が変数ではないことを示す
    symbol_table.kind_of.return_value = None

    engine.compile_do()

    # compile_subroutine_call が className.subroutineName パターンで呼ばれることを期待
    vm_writer.write_call.assert_called_once_with('MyClass.myMethod', 0)
    # compile_do の最後に pop temp 0 が呼ばれることを確認
    vm_writer.write_pop.assert_called_once_with('temp', 0)
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_expression(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_term をモック化
    def mock_compile_term():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_term = mock_compile_term

    # テストケース1 : termが1つ
    token_list.extend([
        'a', 'dummy'
    ])

    engine.compile_expression()

    vm_writer.write_arithmetic.assert_not_called()
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース2 : termが2つ
    token_list.clear()
    token_list.extend([
        'a', '+', 'b', 'dummy'
    ])

    engine.compile_expression()

    vm_writer.write_arithmetic.assert_any_call('add')
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース3 : termが3つ
    token_list.clear()
    token_list.extend([
        'a', '+', 'b', '-', 'c', 'dummy'
    ])

    engine.compile_expression()

    vm_writer.write_arithmetic.assert_any_call('add')
    vm_writer.write_arithmetic.assert_any_call('sub')
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_term_int_const(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンが整数定数の場合
    tokenizer.token_type.return_value = 'INT_CONST'
    tokenizer.int_val.return_value = 123

    engine.compile_term()

    vm_writer.write_push.assert_called_once_with('constant', 123)
    tokenizer.advance.assert_called_once()


def test_compile_term_string_const(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンが文字列定数の場合
    tokenizer.token_type.return_value = 'STRING_CONST'
    tokenizer.string_val.return_value = "hello"

    engine.compile_term()

    vm_writer.write_push.assert_any_call('constant', 5)  # 文字列の長さ
    vm_writer.write_call.assert_any_call('String.new', 1)
    vm_writer.write_push.assert_any_call('constant', ord('h'))
    vm_writer.write_call.assert_any_call('String.appendChar', 2)
    tokenizer.advance.assert_called_once()


def test_compile_term_keyword_const(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンがキーワード定数の場合
    tokenizer.token_type.return_value = 'KEYWORD'
    tokenizer.keyword.return_value = 'true'

    engine.compile_term()

    vm_writer.write_push.assert_called_once_with('constant', 1)
    vm_writer.write_arithmetic.assert_called_once_with('neg')
    tokenizer.advance.assert_called_once()


def test_compile_term_var_name(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンが識別子の場合（変数名）
    tokenizer.token_type.return_value = 'IDENTIFIER'
    tokenizer.get_current_token.return_value = 'myVar'
    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 2

    engine.compile_term()

    vm_writer.write_push.assert_called_once_with('local', 2)
    tokenizer.advance.assert_called_once()


def test_compile_term_var_name_array(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンが配列の場合
    tokenizer.token_type.return_value = 'IDENTIFIER'
    # tokenizer.get_current_token.side_effect は使用しない

    # symbol_table の設定
    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 3

    # 配列アクセスのトークンシーケンスを token_list に設定
    token_list.extend(['myArray', '[', 'index', ']', 'dummy'])

    # compile_expression のモック: 配列インデックスを計算し、トークンを消費
    def mock_compile_expression():
        vm_writer.write_push('constant', 5)  # 配列のインデックスを計算する例
        # compile_expression は 'index' トークンを消費する責任を持つ
        tokenizer.advance()  # 'index' トークンを消費

    engine.compile_expression = mock_compile_expression

    engine.compile_term()

    # アサーション
    vm_writer.write_push.assert_any_call('local', 3)  # 配列ベースアドレス
    vm_writer.write_push.assert_any_call('constant', 5)  # インデックス計算結果
    vm_writer.write_arithmetic.assert_called_once_with('add')
    vm_writer.write_pop.assert_called_once_with('pointer', 1)
    # assert_called_once_with を assert_any_call に変更
    vm_writer.write_push.assert_any_call('that', 0)
    assert tokenizer.get_current_token() == 'dummy'  # 最後のトークンまで進んでいるか確認


def test_compile_term_unary_op(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンシーケンス: '-' term dummy
    token_list.extend(['-', '10', 'dummy'])

    # tokenizer の設定:
    # 最初のトークン '-'
    tokenizer.token_type.side_effect = ['SYMBOL', 'INT_CONST']  # 最初の呼び出しで SYMBOL, 次で INT_CONST
    tokenizer.symbol.return_value = '-'
    # 2番目のトークン '10'
    tokenizer.int_val.return_value = 10

    # engine.compile_term = mock_compile_term # この行を削除

    engine.compile_term()  # 実際の compile_term を呼び出す

    # アサーション:
    # 1. term '10' の処理で write_push('constant', 10) が呼ばれる
    vm_writer.write_push.assert_called_once_with('constant', 10)
    # 2. 単項演算子 '-' の処理で write_arithmetic('neg') が呼ばれる
    vm_writer.write_arithmetic.assert_called_once_with('neg')
    # 3. トークンが '-' と '10' の2つ進むことを確認
    assert tokenizer.advance.call_count == 2
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_term_expression_in_parentheses(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # トークンシーケンス: '(' expression ')' dummy
    token_list.extend(['(', '10', ')', 'dummy'])

    # tokenizer の設定:
    # compile_term の最初の token_type 呼び出しで SYMBOL を返す
    tokenizer.token_type.return_value = 'SYMBOL'
    # compile_term の SYMBOL ブロックで '(' を返すように設定
    tokenizer.symbol.return_value = '('
    # compile_expression 内の compile_term で 10 を返すように設定 (これは compile_expression のモック内で処理)
    # tokenizer.int_val.return_value = 10 # モックで処理するため不要

    # compile_expression のモック: 式の結果をプッシュし、式トークンを消費
    def mock_compile_expression():
        # compile_expression は内部で compile_term を呼び出す想定だが、
        # ここでは簡略化し、式 '10' の結果をプッシュし、トークンを消費する
        vm_writer.write_push('constant', 10)
        tokenizer.advance()  # '10' トークンを消費

    engine.compile_expression = mock_compile_expression

    engine.compile_term()  # 実際の compile_term を呼び出す

    # アサーション:
    # 1. expect_token('(') で '(' が消費される -> advance が呼ばれる
    # 2. mock_compile_expression で '10' が消費される -> advance が呼ばれる
    # 3. expect_token(')') で ')' が消費される -> advance が呼ばれる
    assert tokenizer.advance.call_count == 3
    # 括弧内の式のコンパイル結果がプッシュされる
    vm_writer.write_push.assert_called_once_with('constant', 10)
    # 最後のトークンまで進んでいるか確認
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_subroutine_call(setup_engine):
    engine, tokenizer, symbol_table, vm_writer, token_list = setup_engine

    # compile_expression_list をモック化し、引数の数を返し、トークンを消費するように設定
    def mock_compile_expression_list():
        count = 0
        # compile_expression_list が呼ばれるのは '(' の後
        # 次のトークンが ')' でなければ引数リストが始まる
        if tokenizer.get_current_token() != ')':
            count = 1
            engine.compile_expression()  # 最初の引数をコンパイル (モック内で advance が呼ばれる想定)
            # ',' が続く限り引数を処理
            while tokenizer.get_current_token() == ',':
                engine.expect_token(',')  # ',' を消費
                count += 1
                engine.compile_expression()  # 次の引数をコンパイル
        return count

    # compile_expression のモックも定義 (引数トークンを消費するため)
    def mock_compile_expression():
        tokenizer.advance()  # 引数トークンを消費

    engine.compile_expression_list = mock_compile_expression_list
    engine.compile_expression = mock_compile_expression  # compile_expression_list内で使うため設定
    engine.class_name = 'CurrentClass'  # 現在のクラス名を設定

    # --- テストケース1: subroutineName '(' expressionList ')' ---
    token_list.extend(['myMethod', '(', 'arg1', ',', 'arg2', ')', 'dummy'])

    engine.compile_subroutine_call()

    # アサーション
    vm_writer.write_push.assert_called_once_with('pointer', 0)
    vm_writer.write_call.assert_called_once_with('CurrentClass.myMethod', 3)
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()
    symbol_table.reset_mock()
    token_list.clear()

    # --- テストケース2: className '.' subroutineName '(' expressionList ')' ---
    token_list.extend(['OtherClass', '.', 'staticMethod', '(', 'arg1', ')', 'dummy'])
    symbol_table.kind_of.return_value = None

    engine.compile_subroutine_call()

    # アサーション
    vm_writer.write_push.assert_not_called()
    vm_writer.write_call.assert_called_once_with('OtherClass.staticMethod', 1)
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()
    symbol_table.reset_mock()
    token_list.clear()

    # --- テストケース3: varName '.' subroutineName '(' expressionList ')' ---
    token_list.extend(['myObject', '.', 'instanceMethod', '(', ')', 'dummy'])  # 引数なしケース
    symbol_table.kind_of.return_value = 'var'
    symbol_table.index_of.return_value = 2
    symbol_table.type_of.return_value = 'ObjectClass'

    engine.compile_subroutine_call()

    # アサーション
    vm_writer.write_push.assert_called_once_with('local', 2)
    vm_writer.write_call.assert_called_once_with('ObjectClass.instanceMethod', 1)
    assert tokenizer.get_current_token() == 'dummy'


def test_compile_expression_list(setup_engine):
    engine, tokenizer, _, vm_writer, token_list = setup_engine

    # compile_expression をモック化
    def mock_compile_expression():
        tokenizer.advance()  # 現トークンを一つ進める

    engine.compile_expression = mock_compile_expression

    # テストケース1 : 引数なし
    token_list.extend(['(', ')', 'dummy'])

    count = engine.compile_expression_list()

    assert count == 0
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース2 : 引数1つ
    token_list.clear()
    token_list.extend(['(', 'a', ')', 'dummy'])

    count = engine.compile_expression_list()

    assert count == 1
    assert tokenizer.get_current_token() == 'dummy'

    # 呼び出し履歴を初期化
    vm_writer.reset_mock()

    # テストケース3 : 引数2つ
    token_list.clear()
    token_list.extend(['(', 'a', ',', 'b', ')', 'dummy'])

    count = engine.compile_expression_list()

    assert count == 2
    assert tokenizer.get_current_token() == 'dummy'
