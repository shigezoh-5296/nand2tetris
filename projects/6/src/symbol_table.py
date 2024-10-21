class SymbolTable:
    def __init__(self):
        self.table = {}
        self.initialize_predefined_symbols()
        self.current_ram_address = 16

    def initialize_predefined_symbols(self):
        self.table['SP'] = 0
        self.table['LCL'] = 1
        self.table['ARG'] = 2
        self.table['THIS'] = 3
        self.table['THAT'] = 4
        for i in range(16):
            self.table[f'R{i}'] = i
        self.table['SCREEN'] = 16384
        self.table['KBD'] = 24576

    def add_ram_symbol(self, symbol):
        self.table[symbol] = self.current_ram_address
        self.current_ram_address += 1

    def add_rom_symbol(self, symbol, address):
        self.table[symbol] = address

    def get(self, symbol):
        return self.table.get(symbol)

    def contains(self, symbol):
        return symbol in self.table
