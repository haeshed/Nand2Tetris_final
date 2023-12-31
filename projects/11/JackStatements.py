from JackExpression import JackExpression, JackSubroutineCall
from JackTokenizer import JackToken
from JackSymbolTable import searchSymbol
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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        lbl_true = class_symtable.generateLabel()
        lbl_false = class_symtable.generateLabel()
        lbl_cont = class_symtable.generateLabel()
        cond_expr = self.elements[2]
        statements = self.elements[5]
        if len(self.elements) >= 9:
            else_statements = self.elements[9]
        else:
            else_statements = None

        cond_expr.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeIfGoto(lbl_true)
        vm_writer.writeGoto(lbl_false)
        vm_writer.writeLabel(lbl_true)
        statements.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeGoto(lbl_cont)
        vm_writer.writeLabel(lbl_false)
        if else_statements:
            else_statements.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeLabel(lbl_cont)


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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        lbl_while = class_symtable.generateLabel()
        lbl_cont = class_symtable.generateLabel()
        cond_expr = self.elements[2]
        statements = self.elements[5]

        vm_writer.writeLabel(lbl_while)
        cond_expr.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeUnaryOp("~")
        vm_writer.writeIfGoto(lbl_cont)
        statements.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeGoto(lbl_while)
        vm_writer.writeLabel(lbl_cont)



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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        if not (isinstance(self.elements[1], JackToken) and self.elements[1].value == ';'):
            jack_expression = self.elements[1]
            jack_expression.compile(vm_writer, class_symtable, subroutine_symtable)
        else:
            vm_writer.writePush("constant", 0)
        vm_writer.writeReturn()

class LetStatement:
    def __init__(self, elements, is_array_assignment):
        self.elements = elements
        self.is_array_assignment = is_array_assignment

    @classmethod
    def parse(cls, tokenizer):
        elements = []
        is_array_assignment = False

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
            is_array_assignment = True
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
        
        return LetStatement(elements, is_array_assignment)
    
    def serialize(self):
        result = "<letStatement>\n"
        for elem in self.elements:
            if isinstance(elem, (JackStatements, JackExpression)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</letStatement>"
        return result
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        if self.is_array_assignment:
            arr = self.elements[1]
            index = self.elements[3]
            rvalue = self.elements[6]
            arr_sym = searchSymbol(arr.value, subroutine_symtable, class_symtable)

            vm_writer.writePushSymbol(arr_sym)
            index.compile(vm_writer, class_symtable, subroutine_symtable)
            vm_writer.writeOp('+')
            
            rvalue.compile(vm_writer, class_symtable, subroutine_symtable)

            vm_writer.writePop("temp", 0)
            vm_writer.writePop("pointer", 1)
            vm_writer.writePush("temp", 0)
            vm_writer.writePop("that", 0)
        else:
            lvalue = self.elements[1]
            lvalue_sym = searchSymbol(lvalue.value, subroutine_symtable, class_symtable)
            rvalue = self.elements[3]
            rvalue.compile(vm_writer, class_symtable, subroutine_symtable)
            vm_writer.writePopSymbol(lvalue_sym)

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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        subroutine_call = self.elements[1]
        subroutine_call.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writePop("temp", "0")

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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        for statement in self.statements:
            statement.compile(vm_writer, class_symtable, subroutine_symtable)
