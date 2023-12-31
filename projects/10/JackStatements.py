from JackExpression import JackExpression, JackSubroutineCall
from helpers import indent

class NotAStatement(Exception):
    pass

class InvalidStatement(Exception):
    pass


class IfStatement:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        if_keyword = tokenizer.advance()
        elements.append(if_keyword)
        
        # (
        open_parenthesis = tokenizer.advance()
        if not (open_parenthesis.type_ == "symbol" and open_parenthesis.value == '('):
            raise InvalidStatement("Expected (. Got: {}".format(open_parenthesis))
        elements.append(open_parenthesis)

        # Expression
        expression  = JackExpression.parse(tokenizer)
        elements.append(expression)

        # )
        close_parenthesis = tokenizer.advance()
        if not (close_parenthesis.type_ == "symbol" and close_parenthesis.value == ')'):
            raise InvalidStatement("Expected ). Got: {}".format(close_parenthesis))
        elements.append(close_parenthesis)

        # {
        open_bracket = tokenizer.advance()
        if not (open_bracket.type_ == "symbol" and open_bracket.value == '{'):
            raise InvalidStatement("Expected {. Got: %s" % (open_bracket, ))
        elements.append(open_bracket)

        # statements
        statements = JackStatements.parse(tokenizer)
        elements.append(statements)

        # }
        close_bracket = tokenizer.advance()
        if not (close_bracket.type_ == "symbol" and close_bracket.value == '}'):
            raise InvalidStatement("Expected }. Got: %s" % (close_bracket, ))
        elements.append(close_bracket)

        # else?
        else_keyword = tokenizer.advance()
        if not (else_keyword.type_ == "keyword" and else_keyword.value == 'else'):
            tokenizer.restoreLastToken()
        else:
            elements.append(else_keyword)

            # {
            open_bracket = tokenizer.advance()
            if not (open_bracket.type_ == "symbol" and open_bracket.value == '{'):
                raise InvalidStatement("Expected {. Got: %s" % (open_bracket, ))
            elements.append(open_bracket)

            # statements
            statements = JackStatements.parse(tokenizer)
            elements.append(statements)

            # }
            close_bracket = tokenizer.advance()
            if not (close_bracket.type_ == "symbol" and close_bracket.value == '}'):
                raise InvalidStatement("Expected }. Got: %s" % (close_bracket, ))
            elements.append(close_bracket)

        return IfStatement(elements)
    
    def serialize(self):
        result = "<ifStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackExpression)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</ifStatement>"
        return result


class WhileStatement:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        while_keyword = tokenizer.advance()
        elements.append(while_keyword)
        
        # (
        open_parenthesis = tokenizer.advance()
        if not (open_parenthesis.type_ == "symbol" and open_parenthesis.value == '('):
            raise InvalidStatement("Expected (. Got: {}".format(open_parenthesis))
        elements.append(open_parenthesis)

        # Expression
        expression  = JackExpression.parse(tokenizer)
        elements.append(expression)

        # )
        close_parenthesis = tokenizer.advance()
        if not (close_parenthesis.type_ == "symbol" and close_parenthesis.value == ')'):
            raise InvalidStatement("Expected ). Got: {}".format(close_parenthesis))
        elements.append(close_parenthesis)

        # {
        open_bracket = tokenizer.advance()
        if not (open_bracket.type_ == "symbol" and open_bracket.value == '{'):
            raise InvalidStatement("Expected {. Got: %s" % (open_bracket, ))
        elements.append(open_bracket)

        # statements
        statements = JackStatements.parse(tokenizer)
        elements.append(statements)

        # }
        close_bracket = tokenizer.advance()
        if not (close_bracket.type_ == "symbol" and close_bracket.value == '}'):
            raise InvalidStatement("Expected }. Got: %s" % (close_bracket, ))
        elements.append(close_bracket)

        return WhileStatement(elements)
    
    def serialize(self):
        result = "<whileStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackExpression)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</whileStatement>"
        return result

