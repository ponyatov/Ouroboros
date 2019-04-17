
################################################################# frame system

class Frame:
    def __init__(self,V):
        self.type  = self.__class__.__name__.lower()
        self.value = V
        self.attr  = {}
        self.nest  = []
        
    def __repr__(self):
        return self.dump()
    def head(self):
        return '<%s:%s>' % (self.type, self.value)
    def pad(self,N):
        return '\n' + '\t'*N
    def dump(self,depth=0):
        S = self.pad(depth) + self.head()
        return S
    
    def __setitem__(self,key,obj):
        self.attr[key] = obj ; return self
    def __getitem__(self,key):
        return self.attr[key]
    
class Sym(Frame): pass

class Stack(Frame): pass

class Dict(Frame): pass

######################################################################## FORTH

W = Dict('FORTH')

W['W'] = W

S = Stack('DATA')

W['S'] = S

print W

def FIND(token): S << W[token.value]

######################################################################## parser

import ply.lex as lex

tokens = ['sym']

t_ignore = ' \t\r\n'
t_ignore_COMMENT = r'[\\\#].*'

def t_sym(t):
    r'[a-zA-Z0-9_:]+'
    return Sym(t.value)

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()

lexer.input(open('src.src').read())
while True:
    token = lexer.token()
    if not token: break
    FIND(token)
    print W
