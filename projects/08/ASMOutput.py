import glob
import os
import sys
from VMParser import Parser

COMMENT = '//'

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
        self.line_count = 0
        self.boolean_cmp_count = 0 # Boolean comparisons done so far
        self.func_call_count = 0 # Function calls done so far

    def init(self):
        self.write('@256')
        self.write('D=A')
        self.write('@SP')
        self.write('M=D')
        self.write_call('Sys.init', 0)

    def update_vm_file(self, vm_filename):
        self.curr_file = os.path.basename(vm_filename).replace('.vm', '')

    def write_arithmetic(self, operation):
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
            self.write('@BOOL{}'.format(self.boolean_cmp_count))

            if operation == 'eq':
                self.write('D;JEQ') # if x == y, x - y == 0
            elif operation == 'gt':
                self.write('D;JGT') # if x > y, x - y > 0
            elif operation == 'lt':
                self.write('D;JLT') # if x < y, x - y < 0

            self.set_A_to_stack()
            self.write('M=0') # False
            self.write('@ENDBOOL{}'.format(self.boolean_cmp_count))
            self.write('0;JMP')

            self.write('(BOOL{})'.format(self.boolean_cmp_count), is_code=False)
            self.set_A_to_stack()
            self.write('M=-1') # True

            self.write('(ENDBOOL{})'.format(self.boolean_cmp_count), is_code=False)
            self.boolean_cmp_count += 1
        else:
            ValueError('{} is an invalid instruction'.format(operation))
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
            ValueError('{} is an invalid command'.format(command))

    def write_label(self, label):
        self.write('({}${})'.format(self.curr_file, label), is_code=False)

    def write_goto(self, label):
        self.write('@{}${}'.format(self.curr_file, label))
        self.write('0;JMP')

    def write_if(self, label):
        self.pop_stack_to_D()
        self.write('@{}${}'.format(self.curr_file, label))
        self.write('D;JNE')

    def write_function(self, function_name, num_locals):
        self.write('({})'.format(function_name), is_code=False)
        for _ in range(num_locals): # Initialize local vars to 0
            self.write('D=0')
            self.push_D_to_stack()

    def write_call(self, function_name, num_args):
        ret_label = function_name + 'RET' +  str(self.func_call_count) # Unique return label
        self.func_call_count += 1

        # push return-address
        self.write('@' + ret_label)
        self.write('D=A')
        self.push_D_to_stack()

        # push LCL
        # push ARG
        # push THIS
        # push THAT
        for address in ['@LCL', '@ARG', '@THIS', '@THAT']:
            self.write(address)
            self.write('D=M')
            self.push_D_to_stack()

        # LCL = SP
        self.write('@SP')
        self.write('D=M')
        self.write('@LCL')
        self.write('M=D')

        # ARG = SP-n-5
        self.write('@' + str(num_args + 5))
        self.write('D=D-A')
        self.write('@ARG')
        self.write('M=D')

        # goto f
        self.write('@' + function_name)
        self.write('0;JMP')

        # (return_address)
        self.write('({})'.format(ret_label), is_code=False)

    def write_return(self):
        # Temporary variables
        FRAME = 'R13'
        RET = 'R14'

        # FRAME = LCL
        self.write('@LCL')
        self.write('D=M')
        self.write('@' + FRAME)
        self.write('M=D')

        # RET = *(FRAME-5)
        # Can't be included in iterator b/c value will be overwritten if num_args=0
        self.write('@' + FRAME)
        self.write('D=M') # Save start of frame
        self.write('@5')
        self.write('D=D-A') # Adjust address
        self.write('A=D') # Prepare to load value at address
        self.write('D=M') # Store value
        self.write('@' + RET)
        self.write('M=D') # Save value

        # *ARG = pop()
        self.pop_stack_to_D()
        self.write('@ARG')
        self.write('A=M')
        self.write('M=D')

        # SP = ARG+1
        self.write('@ARG')
        self.write('D=M')
        self.write('@SP')
        self.write('M=D+1')

        # THAT = *(FRAME-1)
        # THIS = *(FRAME-2)
        # ARG = *(FRAME-3)
        # LCL = *(FRAME-4)
        offset = 1
        for address in ['@THAT', '@THIS', '@ARG', '@LCL']:
            self.write('@' + FRAME)
            self.write('D=M') # Save start of frame
            self.write('@' + str(offset))
            self.write('D=D-A') # Adjust address
            self.write('A=D') # Prepare to load value at address
            self.write('D=M') # Store value
            self.write(address)
            self.write('M=D') # Save value
            offset += 1

        # goto RET
        self.write('@' + RET)
        self.write('A=M')
        self.write('0;JMP')

    def write(self, command, is_code=True):
        self.asm.write(command)
        if is_code:
            self.line_count += 1
        self.asm.write('\n')

    def close(self):
        self.asm.close()

    def resolve_address(self, segment, index):
        '''Resolve address to A register'''
        address = self.SPECIAL_REGS.get(segment)
        if segment == 'constant':
            self.write('@' + str(index))
        elif segment == 'static':
            self.write('@' + self.curr_file + '.' + str(index))
        elif segment in ['pointer', 'temp']:
            self.write('@R' + str(address + index)) # Address is an int
        elif segment in ['local', 'argument', 'this', 'that']:
            self.write('@' + address) # Address is a string
            self.write('D=M')
            self.write('@' + str(index))
            self.write('A=D+A') # D is segment base
        else:
            ValueError('{} is an invalid segment'.format(segment))

    def push_D_to_stack(self):
        '''Push from D onto top of stack, increment @SP'''
        self.write('@SP') # Get current stack pointer
        self.write('A=M') # Set address to current stack pointer
        self.write('M=D') # Write data to top of stack
        self.increment_SP()

    def pop_stack_to_D(self):
        '''Decrement @SP, pop from top of stack onto D'''
        self.decrement_SP()
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
