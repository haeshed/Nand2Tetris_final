
class VMWriter:

    SEGMENTS = ["constant", "argument", "local", "static", "this", "that", "pointer", "temp"]

    def __init__(self, fh):
        self.fh = fh
    
    def _writeLine(self, line, indent=True):
        # if indent:
        #     self.fh.write('\t')
        self.fh.write(line + "\n")
        self.fh.flush()

    def writeLabel(self, label):
        self._writeLine("label {label}".format(label=label), indent=False)
    
    def writeFunctionEP(self, name, nargs):
        self._writeLine("function {name} {nargs}".format(name=name, nargs=nargs), indent=False)
    
    def writeReturn(self):
        self._writeLine("return")
    
    def writeInitObjectCode(self, size):
        self.writePush("constant", size)
        self._writeLine("call Memory.alloc 1")
        self._writeLine("pop pointer 0")

    def loadThis(self):
        self._writeLine("push argument 0")
        self._writeLine("pop pointer 0")
    
    def writeOp(self, op):
        op_to_jack_funcname = {
            '+': "add",
            '-': "sub",
            '<': "lt",
            '>': "gt",
            '&': "and",
            '|': "or",
            '=': "eq"
        }
        self._writeLine(op_to_jack_funcname[op])
    
    def writeUnaryOp(self, op):
        op_to_jack_funcname = {
            '~': "not",
            '-': "neg",
        }
        self._writeLine(op_to_jack_funcname[op])
    
    def writePush(self, segment, index):
        if segment not in self.SEGMENTS:
            self._writeLine("push {segment}".format(segment=segment))
        else:
            self._writeLine("push {segment} {index}".format(segment=segment, index=index))
    
    def writePushSymbol(self, sym):
        self.writePush(sym[1], sym[2])

    def writePop(self, segment, index):
        self._writeLine("pop {segment} {index}".format(segment=segment, index=index))

    def writePopSymbol(self, sym):
        self.writePop(sym[1], sym[2])

    def writeCall(self, subroutine, nargs):
        self._writeLine("call {subroutine} {nargs}".format(subroutine=subroutine, nargs=nargs))
    
    def writeIfGoto(self, label):
        self._writeLine("if-goto {label}".format(label=label))
    
    def writeGoto(self, label):
        self._writeLine("goto {label}".format(label=label))