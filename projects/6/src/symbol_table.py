class SymbolTable:
    def __init__(self):
        self.table = {}
        self.add(self, 'SP', 0)
        self.add(self, 'LCL', 1)
        self.add(self, 'ARG', 2)
        self.add(self, 'THIS', 3)
        self.add(self, 'THAT', 4)
        for i in range(16):
            self.add(self, f'R{i}', i)
        self.add(self, 'SCREEN', 16384)
        self.add(self, 'KBD', 24576)

    def add(self, symbol, address):
        self.table[symbol] = address

    def get(self, symbol):
        return self.table.get(symbol)

    def contains(self, symbol):
        return symbol in self.table
