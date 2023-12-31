
import re

class Instruction:
    def encode(self, **kwargs):
        pass

class InstructionParser:
    @staticmethod
    def parse(line):
        no_comment_pattern = "^(.+?)(\/\/.*)?$"
        stripped_line = re.match(no_comment_pattern, line).group(1)
        stripped_line = stripped_line.strip()
        print(stripped_line)
        if stripped_line[0] == "@":
            # Parse A instruction
            addr = stripped_line[1:]
            return AInstruction(addr)
        else:
            # Parse C instruction
            pattern = "^((.+)=)?(.+?)(;(.+))?$"
            dest, comp, jmp = re.match(pattern, stripped_line).group(2, 3, 5)
            return CInstruction(dest, comp, jmp)


class CInstruction(Instruction):
    def __init__(self, dest, comp, jmp):
        self.dest = dest
        self.comp = comp
        self.jmp = jmp

    def _encode_comp(self, **kwargs):
        if "M" in self.comp:
            a = '1'
        else:
            a = '0'

        if self.comp == '0':
            enc_c = "101010"
        elif self.comp == '1':
            enc_c = "111111"
        elif self.comp == "-1":
            enc_c = "111010"
        elif self.comp == "D":
            enc_c = "001100"
        elif self.comp == "A" or self.comp == "M":
            enc_c = "110000"
        elif self.comp == "!D":
            enc_c = "001101"
        elif self.comp == "!A" or self.comp == "!M":
            enc_c = "110001"
        elif self.comp == "-D":
            enc_c = "001111"
        elif self.comp == "-A" or self.comp == "-M":
            enc_c = "110011"
        elif self.comp == "D+1":
            enc_c = "011111"
        elif self.comp == "A+1" or self.comp == "M+1":
            enc_c = "110111"
        elif self.comp == "D-1":
            enc_c = "001110"
        elif self.comp == "A-1" or self.comp == "M-1":
            enc_c = "110010"
        elif self.comp == "D+A" or self.comp == "D+M":
            enc_c = "000010"
        elif self.comp == "D-A" or self.comp == "D-M":
            enc_c = "010011"
        elif self.comp == "A-D" or self.comp == "M-D":
            enc_c = "000111"
        elif self.comp == "D&A" or self.comp == "D&M":
            enc_c = "000000"
        elif self.comp == "D|A" or self.comp == "D|M":
            enc_c = "010101"
        else:
            raise NotImplementedError("{} not implemented".format(self.comp))

        return a + enc_c

    def _encode_destination(self):
        if self.dest is None:
            return "000"
        elif self.dest == "M":
            return "001"
        elif self.dest == "D":
            return "010"
        elif self.dest == "MD":
            return "011"
        elif self.dest == "A":
            return "100"
        elif self.dest == "AM":
            return "101"
        elif self.dest == "AD":
            return "110"
        elif self.dest == "AMD":
            return "111"
        else:
            raise NotImplementedError("{} not implemented".format(self.dest))

    def _encode_jump(self):
        if self.jmp is None:
            return "000"
        elif self.jmp == "JGT":
            return "001"
        elif self.jmp == "JEQ":
            return "010"
        elif self.jmp == "JGE":
            return "011"
        elif self.jmp == "JLT":
            return "100"
        elif self.jmp == "JNE":
            return "101"
        elif self.jmp == "JLE":
            return "110"
        elif self.jmp == "JMP":
            return "111"
        else:
            raise NotImplementedError("{} not implemented".format(self.jmp))

    def encode(self, **kwargs):
        encoded_instruction = "111"
        encoded_instruction += self._encode_comp()
        encoded_instruction += self._encode_destination()
        encoded_instruction += self._encode_jump()
        encoded_instruction += "\r\n"
        return encoded_instruction

    def __str__(self):
        return "C: {}={};{}\n{}".format(self.dest, self.comp, self.jmp, self.encode())

class AInstruction(Instruction):

    ADDR_WIDTH = 15

    def __init__(self, addr):
        self.addr = addr

    def encode(self, symtable):
        try:
            addr_int = int(self.addr)
        except ValueError:
            sym = self.addr
            addr_int = symtable.get(sym)
            if addr_int is None:
                addr_int = symtable.allocate_variable(sym)

        encoded_addr = bin(addr_int)[2:] # Strip 0b prefix
        return "0" + encoded_addr.zfill(AInstruction.ADDR_WIDTH) + "\r\n"

    def __str__(self):
        return "A: {}\n{}".format(self.addr, self.encode())


if __name__ == "__main__":
    instructions = ["@2", "@2222", " @3   ", " D=A   ", " D=D+A   ", " D;JGT   ", " 1;JGT   "]
    for inst in instructions:
        instr_obj = InstructionParser.parse(inst)
        print(instr_obj)