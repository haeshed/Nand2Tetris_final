from helpers import indent
from JackSymbolTable import searchSymbol
from JackTokenizer import JackToken

class NotAStatement(Exception):
    pass

class InvalidExpression(Exception):
    pass

class InvaledSubroutineCall(Exception):
    pass

class ExpressionList:
    def __init__(self, elements, num_of_expr):
        self.elements = elements
        self.len = num_of_expr
    
    @classmethod
    def parse(cls, tokenizer):
        all_elements = []
        expr_count = 0
        # ) or '(type var_name) (, type var_name)'
        next_token = tokenizer.advance()
        if next_token.type_ == "symbol" and next_token.value == ')':
            tokenizer.restoreLastToken()
        else:
            # Expression
            tokenizer.restoreLastToken()
            expression = JackExpression.parse(tokenizer)
            expr_count += 1
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
                expr_count += 1

                next_token = tokenizer.advance()
            tokenizer.restoreLastToken()

        return ExpressionList(all_elements, expr_count)
    
    def serialize(self):
        result = "<expressionList>\n"
        for elem in self.elements:
            if isinstance(elem, JackExpression):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</expressionList>"
        return result
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        i = 0
        while i < len(self.elements):
            expr = self.elements[i]
            expr.compile(vm_writer, class_symtable, subroutine_symtable)
            i += 2

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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        if self.elements[1].value == '.':
            cls_or_obj = self.elements[0].value
            expr_list = self.elements[4]
            nargs = expr_list.len
            try:
                obj_sym = searchSymbol(cls_or_obj, subroutine_symtable, class_symtable)
                vm_writer.writePushSymbol(obj_sym)
                class_name = obj_sym[0]
                nargs += 1
            except:
                class_name = cls_or_obj
            subroutine = "{}.{}".format(class_name, self.elements[2].value)

        else:
            subroutine = self.elements[0].value
            expr_list = self.elements[2]
            nargs = expr_list.len
            subroutine_sym = searchSymbol(subroutine, class_symtable, class_symtable)
            if subroutine_sym[1] == "method":
                nargs += 1
                vm_writer.writePush("pointer", 0)
            subroutine = "{}.{}".format(class_symtable.getName(), self.elements[0].value)

        expr_list.compile(vm_writer, class_symtable, subroutine_symtable)
        vm_writer.writeCall(subroutine, nargs)

