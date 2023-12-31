import glob
import os
import sys

COMMENT = '//'

class Parser(object):
    """Responsible for processing VM file and iterating through commands

    Args:
        object (_type_): _description_

    Returns:
        _type_: _description_
    """
    COMMAND_MAP = {
            'add': 'C_ARITHMETIC',
            'sub': 'C_ARITHMETIC',
            'neg': 'C_ARITHMETIC',
             'eq': 'C_ARITHMETIC',
             'gt': 'C_ARITHMETIC',
             'lt': 'C_ARITHMETIC',
            'and': 'C_ARITHMETIC',
             'or': 'C_ARITHMETIC',
            'not': 'C_ARITHMETIC',
           'push': 'C_PUSH',
            'pop': 'C_POP',
          'label': 'C_LABEL',
           'goto': 'C_GOTO',
        'if-goto': 'C_IF',
       'function': 'C_FUNCTION',
         'return': 'C_RETURN',
           'call': 'C_CALL'
    }

    def __init__(self, vm_filename):
        self.vm_filename = vm_filename
        self.vm_fh = open(vm_filename, 'r')
        self.curr_instruction = None
        self.init()

    def advance(self):
        self.curr_instruction = self.next_instruction
        self.next()

    @property
    def has_more_commands(self):
        return bool(self.next_instruction)

    @property
    def command_type(self):
        return self.COMMAND_MAP[self.curr_instruction[0].lower()]

    @property
    def arg1(self):
        '''Handle C_ARITHMETIC'''
        if self.command_type == 'C_ARITHMETIC':
            return self.get_arg_by_position(0)
        return self.get_arg_by_position(1)

    @property
    def arg2(self):
        '''C_PUSH, C_POP, C_FUNCTION, C_CALL'''
        return self.get_arg_by_position(2)

    def init(self):
        self.vm_fh.seek(0)
        line = self.vm_fh.readline().strip()
        while not self.is_instruction(line):
            line = self.vm_fh.readline().strip()
        self.next(line)

    def next(self, line=None):
        line = line if line is not None else self.vm_fh.readline().strip()
        self.next_instruction = line.split(COMMENT)[0].strip().split()

    def is_instruction(self, line):
        return line and not line.startswith(COMMENT)

    def get_arg_by_position(self, n):
        if len(self.curr_instruction) >= n+1:
            return self.curr_instruction[n]
        return None


