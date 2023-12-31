from JackSubroutine import JackSubroutinesDeclaration
from helpers import indent

class InvalidClassDefinition(Exception):
    pass

class NotAClassVariableDeclaration(Exception):
    pass


class InvalidClassVariableDeclaration(Exception):
    pass



class JackClassVariableDeclaration:
    def __init__(self, tokens):
        self.tokens = tokens

    @classmethod
    def parse(cls, tokenizer):
        all_tokens = []

        # Static | field
        modifier = tokenizer.advance()
        if not (modifier.type_ == "keyword" and modifier.value in ["static", "field"]):
            raise NotAClassVariableDeclaration("Expected modifier: (static | field). Got: {}".format(modifier))
        
        # Type
        var_type = tokenizer.advance()
        if not ((var_type.type_ == "keyword" and var_type.value in ["int", "char", "boolean"]) \
            or (var_type.type_ == "identifier")):
            raise InvalidClassVariableDeclaration("Expected type: (int | char | boolean). Got: {}".format(var_type))
        
        # Var name
        var_name = tokenizer.advance()
        if not (var_name.type_ == "identifier"):
            raise InvalidClassVariableDeclaration("Expected variable name: identifier. Got: {}".format(var_name))

        all_tokens.append(modifier)
        all_tokens.append(var_type)
        all_tokens.append(var_name)

        # ; or ', var_name'
        next_token = tokenizer.advance()
        while not (next_token.type_ == "symbol" and next_token.value == ';'):
            
            # Handle ','
            if not (next_token.type_ == "symbol" and next_token.value == ','):
                raise InvalidClassVariableDeclaration("Expected ,. Got: {}".format(next_token))
            comma_token = next_token
            
            # Handle variable name
            var_name = tokenizer.advance()
            if not (var_name.type_ == "identifier"):
                raise InvalidClassVariableDeclaration("Expected variable name: identifier. Got: {}".format(var_name))
            
            all_tokens.append(comma_token)
            all_tokens.append(var_name)
            next_token = tokenizer.advance()
        
        # Add ';' token
        all_tokens.append(next_token)
        return JackClassVariableDeclaration(all_tokens)

    def serialize(self):
        result = "<classVarDec>\n"
        for token in self.tokens:
            result += "  {}\n".format(token.serialize())
        result += "</classVarDec>"
        return result

class JackClassVariablesDeclaration:
    def __init__(self, jack_variable_declarations):
        self.jack_variable_declarations = jack_variable_declarations

    @classmethod
    def parse(cls, tokenizer):
        var_decs = []
        try:
            while True:
                class_variable_declaration = JackClassVariableDeclaration.parse(tokenizer)
                var_decs.append(class_variable_declaration)
        except NotAClassVariableDeclaration:
            tokenizer.restoreLastToken()

        return JackClassVariablesDeclaration(var_decs)

    def serialize(self):
        result = ""
        for var_dec in self.jack_variable_declarations:
            result += var_dec.serialize() + "\n"
        return result[:-1]


class JackClass:
    def __init__(self, class_keyword, class_name, open_bracket, class_var_decs, subroutine_decs, close_bracket):
        self.class_keyword = class_keyword
        self.class_name = class_name
        self.open_bracket = open_bracket
        self.class_var_decs = class_var_decs
        self.subroutine_decs = subroutine_decs
        self.close_bracket = close_bracket

    @classmethod
    def parse(cls, tokenizer):
        # Class keyword
        class_keyword = tokenizer.advance()
        if not (class_keyword.type_ == "keyword" and class_keyword.value == "class"):
            raise InvalidClassDefinition("Expected keyword: class. Got {}".format(class_keyword))
        
        # Class name
        class_name = tokenizer.advance()
        if class_name.type_ != "identifier":
            raise InvalidClassDefinition("Expected identifier <class name>. Got {}".format(class_name))
        
        # Open bracket
        open_bracket = tokenizer.advance()
        if not (open_bracket.type_ == "symbol" and open_bracket.value == "{"):
            raise InvalidClassDefinition("Expected symbol {. Got {}".format(open_bracket))
        
        # Class variable declarations
        class_var_decs = JackClassVariablesDeclaration.parse(tokenizer)

        # Subroutines declarations
        subroutine_decs = JackSubroutinesDeclaration.parse(tokenizer)

        # Close bracket
        close_bracket = tokenizer.advance()
        if not (close_bracket.type_ == "symbol" and close_bracket.value == "}"):
            raise InvalidClassDefinition("Expected symbol }. Got %s" % close_bracket)

        return JackClass(class_keyword, class_name, open_bracket, class_var_decs, subroutine_decs, close_bracket)
    
    def serialize(self):
        return \
        """<class>
  {}
  {}
  {}
{}
{}
  {}
</class>
""".format(self.class_keyword.serialize(), self.class_name.serialize(), self.open_bracket.serialize(),\
     indent(self.class_var_decs.serialize()), indent(self.subroutine_decs.serialize()), self.close_bracket.serialize())

class ParseTree:
    def __init__(self, jack_class):
        self.jack_class = jack_class

class JackParser:
    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
    
    def generate_parse_tree(self):
        return JackClass.parse(self.tokenizer)
