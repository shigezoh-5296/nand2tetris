import os
import sys
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from src.code_to_bin import Code


@pytest.fixture
def code():
    return Code()


def test_dest(code):
    assert code.dest('M') == '001'
    assert code.dest('D') == '010'
    assert code.dest('MD') == '011'
    assert code.dest('A') == '100'
    assert code.dest('AM') == '101'
    assert code.dest('AD') == '110'
    assert code.dest('AMD') == '111'
    assert code.dest('X') == '000'  # Default case


def test_jump(code):
    assert code.jump('JGT') == '001'
    assert code.jump('JEQ') == '010'
    assert code.jump('JGE') == '011'
    assert code.jump('JLT') == '100'
    assert code.jump('JNE') == '101'
    assert code.jump('JLE') == '110'
    assert code.jump('JMP') == '111'
    assert code.jump('XYZ') == '000'  # Default case


def test_comp(code):
    assert code.comp('0') == '0101010'
    assert code.comp('1') == '0111111'
    assert code.comp('-1') == '0111010'
    assert code.comp('D') == '0001100'
    assert code.comp('A') == '0110000'
    assert code.comp('!D') == '0001101'
    assert code.comp('!A') == '0110001'
    assert code.comp('-D') == '0001111'
    assert code.comp('-A') == '0110011'
    assert code.comp('D+1') == '0011111'
    assert code.comp('A+1') == '0110111'
    assert code.comp('D-1') == '0001110'
    assert code.comp('A-1') == '0110010'
    assert code.comp('D+A') == '0000010'
    assert code.comp('D-A') == '0010011'
    assert code.comp('A-D') == '0000111'
    assert code.comp('D&A') == '0000000'
    assert code.comp('D|A') == '0010101'
    assert code.comp('M') == '1110000'
    assert code.comp('!M') == '1110001'
    assert code.comp('-M') == '1110011'
    assert code.comp('M+1') == '1110111'
    assert code.comp('M-1') == '1110010'
    assert code.comp('D+M') == '1000010'
    assert code.comp('D-M') == '1010011'
    assert code.comp('M-D') == '1000111'
    assert code.comp('D&M') == '1000000'
    assert code.comp('D|M') == '1010101'
    # assert code.comp('XYZ') == '0000000'  # Default case
