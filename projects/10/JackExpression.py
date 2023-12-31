from helpers import indent

class NotAStatement(Exception):
    pass

class InvalidExpression(Exception):
    pass

class InvaledSubroutineCall(Exception):
    pass

class ExpressionList:
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
            # Expression
            tokenizer.restoreLastToken()
            expression = JackExpression.parse(tokenizer)
            all_elements.append(expression)

            # Handle (, expression) | ')'
            next_token = tokenizer.advance()
            while not (next_token.type_ == "symbol" and next_token.value == ')'):

                # ,
                if not (next_token.type_ == "symbol" and next_token.value == ','):
                    raise InvaledSubroutineCall("Expected symbol: ','. Got: {}".format(next_token))
                all_elements.append(next_token)

                # Expression
                expression = JackExpression.parse(tokenizer)
                all_elements.append(expression)

                next_token = tokenizer.advance()
            tokenizer.restoreLastToken()

        return ExpressionList(all_elements)
    
    def serialize(self):
        result = "<expressionList>\n"
        for elem in self.elements:
            if isinstance(elem, JackExpression):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</expressionList>"
        return result

class JackSubroutineCall:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        # Handle variable name
        subroutine_name = tokenizer.advance()
        if not (subroutine_name.type_ == "identifier"):
            raise InvaledSubroutineCall("Expected variable name: identifier. Got: {}".format(subroutine_name))
        elements.append(subroutine_name)

        # Handle .subroutine
        next_token = tokenizer.advance()
        if next_token.type_ == "symbol" and next_token.value == '.':
            elements.append(next_token)
            
            # Handle variable name
            subroutine_name = tokenizer.advance()
            if not (subroutine_name.type_ == "identifier"):
                raise InvaledSubroutineCall("Expected variable name: identifier. Got: {}".format(subroutine_name))
            elements.append(subroutine_name)
        else:
            tokenizer.restoreLastToken()
        
        # Handle ( expression list )
        next_token = tokenizer.advance()
        if not (next_token.type_ == "symbol" and next_token.value == '('):
            raise InvaledSubroutineCall("Expected (. Got {}". format(next_token))
        elements.append(next_token)

        expression_list = ExpressionList.parse(tokenizer)
        elements.append(expression_list)
        
        # )
        next_token = tokenizer.advance()
        if not (next_token.type_ == "symbol" and next_token.value == ')'):
            raise InvaledSubroutineCall("Expected ). Got {}". format(next_token))
        elements.append(next_token)

        return JackSubroutineCall(elements)

    def serialize(self):
        result = ""
        for elem in self.elements:
            result += elem.serialize() + "\n"
        return result

class JackTerm:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []
        token = tokenizer.advance()

        # ( expression )
        if token.type_ == "symbol" and token.value == "(":
            elements.append(token)
            
            expression = JackExpression.parse(tokenizer)
            elements.append(expression)
            
            # )
            next_token = tokenizer.advance()
            if not (next_token.type_ == "symbol" and next_token.value == ')'):
                raise InvaledSubroutineCall("Expected ). Got {}". format(next_token))
            elements.append(next_token)
            return JackTerm(elements)
        
        # unaryop term
        elif token.type_ == "symbol" and token.value in ['-', '~']:
            elements.append(token)

            term = JackTerm.parse(tokenizer)
            elements.append(term)
            return JackTerm(elements) 

        # no other symbols allowed
        elif token.type_ == 'symbol':
            raise InvalidExpression("Expected expression: Got symbol: {}".format(token))
        
        # constant keyword
        if token.type_ == 'keyword' and token.value in ["true", "false", "null", "this"]:
            return JackTerm([token])
        elif token.type_ == 'keyword':
            raise InvalidExpression("Expected expression: Got symbol: {}".format(token))

        next_token = tokenizer.advance()

        # name.subroutine()
        if next_token.type_ == "symbol" and next_token.value == ".":
            tokenizer.restore2LastTokens()
            subroutine_call = JackSubroutineCall.parse(tokenizer)
            return JackTerm([subroutine_call])
        
        # name[]
        elif next_token.type_ == "symbol" and next_token.value == "[":
            elements.append(token)
            elements.append(next_token)
            expression = JackExpression.parse(tokenizer)
            elements.append(expression)
            next_token = tokenizer.advance()
            if not (next_token.type_ == "symbol" and next_token.value == ']'):
                raise InvalidExpression("Expected: ]. Got: {}".format(next_token))
            elements.append(next_token)
            return JackTerm(elements)

        else:
            tokenizer.restoreLastToken()
            return JackTerm([token])

    def serialize(self):
        result = "<term>\n"
        for elem in self.elements:
            if isinstance(elem, (JackExpression, ExpressionList, JackSubroutineCall, JackTerm)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</term>"
        return result

class JackExpression:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        # term
        term = JackTerm.parse(tokenizer)
        elements.append(term)

        # (op term)?
        next_token = tokenizer.advance()
        while next_token.type_ == "symbol" and next_token.value in ["+", "-", "*", "/", "&", "|", "<", ">", "="]:
            elements.append(next_token) # op

            term = JackTerm.parse(tokenizer)
            elements.append(term)

            next_token = tokenizer.advance()
        tokenizer.restoreLastToken()
        return JackExpression(elements)
        
    def serialize(self):
        result = "<expression>\n"
        for elem in self.elements:
            if isinstance(elem, JackTerm):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</expression>"
        return result

        
