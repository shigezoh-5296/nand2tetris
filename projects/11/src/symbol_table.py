class SymbolTable:
    def __init__(self):
        self.class_symbols = {}
        self.subroutine_symbols = {}
        self.static_index = 0
        self.field_index = 0
        self.argument_index = 0
        self.var_index = 0

    def start_subroutine(self):
        self.subroutine_symbols = {}
        self.argument_index = 0
        self.var_index = 0

    def define(self, name, type, kind):
        if kind in ['static', 'field']:  # class scope
            if kind == 'static':
                index = self.static_index
                self.static_index += 1
            else:
                index = self.field_index
                self.field_index += 1
            self.class_symbols[name] = (type, kind, index)
        else:  # subroutine scope
            if kind == 'argument':
                index = self.argument_index
                self.argument_index += 1
            else:
                index = self.var_index
                self.var_index += 1
            self.subroutine_symbols[name] = (type, kind, index)

    def var_count(self, kind):
        if kind in ['static', 'field']:
            return self.static_index if kind == 'static' else self.field_index
        else:
            return self.argument_index if kind == 'argument' else self.var_index

    def kind_of(self, name):
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name][1]
        elif name in self.class_symbols:
            return self.class_symbols[name][1]
        else:
            return None

    def type_of(self, name):
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name][0]
        elif name in self.class_symbols:
            return self.class_symbols[name][0]
        else:
            return None

    def index_of(self, name):
        if name in self.subroutine_symbols:
            return self.subroutine_symbols[name][2]
        elif name in self.class_symbols:
            return self.class_symbols[name][2]
        else:
            return None
