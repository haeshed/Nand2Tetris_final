import sys
import os
import glob
from JackTokenizer import JackTokenizer, JackToken
from JackParser import JackParser
from JackSymbolTable import ClassSymbolTable, SubroutineSymbolTable
from VMWriter import VMWriter

class JackCompiler:
    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.vm_file = jack_file.replace('.jack', '.vm')
        
        self.jack_file_h = open(self.jack_file, 'r')
        tokenizer = JackTokenizer(self.jack_file_h)
        self.parser = JackParser(tokenizer)

        self.vm_file_fh = open(self.vm_file, "w")
        self.vm_writer = VMWriter(self.vm_file_fh)

    def generate_jack_xml(self):
        parse_tree = self.parser.generate_parse_tree()
        return parse_tree.serialize()
    
    def write_jack_xml(self):
        with open(self.xml_tree_file, "w") as fh:
            fh.write(self.generate_jack_xml())
    
    def compile(self):
        jack_class = self.parser.generate_parse_tree()
        jack_class.compile(self.vm_writer)

    def close(self):
        self.jack_file_h.close()

if __name__ == '__main__':
    file_path = sys.argv[1]
    if os.path.isfile(file_path):
        jack_files = [file_path]
    else:
        filename = os.path.basename(file_path)
        jack_files = glob.glob(file_path + "/*.jack")

    for jack_file in jack_files:
        jack_compiler = JackCompiler(jack_file)
        jack_compiler.compile()