class OutputCodeStream(object):
    """Responsible for writing the output asm files
    """

    SPECIAL_REGS = {
        'local': 'LCL',
        'argument': 'ARG',
        'this': 'THIS',
        'that': 'THAT',
        'pointer': 3,
        'temp': 5,
        'static': 16,
    }

    def __init__(self, asm_filename):
        self.asm = open(asm_filename, 'w')
        self.curr_file = None
        self.bool_count = 0 # Number of boolean comparisons so far

    def update_vm_file(self, vm_filename):
        self.curr_file = os.path.basename(vm_filename).replace('.vm', '')

    def write_arithmetic(self, operation):
        '''Apply operation to top of stack'''
        if operation not in ['neg', 'not']: # Binary operator
            self.pop_stack_to_D()
        self.decrement_SP()
        self.set_A_to_stack()

        if operation == 'add': # Arithmetic operators
            self.write('M=M+D')
        elif operation == 'sub':
            self.write('M=M-D')
        elif operation == 'and':
            self.write('M=M&D')
        elif operation == 'or':
            self.write('M=M|D')
        elif operation == 'neg':
            self.write('M=-M')
        elif operation == 'not':
            self.write('M=!M')
        elif operation in ['eq', 'gt', 'lt']: # Boolean operators
            self.write('D=M-D')
            self.write('@BOOL{}'.format(self.bool_count))

            if operation == 'eq':
                self.write('D;JEQ') # if x == y, x - y == 0
            elif operation == 'gt':
                self.write('D;JGT') # if x > y, x - y > 0
            elif operation == 'lt':
                self.write('D;JLT') # if x < y, x - y < 0

            self.set_A_to_stack()
            self.write('M=0') # False
            self.write('@ENDBOOL{}'.format(self.bool_count))
            self.write('0;JMP')

            self.write('(BOOL{})'.format(self.bool_count))
            self.set_A_to_stack()
            self.write('M=-1') # True

            self.write('(ENDBOOL{})'.format(self.bool_count))
            self.bool_count += 1
        else:
            raise ValueError("Invalid command {}!".format(operation))
        self.increment_SP()

    def write_push_pop(self, command, segment, index):
        self.resolve_address(segment, index)
        if command == 'C_PUSH': # load M[address] to D
            if segment == 'constant':
                self.write('D=A')
            else:
                self.write('D=M')
            self.push_D_to_stack()
        elif command == 'C_POP': # load D to M[address]
            self.write('D=A')
            self.write('@R13') # Store resolved address in R13
            self.write('M=D')
            self.pop_stack_to_D()
            self.write('@R13')
            self.write('A=M')
            self.write('M=D')
        else:
            raise ValueError("Invalid command {}!".format(command))


    def close(self):
        self.asm.close()

    def write(self, command):
        self.asm.write(command + '\n')

    def resolve_address(self, segment, index):
        '''Resolve address to A register'''
        address = self.SPECIAL_REGS.get(segment)
        if segment == 'constant':
            self.write('@' + str(index))
        elif segment == 'static':
            self.write('@' + self.curr_file + '.' + str(index))
        elif segment in ['pointer', 'temp']:
            self.write('@R' + str(address + int(index))) # Address is an int
        elif segment in ['local', 'argument', 'this', 'that']:
            self.write('@' + address) # Address is a string
            self.write('D=M')
            self.write('@' + str(index))
            self.write('A=D+A') # D is segment base
        else:
            raise ValueError("Invalid segment {}!".format(segment))

    def push_D_to_stack(self):
        '''Push from D onto top of stack, increment @SP'''
        self.write('@SP') # Get current stack pointer
        self.write('A=M') # Set address to current stack pointer
        self.write('M=D') # Write data to top of stack
        self.write('@SP') # Increment SP
        self.write('M=M+1')

    def pop_stack_to_D(self):
        '''Decrement @SP, pop from top of stack onto D'''
        self.write('@SP')
        self.write('M=M-1') # Decrement SP
        self.write('A=M') # Set address to current stack pointer
        self.write('D=M') # Get data from top of stack

    def decrement_SP(self):
        self.write('@SP')
        self.write('M=M-1')

    def increment_SP(self):
        self.write('@SP')
        self.write('M=M+1')

    def set_A_to_stack(self):
        self.write('@SP')
        self.write('A=M')


class Compiler(object):
    def __init__(self, vm_files, asm_file):
        self.vm_files = vm_files
        self.asm_file = asm_file
        self.output_code_stream = OutputCodeStream(self.asm_file)
        for vm_file in self.vm_files:
            self.compile(vm_file)
        self.output_code_stream.close()

    def compile(self, vm_file):
        parser = Parser(vm_file)
        self.output_code_stream.update_vm_file(vm_file)
        while parser.has_more_commands:
            parser.advance()
            if parser.command_type == 'C_PUSH':
                self.output_code_stream.write_push_pop('C_PUSH', parser.arg1, parser.arg2)
            elif parser.command_type == 'C_POP':
                self.output_code_stream.write_push_pop('C_POP', parser.arg1, parser.arg2)
            elif parser.command_type == 'C_ARITHMETIC':
                self.output_code_stream.write_arithmetic(parser.arg1)


if __name__ == '__main__':
    file_path = sys.argv[1]
    if os.path.isfile(file_path):
        asm_file = file_path.replace('.vm', '.asm')
        Compiler([file_path], asm_file)
    else:
        filename = os.path.basename(file_path)
        asm_file = file_path + "/" + filename + ".asm"
        file_paths = glob.glob(file_path + "/*.vm")
        Compiler(file_paths, asm_file)