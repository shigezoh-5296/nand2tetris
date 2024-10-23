import os
import sys
from symbol_table import SymbolTable
from parser import Parser
from code_to_bin import Code


def conv_first(filename):
    parser = Parser(filename)
    rom_address = 0
    while parser.has_more_commands():
        parser.advance()
        match parser.command_type():
            case 'L_COMMAND':
                symbol_table.add_rom_symbol(parser.symbol(), rom_address)
            case 'A_COMMAND':
                rom_address += 1
            case 'C_COMMAND':
                rom_address += 1


def conv_second(filename):
    parser = Parser(filename)
    code = Code()
    hack = []
    while parser.has_more_commands():
        parser.advance()
        match parser.command_type():
            case 'L_COMMAND':
                pass    # 何もしない
            case 'A_COMMAND':
                symbol = parser.symbol()
                if symbol.isdigit():
                    value = bin(int(symbol))[2:]
                else:
                    if not symbol_table.contains(symbol):
                        symbol_table.add_ram_symbol(symbol)
                    value = bin(symbol_table.get(symbol))[2:]
                hack.append('0' * (16 - len(value)) + value)
            case 'C_COMMAND':
                comp_bin = code.comp(parser.comp())
                dest_bin = code.dest(parser.dest())
                jump_bin = code.jump(parser.jump())
                hack.append('111' + comp_bin + dest_bin + jump_bin)
    return hack


def output(directory, filename, content):
    os.makedirs(directory, exist_ok=True)
    with open(os.path.join(directory, filename), 'w') as f:
        for line in content:
            f.write(line + '\n')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise ValueError('Please input .asm file')
    asm_file_name = sys.argv[1]
    if not asm_file_name.endswith('.asm'):
        raise ValueError('Please input .asm file')

    # ファイル名の設定
    hack_file_name = asm_file_name.replace('.asm', '.hack')
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    target_dir = os.path.join(parent_dir, 'hack')

    # 機械語への変換
    symbol_table = SymbolTable()
    conv_first(asm_file_name)
    hack = conv_second(asm_file_name)
    output(target_dir, hack_file_name, hack)
