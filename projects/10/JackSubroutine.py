from JackTokenizer import EndOfFile
from JackStatements import JackStatements
from helpers import indent

class NotASubroutineDeclaration(Exception):
    pass

class InvalidSubroutineDeclaration(Exception):
    pass

class NotAVariableDeclaration(Exception):
    pass

class InvalidVariableDeclaration(Exception):
    pass


class JackParametersList:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        all_elements = []

        # ) or '(type var_name) (, type var_name)'
        next_token = tokenizer.advance()
        if next_token.type_ == "symbol" and next_token.value == ')':
            tokenizer.restoreLastToken()
        else:
            # Type
            param_type = next_token
            if not ((param_type.type_ == "keyword" and param_type.value in ["int", "char", "boolean"]) \
                or (param_type.type_ == "identifier")):
                raise InvalidSubroutineDeclaration("Expected type: (int | char | boolean | className). Got: {}".format(param_type))
            all_elements.append(param_type)

            # Parameter name
            param_name = tokenizer.advance()
            if not (param_name.type_ == "identifier"):
                raise InvalidSubroutineDeclaration("Expected param name: identifier. Got: {}".format(param_name))
            all_elements.append(param_name)

            # Handle (, type var_name) | ')'
            next_token = tokenizer.advance()
            while not (next_token.type_ == "symbol" and next_token.value == ')'):
                if not (next_token.type_ == "symbol" and next_token.value == ','):
                    raise InvalidSubroutineDeclaration("Expected symbol: ','. Got: {}".format(next_token))
                all_elements.append(next_token)

                # Type
                param_type = tokenizer.advance()
                if not ((param_type.type_ == "keyword" and param_type.value in ["int", "char", "boolean"]) \
                    or (param_type.type_ == "identifier")):
                    raise InvalidSubroutineDeclaration("Expected type: (int | char | boolean | className). Got: {}".format(param_type))
                all_elements.append(param_type)

                # Parameter name
                param_name = tokenizer.advance()
                if not (param_name.type_ == "identifier"):
                    raise InvalidSubroutineDeclaration("Expected param name: identifier. Got: {}".format(param_name))
                all_elements.append(param_name)

                next_token = tokenizer.advance()
            tokenizer.restoreLastToken()

        return JackParametersList(all_elements)

    def serialize(self):
        result = "<parameterList>\n"
        for elem in self.elements:
            result += "  {}\n".format(elem.serialize())
        result += "</parameterList>"
        return result



