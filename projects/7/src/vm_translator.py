import os
import sys
from vm_parser import VmParser
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

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.vm'):
                cw.set_filename(filename)
                parser = VmParser(filename, directory)
                while parser.has_more_commands():
                    parser.advance()
                    command_type = parser.command_type()
                    if command_type == 'C_ARITHMETIC':
                        cw.write_arithmetic(parser.arg1())
                    elif command_type in ['C_PUSH', 'C_POP']:
                        cw.write_push_pop(command_type, parser.arg1(),
                                          parser.arg2())
                    elif command_type == 'C_LABEL':
                        cw.write_label(parser.arg1())
                    elif command_type == 'C_GOTO':
                        cw.write_goto(parser.arg1())
                    elif command_type == 'C_IF':
                        cw.write_if(parser.arg1())
                    elif command_type == 'C_FUNCTION':
                        cw.write_function(parser.arg1(), int(parser.arg2()))
                    elif command_type == 'C_RETURN':
                        cw.write_return()
                    elif command_type == 'C_CALL':
                        cw.write_call(parser.arg1(), int(parser.arg2()))
                    else:
                        raise ValueError(
                            'Invalid command type: {}'.format(command_type))
