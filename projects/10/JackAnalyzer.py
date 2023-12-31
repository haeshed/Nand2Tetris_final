import sys
import os
import glob
from JackTokenizer import JackTokenizer, JackToken
from JackParser import JackParser

class JackAnalyzer:
    def __init__(self, jack_file):
        self.jack_file = jack_file
        self.xml_tree_file = jack_file.replace('.jack', '.xml')
        self.jack_file_h = open(self.jack_file, 'r')
        tokenizer = JackTokenizer(self.jack_file_h)
        self.parser = JackParser(tokenizer)


    def generate_jack_xml(self):
        parse_tree = self.parser.generate_parse_tree()
        return parse_tree.serialize()
    
    def write_jack_xml(self):
        with open(self.xml_tree_file, "w") as fh:
            fh.write(self.generate_jack_xml())

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
        jack_analyzer = JackAnalyzer(jack_file)
        xml = jack_analyzer.write_jack_xml()