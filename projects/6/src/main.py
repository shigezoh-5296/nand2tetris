import os
import sys
from parser import Parser
from code_to_bin import Code


def conv(filename):
    parser = Parser(filename)
    code = Code()
    hack = []
    while parser.has_more_commands():
        parser.advance()
        match parser.command_type():
            case 'A_COMMAND':
                value = bin(int(parser.symbol()))[2:]
                hack.append('0' * (16 - len(value)) + value)

            # case 'L_COMMAND':
            #     hack.append(parser.symbol())

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

    hack_file_name = asm_file_name.replace('.asm', '.hack')
    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)
    target_dir = os.path.join(parent_dir, 'hack')

    hack = conv(asm_file_name)
    output(target_dir, hack_file_name, hack)
