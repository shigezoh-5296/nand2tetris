import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.symbol_table import SymbolTable


def test_define_and_var_count():
    symbol_table = SymbolTable()

    # クラススコープのシンボルを定義
    symbol_table.define("x", "int", "static")
    symbol_table.define("y", "boolean", "field")

    assert symbol_table.var_count("static") == 1
    assert symbol_table.var_count("field") == 1

    # サブルーチンスコープのシンボルを定義
    symbol_table.define("z", "int", "argument")
    symbol_table.define("w", "boolean", "var")

    assert symbol_table.var_count("argument") == 1
    assert symbol_table.var_count("var") == 1


def test_start_subroutine():
    symbol_table = SymbolTable()

    # サブルーチンスコープのシンボルを定義
    symbol_table.define("a", "int", "argument")
    symbol_table.define("b", "boolean", "var")

    # サブルーチンスコープをリセット
    symbol_table.start_subroutine()

    assert symbol_table.var_count("argument") == 0
    assert symbol_table.var_count("var") == 0
    assert symbol_table.kind_of("a") is None
    assert symbol_table.kind_of("b") is None


def test_kind_of():
    symbol_table = SymbolTable()

    # クラススコープのシンボルを定義
    symbol_table.define("x", "int", "static")
    symbol_table.define("y", "boolean", "field")

    # サブルーチンスコープのシンボルを定義
    symbol_table.define("z", "int", "argument")
    symbol_table.define("w", "boolean", "var")

    assert symbol_table.kind_of("x") == "static"
    assert symbol_table.kind_of("y") == "field"
    assert symbol_table.kind_of("z") == "argument"
    assert symbol_table.kind_of("w") == "var"
    assert symbol_table.kind_of("unknown") is None


def test_type_of():
    symbol_table = SymbolTable()

    # クラススコープのシンボルを定義
    symbol_table.define("x", "int", "static")
    symbol_table.define("y", "boolean", "field")

    # サブルーチンスコープのシンボルを定義
    symbol_table.define("z", "int", "argument")
    symbol_table.define("w", "boolean", "var")

    assert symbol_table.type_of("x") == "int"
    assert symbol_table.type_of("y") == "boolean"
    assert symbol_table.type_of("z") == "int"
    assert symbol_table.type_of("w") == "boolean"
    assert symbol_table.type_of("unknown") is None


def test_index_of():
    symbol_table = SymbolTable()

    # クラススコープのシンボルを定義
    symbol_table.define("x", "int", "static")
    symbol_table.define("y", "boolean", "field")

    # サブルーチンスコープのシンボルを定義
    symbol_table.define("z", "int", "argument")
    symbol_table.define("w", "boolean", "var")

    assert symbol_table.index_of("x") == 0
    assert symbol_table.index_of("y") == 0
    assert symbol_table.index_of("z") == 0
    assert symbol_table.index_of("w") == 0
    assert symbol_table.index_of("unknown") is None