class ReturnStatement:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        return_keyword = tokenizer.advance()
        elements.append(return_keyword)
        
        # ; or 'expression;'
        next_token = tokenizer.advance()
        if not (next_token.type_ == "symbol" and next_token.value == ';'):
            tokenizer.restoreLastToken()
            expression = JackExpression.parse(tokenizer)
            elements.append(expression)
            next_token = tokenizer.advance()

        if not (next_token.type_ == "symbol" and next_token.value == ';'):
            raise InvalidStatement("Expected ;. Got: {}".format(next_token))
        elements.append(next_token)
        
        return ReturnStatement(elements)
    
    def serialize(self):
        result = "<returnStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackExpression)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</returnStatement>"
        return result


class LetStatement:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        let_keyword = tokenizer.advance()
        elements.append(let_keyword)
        
        # Handle variable name
        var_name = tokenizer.advance()
        if not (var_name.type_ == "identifier"):
            raise InvalidStatement("Expected variable name: identifier. Got: {}".format(var_name))
        elements.append(var_name)

        # Handle [ expression ]
        next_token = tokenizer.advance()
        if next_token.type_ == "symbol" and next_token.value == '[':
            elements.append(next_token)
            expression = JackExpression.parse(tokenizer)
            elements.append(expression)
            next_token = tokenizer.advance()
            if not (next_token.type_ == "symbol" and next_token.value == ']'):
                raise InvalidStatement("Expected: ]. Got: {}".format(next_token))
            elements.append(next_token)
        else:
            tokenizer.restoreLastToken()
        
        # Handle =
        eq_token = tokenizer.advance()
        if not (eq_token.type_ == "symbol" and eq_token.value == '='):
            raise InvalidStatement("Expected '='. Got {}".format(eq_token))
        elements.append(eq_token)
        
        # expression
        expression = JackExpression.parse(tokenizer)
        elements.append(expression)

        # Handle ;
        next_token = tokenizer.advance()
        if not (next_token.type_ == "symbol" and next_token.value == ';'):
            raise InvalidStatement("Expected ';'. Got {}".format(next_token))
        elements.append(next_token)
        
        return LetStatement(elements)
    
    def serialize(self):
        result = "<letStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackExpression)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</letStatement>"
        return result

class DoStatement:
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, tokenizer):
        elements = []

        do_keyword = tokenizer.advance()
        elements.append(do_keyword)
        
        # Call
        subroutine_call = JackSubroutineCall.parse(tokenizer)
        elements.append(subroutine_call)
        
        # Handle ;
        next_token = tokenizer.advance()
        if not (next_token.type_ == "symbol" and next_token.value == ';'):
            raise InvalidStatement("Expected ';'. Got {}".format(next_token))
        elements.append(next_token)

        return DoStatement(elements)
    
    def serialize(self):
        result = "<doStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackSubroutineCall)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</doStatement>"
        return result


class JackStatement:
    KeywordToJackStatement = {
        "if" : IfStatement,
        "while": WhileStatement,
        "return": ReturnStatement,
        "let": LetStatement,
        "do": DoStatement
    }

    @classmethod
    def parse(cls, tokenizer):
        # let | if | while | do | return
        statement_keyword = tokenizer.advance()
        if not (statement_keyword.type_ == "keyword" and statement_keyword.value in ["let", "if", "while", "do", "return"]):
            raise NotAStatement("Expected statement: (let | if | while | do | return). Got: {}".format(statement_keyword))
        tokenizer.restoreLastToken()
        
        return JackStatement.KeywordToJackStatement[statement_keyword.value].parse(tokenizer)


class JackStatements:
    def __init__(self, statements):
        self.statements = statements

    @classmethod
    def parse(cls, tokenizer):
        statements = []
        try:
            while True:
                statement = JackStatement.parse(tokenizer)
                statements.append(statement)
        except NotAStatement:
            tokenizer.restoreLastToken()

        return JackStatements(statements)

    def serialize(self):
        result = "<statements>\n"
        for statement in self.statements:
            result += indent(statement.serialize()) + "\n"
        result += "</statements>"
        return result
