

import json


class SymbolTable:
    def __init__(self):
        self.symtable = dict()
        self.put("R0", 0)
        self.put("R1", 1)
        self.put("R2", 2)
        self.put("R3", 3)
        self.put("R4", 4)
        self.put("R5", 5)
        self.put("R6", 6)
        self.put("R7", 7)
        self.put("R8", 8)
        self.put("R9", 9)
        self.put("R10", 10)
        self.put("R11", 11)
        self.put("R12", 12)
        self.put("R13", 13)
        self.put("R14", 14)
        self.put("R15", 15)
        self.put("SCREEN", 16384)
        self.put("KBD", 24576)
        self.put("SP", 0)
        self.put("LCL", 1)
        self.put("ARG", 2)
        self.put("THIS", 3)
        self.put("THAT", 4)

        self.next_free_memory_address = 16

    def get(self, symbol):
        return self.symtable.get(symbol, None)
    
    def put(self, symbol, value):
        if symbol in self.symtable:
            raise ValueError("{} already exists in symtable".format(symbol))
        self.symtable[symbol] = value
    
    def allocate_variable(self, symbol):
        self.put(symbol, self.next_free_memory_address)
        sym_value = self.next_free_memory_address
        self.next_free_memory_address += 1
        return sym_value

    def __str__(self):
        return json.dumps(self.symtable, indent=4, sort_keys=True)

if __name__ == "__main__":
    print(SymbolTable())