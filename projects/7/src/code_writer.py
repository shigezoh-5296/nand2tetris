import os


class CodeWriter:
    def __init__(self, filename, directory):
        self.output_filename = filename
        # asm_directory = os.path.join(directory, 'asm')
        # os.makedirs(asm_directory, exist_ok=True)
        try:
            self.f = open(os.path.join(directory, filename + '.asm'), 'w')
        except IOError as e:
            print(f"Error opening file: {e}")
            raise

    def set_filename(self, filename):
        self.input_filename = filename

    def write_arithmetic(self, command):
        asm_code = []
        if command == 'add':
            # add                       Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=M-1')    # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('A=M')      # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('D=M')      # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=M-1')    # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('A=M')      # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=D+M')    # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
            asm_code.append('M=M+1')    # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=5
        elif command == 'sub':
            # sub                       Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=M-1')    # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('A=M')      # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('D=M')      # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=M-1')    # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('A=M')      # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
            asm_code.append('M=M-D')    # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
            asm_code.append('@SP')      # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
            asm_code.append('M=M+1')    # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=1
        elif command == 'neg':
            # neg                            Ex) RAM[0]=SP=258, RAM[257]=2
            # 後から実装
            pass
        elif command == 'eq':
            # eq                             Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=2
            # 後から実装
            pass
        elif command == 'gt':
            # gt                             Ex) RAM[0]=SP=258, RAM[257]=3, RAM[256]=2
            # 後から実装
            pass
        elif command == 'lt':
            # lt                             Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            # 後から実装
            pass
        elif command == 'and':
            # and                            Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            # 後から実装
            pass
        elif command == 'or':
            # or                             Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            # 後から実装
            pass
        elif command == 'not':
            # not                            Ex) RAM[0]=SP=258, RAM[257]=2
            # 後から実装
            pass
        else:
            raise ValueError('Invalid command: {}'.format(command))

        self.f.write('\n'.join(asm_code) + '\n')

    def write_push_pop(self, command, segment, index):
        asm_code = []
        if command == 'C_PUSH':
            if segment == 'constant':
                # push constant x              Ex) RAM[0]=SP=256, RAM[256]=0
                asm_code.append('@' + index)   # A=x,   M=RAM[x],   D=0,  RAM[0]=256, RAM[256]=0
                asm_code.append('D=A')         # A=x,   M=RAM[x],   D=x,  RAM[0]=256, RAM[256]=0
                asm_code.append('@SP')         # A=0,   M=RAM[0],   D=x,  RAM[0]=256, RAM[256]=0
                asm_code.append('A=M')         # A=256, M=RAM[256], D=x,  RAM[0]=256, RAM[256]=0
                asm_code.append('M=D')         # A=256, M=RMA[256], D=x,  RAM[0]=256, RAM[256]=x
                asm_code.append('@SP')         # A=0,   M=RAM[0],   D=x,  RAM[0]=256, RAM[256]=x
                asm_code.append('M=M+1')       # A=0,   M=RAM[0],   D=x,  RAM[0]=257, RAM[256]=x
            elif segment == 'local':
                # push local x                       Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'argument':
                # push argument x                    Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'this':
                # push this x                        Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'that':
                # push that x                        Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'pointer':
                # push pointer x                     Ex) RAM[0]=SP=256, RAM[257]=3, RAM[256]=4
                # 後から実装
                pass
            elif segment == 'temp':
                # push temp x                        Ex) RAM[0]=SP=256, RAM[257]=5, RAM[256]=6
                # 後から実装
                pass
            elif segment == 'static':
                # push static x                      Ex) RAM[0]=SP=256, RAM[257]=16, RAM[256]=17
                # 後から実装
                pass
            else:
                raise ValueError('Invalid segment: {}'.format(segment))
        elif command == 'C_POP':
            if segment == 'local':
                # pop local x                        Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'argument':
                # pop argument x                     Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'this':
                # pop this x                         Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'that':
                # pop that x                         Ex) RAM[0]=SP=256, RAM[257]=2, RAM[256]=3
                # 後から実装
                pass
            elif segment == 'pointer':
                # pop pointer x                      Ex) RAM[0]=SP=256, RAM[257]=3, RAM[256]=4
                # 後から実装
                pass
            elif segment == 'temp':
                # pop temp x                         Ex) RAM[0]=SP=256, RAM[257]=5, RAM[256]=6
                # 後から実装
                pass
            elif segment == 'static':
                # pop static x                       Ex) RAM[0]=SP=256, RAM[257]=16, RAM[256]=17
                # 後から実装
                pass
            else:
                raise ValueError('Invalid segment: {}'.format(segment))
        else:
            raise ValueError('Invalid command: {}'.format(command))

        self.f.write('\n'.join(asm_code) + '\n')

    def close(self):
        self.f.close()
