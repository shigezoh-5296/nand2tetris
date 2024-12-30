import os


class VmParser:
    def __init__(self, filename, directory):
        self.filename = filename
        try:
            self.f = open(os.path.join(directory, filename), 'r')
        except FileNotFoundError:
            print('File not found')
            raise
        self.lines = self.get_lines()
        self.current_line = -1
        self.current_command = None

    def get_lines(self):
        # 空行とコメント行（行頭が//）は削除したリストを返す
        lines = self.f.readlines()
        lines = [line.strip() for line in lines if line.strip()
                 and not line.strip().startswith('//')]
        # 途中のコメントも削除
        lines = [line.split('//')[0].strip() for line in lines]
        return lines

    def has_more_commands(self):
        return self.current_line + 1 < len(self.lines)

    def advance(self):
        self.current_line += 1
        self.current_command = self.lines[self.current_line]

    def command_type(self):
        if self.current_command.startswith('push'):
            return 'C_PUSH'
        elif self.current_command.startswith('pop'):
            return 'C_POP'
        elif self.current_command.startswith('label'):
            return 'C_LABEL'
        elif self.current_command.startswith('goto'):
            return 'C_GOTO'
        elif self.current_command.startswith('if-goto'):
            return 'C_IF'
        elif self.current_command.startswith('function'):
            return 'C_FUNCTION'
        elif self.current_command.startswith('call'):
            return 'C_CALL'
        elif self.current_command.startswith('return'):
            return 'C_RETURN'
        else:
            return 'C_ARITHMETIC'

    def arg1(self):
        if self.command_type() == 'C_ARITHMETIC':
            return self.current_command.split()[0]
        else:
            return self.current_command.split()[1]

    def arg2(self):
        return self.current_command.split()[2]