class JackSubroutineDeclaration:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        all_elements = []

        # constructor | function | method
        func_type = tokenizer.advance()
        if not (func_type.type_ == "keyword" and func_type.value in ["constructor", "function", "method"]):
            raise NotASubroutineDeclaration("Expected modifier: (constructor | function | method). Got: {}".format(func_type))
        
        # Type
        subroutine_name_type = tokenizer.advance()
        if not ((subroutine_name_type.type_ == "keyword" and subroutine_name_type.value in ["int", "char", "boolean", "void"]) \
            or (subroutine_name_type.type_ == "identifier")):
            raise InvalidSubroutineDeclaration("Expected type: (int | char | boolean | void | className). Got: {}".format(subroutine_name_type))
        
        # Subroutine name
        subroutine_name = tokenizer.advance()
        if not (subroutine_name.type_ == "identifier"):
            raise InvalidSubroutineDeclaration("Expected variable name: identifier. Got: {}".format(subroutine_name))
        
        # (
        open_parenthesis = tokenizer.advance()
        if not (open_parenthesis.type_ == "symbol" and open_parenthesis.value == '('):
            raise InvalidSubroutineDeclaration("Expected (. Got: {}".format(open_parenthesis))
        
        all_elements.append(func_type)
        all_elements.append(subroutine_name_type)
        all_elements.append(subroutine_name)
        all_elements.append(open_parenthesis)

        # Parameters list
        param_list = JackParametersList.parse(tokenizer)
        all_elements.append(param_list)

        # )
        close_parenthesis = tokenizer.advance()
        if not (close_parenthesis.type_ == "symbol" and close_parenthesis.value == ')'):
            raise InvalidSubroutineDeclaration("Expected ). Got: {}".format(close_parenthesis))
        all_elements.append(close_parenthesis)

        subroutine_body = JackSubroutinesBody.parse(tokenizer)
        all_elements.append(subroutine_body)

        return JackSubroutineDeclaration(all_elements)

    def serialize(self):
        result = "<subroutineDec>\n"
        for elem in self.elements:
            if isinstance(elem, (JackSubroutinesBody, JackParametersList)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</subroutineDec>"
        return result

class JackSubroutinesDeclaration:
    def __init__(self, subroutines_declarations):
        self.subroutines_declarations = subroutines_declarations

    @classmethod
    def parse(cls, tokenizer):
        subroutine_decs = []
        try:
            while True:
                subroutines_declaration = JackSubroutineDeclaration.parse(tokenizer)
                subroutine_decs.append(subroutines_declaration)
        except NotASubroutineDeclaration:
            tokenizer.restoreLastToken()

        return JackSubroutinesDeclaration(subroutine_decs)

    def serialize(self):
        result = ""
        for sub_dec in self.subroutines_declarations:
            result += sub_dec.serialize() + "\n"
        return result


class JackVariableDeclaration:
    def __init__(self, tokens):
        self.tokens = tokens

    @classmethod
    def parse(cls, tokenizer):
        all_tokens = []

        # var
        var = tokenizer.advance()
        if not (var.type_ == "keyword" and var.value == "var"):
            raise NotAVariableDeclaration("Expected var. Got: {}".format(var))
        all_tokens.append(var)

        # Type
        var_type = tokenizer.advance()
        if not ((var_type.type_ == "keyword" and var_type.value in ["int", "char", "boolean"]) \
            or (var_type.type_ == "identifier")):
            raise InvalidVariableDeclaration("Expected type: (int | char | boolean). Got: {}".format(var_type))
        all_tokens.append(var_type)

        # Var name
        var_name = tokenizer.advance()
        if not (var_name.type_ == "identifier"):
            raise InvalidVariableDeclaration("Expected variable name: identifier. Got: {}".format(var_name))
        all_tokens.append(var_name)

        # ; or ', var_name'
        next_token = tokenizer.advance()
        while not (next_token.type_ == "symbol" and next_token.value == ';'):
            
            # Handle ','
            if not (next_token.type_ == "symbol" and next_token.value == ','):
                raise InvalidVariableDeclaration("Expected ,. Got: {}".format(next_token))
            comma_token = next_token
            
            # Handle variable name
            var_name = tokenizer.advance()
            if not (var_name.type_ == "identifier"):
                raise InvalidVariableDeclaration("Expected variable name: identifier. Got: {}".format(var_name))
            
            all_tokens.append(comma_token)
            all_tokens.append(var_name)
            next_token = tokenizer.advance()
        
        # Add ';' token
        all_tokens.append(next_token)
        return JackVariableDeclaration(all_tokens)

    def serialize(self):
        result = "<varDec>\n"
        for token in self.tokens:
            result += "  {}\n".format(token.serialize())
        result += "</varDec>"
        return result

class JackVariablesDeclaration:
    def __init__(self, jack_variable_declarations):
        self.jack_variable_declarations = jack_variable_declarations

    @classmethod
    def parse(cls, tokenizer):
        var_decs = []
        try:
            while True:
                class_variable_declaration = JackVariableDeclaration.parse(tokenizer)
                var_decs.append(class_variable_declaration)
        except NotAVariableDeclaration:
            tokenizer.restoreLastToken()

        return JackVariablesDeclaration(var_decs)

    def serialize(self):
        result = ""
        for var_dec in self.jack_variable_declarations:
            result += var_dec.serialize() + "\n"
        return result



class JackSubroutinesBody:
    def __init__(self, open_bracket, var_decs, statements, close_bracket):
        self.open_bracket = open_bracket
        self.var_decs = var_decs
        self.statements = statements
        self.close_bracket = close_bracket

    @classmethod
    def parse(cls, tokenizer):
        # {
        open_bracket = tokenizer.advance()
        if not (open_bracket.type_ == "symbol" and open_bracket.value == '{'):
            raise InvalidSubroutineDeclaration("Expected {. Got: %s" % (open_bracket, ))

        # varDecs
        var_decs = JackVariablesDeclaration.parse(tokenizer)

        # statements
        statements = JackStatements.parse(tokenizer)

        # }
        close_bracket = tokenizer.advance()
        if not (close_bracket.type_ == "symbol" and close_bracket.value == '}'):
            raise InvalidSubroutineDeclaration("Expected }. Got: %s" % (close_bracket, ))

        return JackSubroutinesBody(open_bracket, var_decs, statements, close_bracket)

    def serialize(self):
        result = "<subroutineBody>\n"
        result += '  ' + self.open_bracket.serialize() + "\n"
        result += indent(self.var_decs.serialize()) + "\n"
        result += indent(self.statements.serialize()) + "\n"
        result += '  ' + self.close_bracket.serialize() + "\n"
        result += "</subroutineBody>"
        return result