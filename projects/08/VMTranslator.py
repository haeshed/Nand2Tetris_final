import glob
import os
import sys
from VMParser import Parser
from ASMOutput import OutputCodeStream

COMMENT = '//'

class Compiler(object):
    def __init__(self, vm_files, asm_file, should_bootstrap):
        self.vm_files = vm_files
        self.asm_file = asm_file
        self.cw = OutputCodeStream(self.asm_file)
        if should_bootstrap:
            self.cw.init()
        for vm_file in self.vm_files:
            self.compile(vm_file)
        self.cw.close()

    def compile(self, vm_file):
        parser = Parser(vm_file)
        self.cw.update_vm_file(vm_file)
        while parser.has_more_commands:
            parser.advance()
            self.cw.write('// ' + ' '.join(parser.curr_instruction), is_code=False)
            if parser.command_type == 'C_PUSH':
                self.cw.write_push_pop('C_PUSH', parser.arg1, int(parser.arg2))
            elif parser.command_type == 'C_POP':
                self.cw.write_push_pop('C_POP', parser.arg1, int(parser.arg2))
            elif parser.command_type == 'C_ARITHMETIC':
                self.cw.write_arithmetic(parser.arg1)
            elif parser.command_type == 'C_LABEL':
                self.cw.write_label(parser.arg1)
            elif parser.command_type == 'C_GOTO':
                self.cw.write_goto(parser.arg1)
            elif parser.command_type == 'C_IF':
                self.cw.write_if(parser.arg1)
            elif parser.command_type == 'C_FUNCTION':
                self.cw.write_function(parser.arg1, int(parser.arg2))
            elif parser.command_type == 'C_CALL':
                self.cw.write_call(parser.arg1, int(parser.arg2))
            elif parser.command_type == 'C_RETURN':
                self.cw.write_return()
        parser.close()


if __name__ == '__main__':
    file_path = sys.argv[1]
    if os.path.isfile(file_path):
        asm_file = file_path.replace('.vm', '.asm')
        Compiler([file_path], asm_file, should_bootstrap=False)
    else:
        filename = os.path.basename(file_path)
        asm_file = file_path + "/" + filename + ".asm"
        file_paths = glob.glob(file_path + "/*.vm")
        Compiler(file_paths, asm_file, should_bootstrap=True)