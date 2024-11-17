import os
import sys
from parser import Parser
from code_writer import CodeWriter

if __name__ == '__main__':
    # "python vm_translator.py directory"で実行されることを想定
    # それ以外の形式ではエラーを出す
    if len(sys.argv) != 2:
        raise ValueError('Please input .asm file')
    if not os.path.isdir(sys.argv[1]):
        print(sys.argv[1])
        raise ValueError('Please input directory')

    output_filename = os.path.basename(sys.argv[1])
    directory = sys.argv[1]
    cw = CodeWriter(output_filename, directory) 

    for dirpath, _, filenames in os.walk(sys.argv[1]):
        for filename in filenames:
            if filename.endswith('.vm'):
                cw.set_filename(filename)
                parser = Parser(filename)
                while parser.has_more_commands():
                    parser.advance()
                    command_type = parser.command_type()
                    if command_type == 'C_ARITHMETIC':
                        cw.write_arithmetic(parser.arg1())
                    elif command_type in ['C_PUSH', 'C_POP']:
                        cw.write_push_pop(command_type, parser.arg1(),
                                          parser.arg2())
                    else:
                        raise ValueError(
                            'Invalid command type: {}'.format(command_type))