class JackTerm:
    def __init__(self, elements, term_type):
        self.elements = elements
        self.term_type = term_type

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
            return JackTerm(elements, term_type="EXPR")
        
        # unaryop term
        elif token.type_ == "symbol" and token.value in ['-', '~']:
            elements.append(token)

            term = JackTerm.parse(tokenizer)
            elements.append(term)
            return JackTerm(elements, term_type="UOP") 

        # no other symbols allowed
        elif token.type_ == 'symbol':
            raise InvalidExpression("Expected expression: Got symbol: {}".format(token))
        
        # constant keyword
        if token.type_ == 'keyword' and token.value in ["true", "false", "null", "this"]:
            return JackTerm([token], term_type="CONST")
        elif token.type_ == 'keyword':
            raise InvalidExpression("Expected expression: Got symbol: {}".format(token))

        next_token = tokenizer.advance()

        # name.subroutine()
        if next_token.type_ == "symbol" and next_token.value == ".":
            tokenizer.restore2LastTokens()
            subroutine_call = JackSubroutineCall.parse(tokenizer)
            return JackTerm([subroutine_call], term_type="CALL")
        
        # name[]
        elif next_token.type_ == "symbol" and next_token.value == "[":
            elements.append(token) # array name
            elements.append(next_token) # [
            expression = JackExpression.parse(tokenizer) # index
            elements.append(expression)
            next_token = tokenizer.advance()
            if not (next_token.type_ == "symbol" and next_token.value == ']'):
                raise InvalidExpression("Expected: ]. Got: {}".format(next_token))
            elements.append(next_token) # ]
            return JackTerm(elements, term_type="ARRACCESS")

        else:
            tokenizer.restoreLastToken()
            return JackTerm([token], term_type="OTHER") # other token

    def serialize(self):
        result = "<term>\n"
        for elem in self.elements:
            if isinstance(elem, (JackExpression, ExpressionList, JackSubroutineCall, JackTerm)):
                result += indent(elem.serialize()) + "\n"
            else:
                result += "  " + elem.serialize() + "\n"
        result += "</term>"
        return result
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        if self.term_type == "EXPR":
            expression = self.elements[1]
            expression.compile(vm_writer, class_symtable, subroutine_symtable)
        
        elif self.term_type == "UOP":
            op = self.elements[0]
            term = self.elements[1]
            if op.value == '-':
                token = term.elements[0]
                vm_writer.writePush("constant", token.value)
                vm_writer.writeUnaryOp(op.value)
            else:
                term.compile(vm_writer, class_symtable, subroutine_symtable)
                vm_writer.writeUnaryOp(op.value)
        
        elif self.term_type == "CONST":
            const = self.elements[0]
            if const.value in ["false", "null"]:
                vm_writer.writePush("constant", "0")
            elif const.value == "this":
                vm_writer.writePush("pointer", "0")
            elif const.value == "true":
                vm_writer.writePush("constant", "0")
                vm_writer.writeUnaryOp("~")
        
        elif self.term_type == "CALL":
            subroutine_call = self.elements[0]
            subroutine_call.compile(vm_writer, class_symtable, subroutine_symtable)
        
        elif self.term_type == "ARRACCESS":
            arr = self.elements[0]
            arr_symbol = searchSymbol(arr.value, subroutine_symtable, class_symtable)
            index_expr = self.elements[2]
            
            vm_writer.writePushSymbol(arr_symbol)
            index_expr.compile(vm_writer, class_symtable, subroutine_symtable)
            vm_writer.writeOp('+')
            vm_writer.writePop("pointer", "1") # populate that
            vm_writer.writePush("that", "0")
        
        elif self.term_type == "OTHER":
            token = self.elements[0]
            if token.type_ == "integerConstant":
                vm_writer.writePush("constant", token.value)

            elif token.type_ == "identifier":
                sym = searchSymbol(token.value, subroutine_symtable, class_symtable)
                vm_writer.writePushSymbol(sym)
            elif token.type_ == "stringConstant":
                vm_writer.writePush("constant", len(token.value))
                # vm_writer.writeCall("Memory.alloc", 1)
                # vm_writer.writePop("temp", 0)
                # vm_writer.writePop("temp", 1)
                # vm_writer.writePush("temp", 0)
                # vm_writer.writePush("temp", 1)
                vm_writer.writeCall("String.new", 1)
                for c in token.value:
                    vm_writer.writePush("constant", ord(c))
                    vm_writer.writeCall("String.appendChar", 2)

        else:
            raise InvalidExpression("Trying to compile invalid expression")
            

class JackExpression:

    SIMPLE_OPS = ["+", "-", "~", "<", ">", "&", '|', '=']

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
    
    def compile(self, vm_writer, class_symtable, subroutine_symtable):
        first_term = self.elements[0]
        first_term.compile(vm_writer, class_symtable, subroutine_symtable)
        i = 1
        while i < len(self.elements):
            op = self.elements[i]
            i += 1
            term = self.elements[i]
            i += 1
            term.compile(vm_writer, class_symtable, subroutine_symtable)
            if op.value in self.SIMPLE_OPS:
                vm_writer.writeOp(op.value)
            elif op.value == '/':
                vm_writer.writeCall("Math.divide", 2)
            elif op.value == '*':
                vm_writer.writeCall("Math.multiply", 2)
            else:
                raise ValueError("Could not recognize: {}".format(op.value))



        
