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
    
    COMMANDS_MAP = {
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
        self.vm = open(vm_filename, 'r')
        self.EOF = False
        self.curr_instruction = None
        self.init()

    def advance(self):
        self.curr_instruction = self.next_instruction
        self.next()

    @property
    def has_more_commands(self):
        return not self.EOF

    @property
    def command_type(self):
        return self.COMMANDS_MAP[self.curr_instruction[0].lower()]

    @property
    def arg1(self):
        if self.command_type == 'C_ARITHMETIC':
            return self.get_arg_by_position(0)
        return self.get_arg_by_position(1)

    @property
    def arg2(self):
        '''C_PUSH, C_POP, C_FUNCTION, C_CALL'''
        return self.get_arg_by_position(2)

    def close(self):
        self.vm.close()

    def init(self):
        self.vm.seek(0)
        self.next()

    def next(self, line=None):
        instruction_found = False
        while not instruction_found and not self.EOF:
            line = self.vm.readline()
            if not line:
                self.EOF = True
                break
            line = line.strip()
            if self.is_instruction(line):
                self.next_instruction = line.rstrip(COMMENT).strip().split()
                instruction_found = True

    def is_instruction(self, line):
        return line and not line.startswith(COMMENT)

    def get_arg_by_position(self, n):
        if len(self.curr_instruction) >= n+1:
            return self.curr_instruction[n]
        return None
