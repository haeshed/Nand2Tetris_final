from pprint import pprint, pformat

class InvalidKindException(Exception):
    pass

class SymbolExistsException(Exception):
    pass

class SymbolTable(object):

    ACCEPTED_KINDS = []

    def __init__(self):
        self._table = dict()
        self._count_per_kind = {k: 0 for k in self.ACCEPTED_KINDS}
    
    def addSymbol(self, name, type_, kind):
        if kind not in self.ACCEPTED_KINDS:
            raise InvalidKindException("Expected one of: {}. Got: {}".format(self.ACCEPTED_KINDS, kind))
        
        if self.symbolExists(name):
            raise SymbolExistsException("{} symbol exists already".format(name))

        self._table[name] = (type_, kind, self._count_per_kind[kind])
        self._count_per_kind[kind] += 1

    def symbolExists(self, name):
        return name in self._table
    
    def getSymbol(self, name):
        return self._table[name]

    def __str__(self):
        return pformat(self._table)
    


class ClassSymbolTable(SymbolTable):
    ACCEPTED_KINDS = ["static", "field", "function", "method", "constructor"]

    LABEL_COUNT = 0
    
    def __init__(self, name):
        super(ClassSymbolTable, self).__init__()
        self.name = name
    
    def getName(self):
        return self.name

    def getFieldsCount(self):
        return self._count_per_kind["field"]
    
    def generateLabel(self):
        lbl = "L{}".format(self.LABEL_COUNT)
        self.LABEL_COUNT += 1
        return lbl

class SubroutineSymbolTable(SymbolTable):
    ACCEPTED_KINDS = ["argument", "local"]

    def getLocalVarCount(self):
        return self._count_per_kind["local"]

def searchSymbol(name, symtable1, symtable2):
    try:
        sym = symtable1.getSymbol(name)
    except KeyError:
        sym = symtable2.getSymbol(name)
    if sym[1] == "field":
        return (sym[0], "this", sym[2])
    return sym

if __name__ == "__main__":
    a = ClassSymbolTable()
    b = SubroutineSymbolTable()

    a.addSymbol("sym1", "int", "static")
    a.addSymbol("sym2", "int", "static")
    a.addSymbol("sym3", "boolean", "field")

    print(a)
