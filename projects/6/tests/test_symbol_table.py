import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.symbol_table import SymbolTable


@pytest.fixture
def symbol_table():
    return SymbolTable()


def test_initialize_predefined_symbols(symbol_table):
    assert symbol_table.get('SP') == 0
    assert symbol_table.get('LCL') == 1
    assert symbol_table.get('ARG') == 2
    assert symbol_table.get('THIS') == 3
    assert symbol_table.get('THAT') == 4
    for i in range(16):
        assert symbol_table.get(f'R{i}') == i
    assert symbol_table.get('SCREEN') == 16384
    assert symbol_table.get('KBD') == 24576


def test_add_ram_symbol(symbol_table):
    symbol_table.add_ram_symbol('HOGE')
    assert symbol_table.get('HOGE') == 16
    symbol_table.add_ram_symbol('FUGA')
    assert symbol_table.get('FUGA') == 17


def test_add_rom_symbol(symbol_table):
    symbol_table.add_rom_symbol('HOGE', 100)
    assert symbol_table.get('HOGE') == 100
    symbol_table.add_rom_symbol('FUGA', 200)
    assert symbol_table.get('FUGA') == 200


def test_contains(symbol_table):
    assert symbol_table.contains('SP') == True
    assert symbol_table.contains('HOGE') == False
    symbol_table.add_ram_symbol('HOGE')
    assert symbol_table.contains('HOGE') == True
    symbol_table.add_rom_symbol('FUGA', 100)
    assert symbol_table.contains('FUGA') == True
    assert symbol_table.contains('KBD') == True
    assert symbol_table.contains('R0') == True
    assert symbol_table.contains('R15') == True
    assert symbol_table.contains('R16') == False
    assert symbol_table.contains('R17') == False
    assert symbol_table.contains('R18') == False
    assert symbol_table.contains('R19') == False
    assert symbol_table.contains('R20') == False
