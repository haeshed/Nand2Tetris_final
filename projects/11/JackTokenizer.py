
class EndOfFile(Exception):
    pass

class InvalidConstantIntegerToken(Exception):
    pass

class InvalidStringConstantToken(Exception):
    pass

class InvalidIdentifierToken(Exception):
    pass

class JackToken:
    def __init__(self, type_, value):
        self.type_ = type_
        self.value = value
    
    def serialize(self):
        if self.value == '<':
            self.value = "&lt;"
        if self.value == '>':
            self.value = "&gt;"
        if self.value == '"':
            self.value = "&quot;"
        if self.value == '&':
            self.value = "&amp;"

        return "<{type_}> {value} </{type_}>".format(type_=self.type_, value=self.value)

    def __str__(self):
        return "Token - type: {}. value: {}".format(self.type_, self.value)

class JackTokenizer:

    SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
    KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void", \
        "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]

    def __init__(self, jack_fh):
        self.fh = jack_fh
        self._last_token = None
        self._2last_token = None
        self._use_last_token = False
        self._use_2last_token = False
    
    def readOne(self):
        val = self.fh.read(1)
        if val == '':
            raise EndOfFile()
        return val

    def restoreLastToken(self):
        self._use_last_token = True
    
    def restore2LastTokens(self):
        self._use_2last_token = True

    def backOne(self):
        self.fh.seek(self.fh.tell() - 1) # Go back one character

    def consumeWhiteCharacters(self):
        while self.readOne().isspace():
            pass
        self.backOne()

    def advance(self):
        if self._use_2last_token:
            self._use_2last_token = False
            self._use_last_token = True
            return self._2last_token
        elif self._use_last_token:
            self._use_last_token = False
            return self._last_token
        else:
            token = self.advanceImpl()
            self._2last_token = self._last_token
            self._last_token = token
            return token

    def advanceImpl(self):
        self.consumeWhiteCharacters()
        firstChar = self.readOne()
        # while firstChar == '\n':
        #     firstChar = self.readOne()
        if firstChar == '/':
            secondChar = self.readOne()
            if secondChar == '/':
                while (self.readOne() != '\n'):
                    pass
                return self.advanceImpl()
            elif secondChar == '*':
                thirdChar = self.readOne()
                if thirdChar == "*":
                    while (not (self.readOne() == '*' and self.readOne() == '/')):
                        pass
                    return self.advanceImpl()
                else:
                    self.backOne()
                    self.backOne()    
            else:
                self.backOne()

        if firstChar in self.SYMBOLS:
            token = JackToken('symbol', firstChar)
            return token

        if firstChar.isdigit():
            value = firstChar
            try:
                next_character = self.readOne()
                while next_character != ' ' and next_character not in self.SYMBOLS:
                    if not next_character.isdigit():
                        raise InvalidConstantIntegerToken()
                    value += next_character
                    next_character = self.readOne()
                self.backOne()
            except EndOfFile:
                pass
            return JackToken('integerConstant', value)
        
        if firstChar == '"':
            value = ""
            try:
                next_character = self.readOne()
                while next_character != '"':
                    value += next_character
                    next_character = self.readOne()
            except EndOfFile:
                raise InvalidStringConstantToken()
            return JackToken('stringConstant', value)
        
        value = firstChar
        try:
            next_character = self.readOne()
            while next_character != ' ' and next_character not in self.SYMBOLS and next_character != '"':
                if not (next_character.isalnum() or next_character == '_'):
                    raise InvalidIdentifierToken()
                value += next_character
                next_character = self.readOne()
            self.backOne()
        except EndOfFile:
            pass
        
        if value in self.KEYWORDS:
            return JackToken('keyword', value)
        else:
            return JackToken('identifier', value)
        

