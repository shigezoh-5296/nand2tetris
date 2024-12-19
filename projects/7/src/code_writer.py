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
            # add                             Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            asm_code.extend([
                '@SP',                        # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',                     # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'D=M',                        # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                '@SP',                        # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',                     # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'M=D+M',                      # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
                '@SP',                        # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=5
                'M=M+1'                       # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=5
            ])

        elif command == 'sub':
            # sub                             Ex) RAM[0]=SP=258, RAM[257]=2, RAM[256]=3
            asm_code.extend([
                '@SP',                        # A=0,   M=RAM[0],   D=0,  RAM[0]=258, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',                     # A=257, M=RAM[257], D=0,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'D=M',                        # A=257, M=RAM[257], D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                '@SP',                        # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'AM=M-1',                     # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=3
                'M=M-D',                      # A=256, M=RAM[256], D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
                '@SP',                        # A=0,   M=RAM[0],   D=2,  RAM[0]=256, RAM[258]=0, RAM[257]=2, RAM[256]=1
                'M=M+1'                       # A=0,   M=RAM[0],   D=2,  RAM[0]=257, RAM[258]=0, RAM[257]=2, RAM[256]=1
            ])

        elif command == 'neg':
            # neg                             Ex) RAM[0]=SP=257, RAM[256]=2
            asm_code.extend([
                '@SP',                        # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[257]=0, RAM[256]=2
                'AM=M-1',                     # A=256, M=RAM[256], D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=2
                'M=-M',                       # A=256, M=RAM[256], D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=-2
                '@SP',                        # A=0,   M=RAM[0],   D=0,  RAM[0]=256, RAM[257]=0, RAM[256]=-2
                'M=M+1'                       # A=0,   M=RAM[0],   D=0,  RAM[0]=257, RAM[257]=0, RAM[256]=-2
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
                'D;JEQ',
                # FALSEの場合(x-y!=0)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@EQ_E-{self.eq_count}',     # A=EQ_E-N, M=RAM[EQ_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x-y=0)
                f'(EQ_S-{self.eq_count})',    # TRUEの場合のJUMP先
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1

                f'(EQ_E-{self.eq_count})',
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                'M=M+1'                       # A=0,      M=RAM[0],      D=x-y, RAM[0]=257, RAM[257]=y, RAM[256]=-1
            ])
            self.eq_count += 1

        elif command == 'gt':
            # gt                              Ex) RAM[0]=SP=258, RAM[257]=y, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D=M-D',                      # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                f'@GT_S-{self.gt_count}',     # A=GT_S-N, M=RAM[GT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D;JGT',
                # FALSEの場合(x<=y)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@GT_E-{self.gt_count}',     # A=GT_E-N, M=RAM[GT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x>y=0)
                f'(GT_S-{self.gt_count})',
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1

                f'(GT_E-{self.gt_count})',
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                'M=M+1'                       # A=0,      M=RAM[0],      D=x-y, RAM[0]=257, RAM[257]=y, RAM[256]=-1
            ])
            self.gt_count += 1

        elif command == 'lt':
            # lt                              Ex) RAM[0]=SP=258, RAM[257]=y, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D=M-D',                      # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                f'@LT_S-{self.lt_count}',     # A=LT_S-N, M=RAM[LT_S-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'D;JLT',
                # FALSEの場合(x>=y)
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=0',                        # A=256,    M=0,           D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                f'@LT_E-{self.lt_count}',     # A=LT_E-N, M=RAM[LT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=0
                '0;JMP',
                # TRUEの場合(x<y=0)
                f'(LT_S-{self.lt_count})',
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'A=M',                        # A=256,    M=RAM[256],    D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=-1',                       # A=256,    M=-1,          D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1

                f'(LT_E-{self.lt_count})',    # A=LT_E-N, M=RAM[LT_E-N], D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=-1
                'M=M+1'                       # A=0,      M=RAM[0],      D=x-y, RAM[0]=257, RAM[257]=y, RAM[256]=-1
            ])
            self.lt_count += 1

        elif command == 'and':
            # and                             Ex) RAM[0]=SP=258, RAM[257]=y, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=D&M',                      # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x&y
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x&y
                'M=M+1'                       # A=0,      M=RAM[0],      D=x-y, RAM[0]=257, RAM[257]=y, RAM[256]=x&y
            ])

        elif command == 'or':
            # or                              Ex) RAM[0]=SP=258, RAM[257]=y, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=258, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=257,    M=RAM[257],    D=0,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'D=M',                        # A=257,    M=RAM[257],    D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                '@SP',                        # A=0,      M=RAM[0],      D=y,   RAM[0]=257, RAM[257]=y, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x
                'M=D|M',                      # A=256,    M=RAM[256],    D=y,   RAM[0]=256, RAM[257]=y, RAM[256]=x|y
                '@SP',                        # A=0,      M=RAM[0],      D=x-y, RAM[0]=256, RAM[257]=y, RAM[256]=x|y
                'M=M+1'                       # A=0,      M=RAM[0],      D=x-y, RAM[0]=257, RAM[257]=y, RAM[256]=x|y
            ])

        elif command == 'not':
            # not                             Ex) RAM[0]=SP=257, RAM[256]=x
            asm_code.extend([
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=257, RAM[256]=x
                'AM=M-1',                     # A=256,    M=RAM[256],    D=0,   RAM[0]=256, RAM[256]=x
                'M=!M',                       # A=256,    M=RAM[256],    D=0,   RAM[0]=256, RAM[256]=!x
                '@SP',                        # A=0,      M=RAM[0],      D=0,   RAM[0]=256, RAM[256]=!x
                'M=M+1'                       # A=0,      M=RAM[0],      D=0,   RAM[0]=257, RAM[256]=!x
            ])

        else:
            raise ValueError('Invalid command: {}'.format(command))

        self.f.write('\n'.join(asm_code) + '\n')

    def write_push_pop(self, command, segment, index):
        asm_code = []
        if command == 'C_PUSH':
            if segment == 'constant':
                # push constant N             Ex) RAM[0]=SP=256, RAM[256]=0
                asm_code.extend([
                    '@' + index,              # A=N,   M=RAM[N],   D=0,  RAM[0]=256, RAM[256]=0
                    'D=A',                    # A=N,   M=RAM[N],   D=N,  RAM[0]=256, RAM[256]=0
                    '@SP',                    # A=0,   M=RAM[0],   D=N,  RAM[0]=256, RAM[256]=0
                    'A=M',                    # A=256, M=RAM[256], D=N,  RAM[0]=256, RAM[256]=0
                    'M=D',                    # A=256, M=RMA[256], D=N,  RAM[0]=256, RAM[256]=N
                    '@SP',                    # A=0,   M=RAM[0],   D=N,  RAM[0]=256, RAM[256]=N
                    'M=M+1'                   # A=0,   M=RAM[0],   D=N,  RAM[0]=257, RAM[256]=N
                ])

            elif segment == 'local':
                # push local 2                Ex) RAM[0]=SP=256, RAM[1]=LCL=1000, RAM[256]=0, RAM[1002]=5
                asm_code.extend([
                    '@' + index,              # A=2,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5 
                    'D=A',                    # A=2,    M=RAM[0],    D=2,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    '@LCL',                   # A=1,    M=RAM[1],    D=2,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    'A=D+M',                  # A=1002, M=RAM[1002], D=2,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    'D=M',                    # A=1002, M=RAM[1002], D=5,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    'A=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=1000, RAM[256]=0, RAM[1002]=5
                    'M=D',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=1000, RAM[256]=5, RAM[1002]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=1000, RAM[256]=5, RAM[1002]=5
                    'M=M+1'                   # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[1]=1000, RAM[256]=5, RAM[1002]=5
                ])

            elif segment == 'argument':
                # push argument 0             Ex) RAM[0]=SP=256, RAM[2]=ARG=2000, RAM[256]=0, RAM[2000]=5
                asm_code.extend([
                    '@' + index,              # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5 
                    'D=A',                    # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    '@ARG',                   # A=1,    M=RAM[1],    D=0,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    'A=D+M',                  # A=2000, M=RAM[2000], D=0,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    'D=M',                    # A=2000, M=RAM[2000], D=5,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    'A=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=2000, RAM[256]=0, RAM[2000]=5
                    'M=D',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=2000, RAM[256]=5, RAM[2000]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=2000, RAM[256]=5, RAM[2000]=5
                    'M=M+1'                   # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[1]=2000, RAM[256]=5, RAM[2000]=5
                ])

            elif segment == 'this':
                # push this 0                 Ex) RAM[0]=SP=256, RAM[3]=THIS=2048, RAM[256]=0, RAM[2048]=5
                asm_code.extend([
                    '@' + index,              # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    'D=A',                    # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    '@THIS',                  # A=3,    M=RAM[3],    D=0,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    'A=D+M',                  # A=2048, M=RAM[2048], D=0,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    'D=M',                    # A=2048, M=RAM[2048], D=5,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    'A=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=2048, RAM[256]=0, RAM[2048]=5
                    'M=D',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=2048, RAM[256]=5, RAM[2048]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=2048, RAM[256]=5, RAM[2048]=5
                    'M=M+1'                   # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[1]=2048, RAM[256]=5, RAM[2048]=5
                ])

            elif segment == 'that':
                # push that 0                 Ex) RAM[0]=SP=256, RAM[4]=THAT=3048, RAM[256]=0, RAM[3048]=5
                asm_code.extend([
                    '@' + index,              # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    'D=A',                    # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    '@THAT',                  # A=4,    M=RAM[4],    D=0,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    'A=D+M',                  # A=3048, M=RAM[3048], D=0,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    'D=M',                    # A=3048, M=RAM[3048], D=5,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    '@SP',                    # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    'A=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=3048, RAM[256]=0, RAM[3048]=5
                    'M=D',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=3048, RAM[256]=5, RAM[3048]=5
                    '@SP',                    # A=0,    M=RAM[0],    D5,   RAM[0]=256, RAM[1]=3048, RAM[256]=5, RAM[3048]=5
                    'M=M+1'                   # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[1]=3048, RAM[256]=5, RAM[3048]=5
                ])

            elif segment == 'pointer':
                if index == '0':
                    # push pointer 0           Ex) RAM[0]=SP=256, RAM[3]=THIS=3000, RAM[256]=0, RAM[3000]=5
                    asm_code.extend([
                        '@THIS',               # A=3,    M=RAM[3],    D=0,  RAM[0]=256, RAM[3]=3000, RAM[256]=0, RAM[3000]=5
                        'D=M',                 # A=3,    M=RAM[3],    D=5,  RAM[0]=256, RAM[3]=3000, RAM[256]=0, RAM[3000]=5
                        '@SP',                 # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[3]=3000, RAM[256]=0, RAM[3000]=5
                        'A=M',                 # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[3]=3000, RAM[256]=0, RAM[3000]=5
                        'M=D',                 # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=5
                        '@SP',                 # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=5
                        'M=M+1'                # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[3]=3000, RAM[256]=5, RAM[3000]=5
                    ])
                elif index == '1':
                    # push pointer 1           Ex) RAM[0]=SP=256, RAM[4]=THAT=4000, RAM[256]=0, RAM[4000]=5
                    asm_code.extend([
                        '@THAT',               # A=4,    M=RAM[4],    D=0,  RAM[0]=256, RAM[4]=4000, RAM[256]=0, RAM[4000]=5
                        'D=M',                 # A=4,    M=RAM[4],    D=5,  RAM[0]=256, RAM[4]=4000, RAM[256]=0, RAM[4000]=5
                        '@SP',                 # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[4]=4000, RAM[256]=0, RAM[4000]=5
                        'A=M',                 # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[4]=4000, RAM[256]=0, RAM[4000]=5
                        'M=D',                 # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=5
                        '@SP',                 # A=0,    M=RAM[0],    D=5,  RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=5
                        'M=M+1'                # A=0,    M=RAM[0],    D=5,  RAM[0]=257, RAM[4]=4000, RAM[256]=5, RAM[4000]=5
                    ])
                else:
                    raise ValueError('Invalid index: {}'.format(index))

            elif segment == 'temp':
                # push temp 3                 Ex) RAM[0]=SP=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                address = 5 + int(index)
                asm_code.extend([
                    '@' + str(address),       # A=5,    M=RAM[5],    D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    'D=M',                    # A=5,    M=RAM[5],    D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    'A=M',                    # A=256,  M=RAM[256],  D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    'M=D',                    # A=256,  M=RAM[256],  D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=0,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=0
                    'M=M+1'                   # A=0,    M=RAM[0],    D=0,  RAM[0]=257, RAM[5]=0, RAM[8]=5, RAM[256]=0
                ])

            elif segment == 'static':
                # push static 3               Ex) RAM[0]=SP=256, RAM[256]=0, "input_file_name.3"=RAM[16]=5
                asm_code.extend([
                    '@' + self.input_filename + '.' + index,  # A=filename.3, M=RAM[filename.3], D=0,  RAM[0]=256, RAM[256]=0, RAM[16]=5
                    'D=M',                                    # A=filename.3, M=RAM[filename.3], D=5,  RAM[0]=256, RAM[256]=0, RAM[16]=5
                    '@SP',                                    # A=0,          M=RAM[0],          D=5,  RAM[0]=256, RAM[256]=0, RAM[16]=5
                    'A=M',                                    # A=256,        M=RAM[256],        D=5,  RAM[0]=256, RAM[256]=0, RAM[16]=5
                    'M=D',                                    # A=256,        M=RAM[256],        D=5,  RAM[0]=256, RAM[256]=5, RAM[16]=5
                    '@SP',                                    # A=0,          M=RAM[0],          D=5,  RAM[0]=256, RAM[256]=5, RAM[16]=5
                    'M=M+1'                                   # A=0,          M=RAM[0],          D=5,  RAM[0]=257, RAM[256]=5, RAM[16]=5
                ])

            else:
                raise ValueError('Invalid segment: {}'.format(segment))

        elif command == 'C_POP':
            if segment == 'local':
                # pop local 2                Ex) RAM[0]=SP=257, RAM[1]=LCL=1000, RAM[256]=5, RAM[1000]=0, RAM[1002]=0
                asm_code.extend([
                    '@' + index,              # A=2,    M=RAM[2],    D=0,  RAM[0]=257, RAM[1]=1000, RAM[1000]=0, RAM[1002]=0
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[1]=1000, RAM[1000]=0, RAM[1002]=0
                    '@LCL',                   # A=1,    M=RAM[1],    D=2,  RAM[0]=257, RAM[1]=1000, RAM[1000]=0, RAM[1002]=0
                    'M=D+M',                  # A=1,    M=RAM[1],    D=2,  RAM[0]=257, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=2,  RAM[0]=257, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    'AM=M-1',                 # A=256,  M=RAM[256],  D=2,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    'D=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    '@LCL',                   # A=1,    M=RAM[1],    D=5,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    'A=M',                    # A=1002, M=RAM[1002], D=5,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=0
                    'M=D',                    # A=1002, M=RAM[1002], D=5,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=5
                    '@' + index,              # A=2,    M=RAM[2],    D=5,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=5
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=5
                    '@LCL',                   # A=1,    M=RAM[1],    D=2,  RAM[0]=256, RAM[1]=1002, RAM[1000]=0, RAM[1002]=5
                    'M=M-D'                   # A=1,    M=RAM[1],    D=2,  RAM[0]=256, RAM[1]=1000, RAM[1000]=0, RAM[1002]=5
                ])

            elif segment == 'argument':
                # pop argument 2             Ex) RAM[0]=SP=257, RAM[2]=ARG=2000, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                asm_code.extend([
                    '@' + index,              # A=2,    M=RAM[2],    D=0,  RAM[0]=257, RAM[2]=2000, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[2]=2000, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    '@ARG',                   # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[2]=2000, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'M=D+M',                  # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=2,  RAM[0]=257, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'AM=M-1',                 # A=256,  M=RAM[256],  D=2,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'D=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    '@ARG',                   # A=2,    M=RAM[2],    D=5,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'A=M',                    # A=2002, M=RAM[2002], D=5,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=0
                    'M=D',                    # A=2002, M=RAM[2002], D=5,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=5
                    '@' + index,              # A=2,    M=RAM[2],    D=5,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=5
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=5
                    '@ARG',                   # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[2]=2002, RAM[256]=5, RAM[2000]=0, RAM[2002]=5
                    'M=M-D'                   # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[2]=2000, RAM[256]=5, RAM[2000]=0, RAM[2002]=5
                ])

            elif segment == 'this':
                # pop this 2                 Ex) RAM[0]=SP=257, RAM[3]=THIS=2048, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                asm_code.extend([
                    '@' + index,              # A=2,    M=RAM[2],    D=0,  RAM[0]=257, RAM[3]=2048, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[3]=2048, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    '@THIS',                  # A=3,    M=RAM[3],    D=2,  RAM[0]=257, RAM[3]=2048, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'M=D+M',                  # A=3,    M=RAM[3],    D=2,  RAM[0]=257, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=2,  RAM[0]=257, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'AM=M-1',                 # A=256,  M=RAM[256],  D=2,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'D=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    '@THIS',                  # A=3,    M=RAM[3],    D=5,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'A=M',                    # A=2050, M=RAM[2050], D=5,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=0
                    'M=D',                    # A=2050, M=RAM[2050], D=5,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=5
                    '@' + index,              # A=2,    M=RAM[2],    D=5,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=5
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=5
                    '@THIS',                  # A=3,    M=RAM[3],    D=2,  RAM[0]=256, RAM[3]=2050, RAM[256]=5, RAM[2048]=0, RAM[2050]=5
                    'M=M-D'                   # A=3,    M=RAM[3],    D=2,  RAM[0]=256, RAM[3]=2048, RAM[256]=5, RAM[2048]=0, RAM[2050]=5
                ])

            elif segment == 'that':
                # pop that 2                 Ex) RAM[0]=SP=257, RAM[4]=THAT=3048, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                asm_code.extend([
                    '@' + index,              # A=2,    M=RAM[2],    D=0,  RAM[0]=257, RAM[4]=3048, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=257, RAM[4]=3048, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    '@THAT',                  # A=4,    M=RAM[4],    D=2,  RAM[0]=257, RAM[4]=3048, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'M=D+M',                  # A=4,    M=RAM[4],    D=2,  RAM[0]=257, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    '@SP',                    # A=0,    M=RAM[0],    D=2,  RAM[0]=257, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'AM=M-1',                 # A=256,  M=RAM[256],  D=2,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'D=M',                    # A=256,  M=RAM[256],  D=5,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    '@THAT',                  # A=4,    M=RAM[4],    D=5,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'A=M',                    # A=3050, M=RAM[3050], D=5,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=0
                    'M=D',                    # A=3050, M=RAM[3050], D=5,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=5
                    '@' + index,              # A=2,    M=RAM[2],    D=5,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=5
                    'D=A',                    # A=2,    M=RAM[2],    D=2,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=5
                    '@THAT',                  # A=4,    M=RAM[4],    D=2,  RAM[0]=256, RAM[4]=3050, RAM[256]=5, RAM[3048]=0, RAM[3050]=5
                    'M=M-D'                   # A=4,    M=RAM[4],    D=2,  RAM[0]=256, RAM[4]=3048, RAM[256]=5, RAM[3048]=0, RAM[3050]=5
                ])

            elif segment == 'pointer':
                if index == '0':
                    # pop pointer 0           Ex) RAM[0]=SP=257, RAM[3]=THIS=3000, RAM[256]=5, RAM[3000]=0
                    asm_code.extend([
                        '@SP',                 # A=0,    M=RAM[0],    D=257,  RAM[0]=257, RAM[3]=3000, RAM[256]=5, RAM[3000]=0
                        'AM=M-1',              # A=256,  M=RAM[256],  D=257,  RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=0
                        'D=M',                 # A=256,  M=RAM[256],  D=5,    RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=0
                        '@THIS',               # A=3,    M=RAM[3],    D=5,    RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=0
                        'M=D',                 # A=3,    M=RAM[3],    D=5,    RAM[0]=256, RAM[3]=3000, RAM[256]=5, RAM[3000]=5
                    ])
                elif index == '1':
                    # pop pointer 1           Ex) RAM[0]=SP=257, RAM[4]=THAT=4000, RAM[256]=5, RAM[4000]=0
                    asm_code.extend([
                        '@SP',                 # A=0,    M=RAM[0],    D=257,  RAM[0]=257, RAM[4]=4000, RAM[256]=5, RAM[4000]=0
                        'AM=M-1',              # A=256,  M=RAM[256],  D=257,  RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=0
                        'D=M',                 # A=256,  M=RAM[256],  D=5,    RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=0
                        '@THAT',               # A=4,    M=RAM[4],    D=5,    RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=0
                        'M=D',                 # A=4,    M=RAM[4],    D=5,    RAM[0]=256, RAM[4]=4000, RAM[256]=5, RAM[4000]=5
                    ])
                else:
                    raise ValueError('Invalid index: {}'.format(index))

            elif segment == 'temp':
                # pop temp 3                  Ex) RAM[0]=SP=257, RAM[5]=0, RAM[8]=5, RAM[256]=5
                address = 5 + int(index)
                asm_code.extend([
                    '@SP',                     # A=0,    M=RAM[0],    D=257,  RAM[0]=257, RAM[5]=0, RAM[8]=5, RAM[256]=5
                    'AM=M-1',                  # A=256,  M=RAM[256],  D=257,  RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=5
                    'D=M',                     # A=256,  M=RAM[256],  D=5,    RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=5
                    '@' + str(address),        # A=8,    M=RAM[8],    D=5,    RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=5
                    'M=D'                      # A=8,    M=RAM[8],    D=5,    RAM[0]=256, RAM[5]=0, RAM[8]=5, RAM[256]=5
                ])

            elif segment == 'static':
                # pop static 3                Ex) RAM[0]=SP=257, RAM[256]=5, "input_file_name.3"=RAM[16]=0
                asm_code.extend([
                    '@SP',                                    # A=0,          M=RAM[0],          D=257,  RAM[0]=257, RAM[256]=5, RAM[16]=0
                    'AM=M-1',                                 # A=256,        M=RAM[256],        D=257,  RAM[0]=256, RAM[256]=5, RAM[16]=0
                    'D=M',                                    # A=256,        M=RAM[256],        D=5,    RAM[0]=256, RAM[256]=5, RAM[16]=0
                    '@' + self.input_filename + '.' + index,  # A=filename.3, M=RAM[filename.3], D=5,    RAM[0]=256, RAM[256]=5, RAM[16]=0
                    'M=D'                                     # A=filename.3, M=RAM[filename.3], D=5,    RAM[0]=256, RAM[256]=5, RAM[16]=5
                ])

            else:
                raise ValueError('Invalid segment: {}'.format(segment))
        else:
            raise ValueError('Invalid command: {}'.format(command))

        self.f.write('\n'.join(asm_code) + '\n')

    def write_label(self, label):
        asm_code = []
        asm_code.extend([f'({label})'])
        self.f.write('\n'.join(asm_code) + '\n')

    def write_goto(self, label):
        asm_code = []
        asm_code.extend([
            f'@{label}',
            '0;JMP'
        ])
        self.f.write('\n'.join(asm_code) + '\n')

    def write_if(self, label):
        asm_code = []
        asm_code.extend([
            '@SP',
            'AM=M-1',
            'D=M',
            f'@{label}',
            'D;JNE'
        ])
        self.f.write('\n'.join(asm_code) + '\n')

    def close(self):
        self.f.close()
