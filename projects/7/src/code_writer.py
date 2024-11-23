import os


class CodeWriter:
    def __init__(self, filename, directory):
        self.output_filename = filename
        self.eq_count = 0
        self.gt_count = 0
        self.lt_count = 0
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
            asm_code.extend([
                '@SP',      # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',   # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'D=M',      # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                '@SP',      # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',   # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'M=D+M',    # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
                '@SP',      # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
                'M=M+1'     # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=5
            ])
        elif command == 'sub':
            # sub           Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            asm_code.extend([
                '@SP',      # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',   # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'D=M',      # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                '@SP',      # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',   # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'M=M-D',    # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
                '@SP',      # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
                'M=M+1'     # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=1
            ])
        elif command == 'neg':
            # neg           Ex) RAM[0]=SP=257, RAM[256]=2
            asm_code.extend([
                '@SP',      # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[257]=0, RAM[256]=2
                'AM=M-1',   # A=256, M=RAM[256], D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=2
                'M=-M',     # A=256, M=RAM[256], D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=-2
                '@SP',      # A=0,   M=RAM[0],   D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=-2
                'M=M+1'     # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[257]=0, RAM[256]=-2
            ])
        elif command == 'eq':
            # eq                              Ex) RAM[0]=SP=258, RAM[257]=y, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D=M-D',                      # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                f'@EQ_S-{self.eq_count}',     # A=EQ_S-N, M=RAM[EQ_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D;JEQ'
                # FALSEの場合(x-y!=0)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@EQ_E-{self.eq_count}',     # A=EQ_E-N, M=RAM[EQ_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x-y=0)
                f'(EQ_S-{self.eq_count})',    # A=EQ_S-N, M=RAM[EQ_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                # FALSEの場合のJUMP先
                f'(EQ_E-{self.eq_count})',    # A=EQ_E-N, M=RAM[EQ_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
            ])
        elif command == 'gt':
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D=M-D',                      # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                f'@GT_S-{self.gt_count}',     # A=GT_S-N, M=RAM[GT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D;JGT'
                # FALSEの場合(x<=y)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@GT_E-{self.gt_count}',     # A=GT_E-N, M=RAM[GT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x>y=0)
                f'(GT_S-{self.gt_count})',    # A=GT_S-N, M=RAM[GT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                # FALSEの場合のJUMP先
                f'(GT_E-{self.gt_count})',    # A=GT_E-N, M=RAM[GT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
            ])
        elif command == 'lt':
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D=M-D',                      # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                f'@LT_S-{self.lt_count}',     # A=LT_S-N, M=RAM[LT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D;JLT'
                # FALSEの場合(x>=y)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@LT_E-{self.lt_count}',     # A=LT_E-N, M=RAM[LT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x<y=0)
                f'(LT_S-{self.lt_count})',    # A=LT_S-N, M=RAM[LT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                # FALSEの場合のJUMP先
                f'(LT_E-{self.lt_count})',    # A=LT_E-N, M=RAM[LT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
            ])
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
                asm_code.extend([
                    '@' + index,   # A=x,   M=RAM[x],   D=0,  RAM[0]=256, RAM[256]=0
                    'D=A',         # A=x,   M=RAM[x],   D=x,  RAM[0]=256, RAM[256]=0
                    '@SP',         # A=0,   M=RAM[0],   D=x,  RAM[0]=256, RAM[256]=0
                    'A=M',         # A=256, M=RAM[256], D=x,  RAM[0]=256, RAM[256]=0
                    'M=D',         # A=256, M=RMA[256], D=x,  RAM[0]=256, RAM[256]=x
                    '@SP',         # A=0,   M=RAM[0],   D=x,  RAM[0]=256, RAM[256]=x
                    'M=M+1'        # A=0,   M=RAM[0],   D=x,  RAM[0]=257, RAM[256]=x
                ])
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