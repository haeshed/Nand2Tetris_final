import sys
import os
import traceback
from SymbolTable import SymbolTable
from Instruction import InstructionParser, Instruction
import re

class HackAssembler:
    def __init__(self, asm_filename):
        self.asm_filename = asm_filename
        self.hack_filename = os.path.splitext(asm_filename)[0] + ".hack"
        self.symtable = SymbolTable()

    def __enter__(self):
        self.asm_fh = open(self.asm_filename, "r")
        self.hack_fh = open(self.hack_filename, "w")
        return self

    def __exit__(self, exc_type, exc_value, tb):
        ret = True
        if exc_type is not None:
            ret = False
        self.asm_fh.close()
        self.hack_fh.close()
        return ret

    def _is_comment_line(self, line):
        return line.strip().startswith("//")
    
    def _is_empty_line(self, line):
        return line == "\n" or line == "\r\n"
    
    def _should_skip_line(self, line):
        return self._is_empty_line(line) or self._is_comment_line(line)

    def _is_label(self, line):
        stripped_line = line.strip()
        return stripped_line[0] == "(" and stripped_line[-1] == ")"
    
    def _parse_label(self, label_line):
        pattern = "\((.*)\)"
        label = re.match(pattern, label_line).group(1)
        return label

    def _first_pass(self):
        line = self.asm_fh.readline()
        instruction_idx = -1
        while line:
            if not self._should_skip_line(line):
                if self._is_label(line):
                    label = self._parse_label(line)
                    self.symtable.put(label, instruction_idx + 1)
                else:
                    instruction_idx += 1
            line = self.asm_fh.readline()

    def _second_pass(self):
        line = self.asm_fh.readline()
        instruction_idx = -1
        while line:
            if not self._should_skip_line(line) and not self._is_label(line):
                instruction = InstructionParser.parse(line)
                self.hack_fh.write(instruction.encode(symtable=self.symtable))
                instruction_idx += 1
            line = self.asm_fh.readline()

    def assemble(self):
        self._first_pass()
        self.asm_fh.seek(0)
        self._second_pass()
        print(self.symtable)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python HackAssembler.py <asm_file>")
        sys.exit(1)
    asm_filename = sys.argv[1]
    with HackAssembler(asm_filename) as assembler:
        assembler.assemble()
