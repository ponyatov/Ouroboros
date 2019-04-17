
################################################################# frame system

class Frame:
    def __init__(self,V):
        self.type  = self.__class__.__name__.lower()
        self.value = V
        self.attr  = {}
        self.nest  = []
        
    def __repr__(self):
        return self.dump()
    def head(self,prefix=''):
        return '%s<%s:%s> @%x' % (prefix, self.type, self.value, id(self))
    def pad(self,N):
        return '\n' + '\t'*N
    def dump(self,depth=0,prefix=''):
        if not depth: Frame.dumped = []
        T = self.pad(depth) + self.head(prefix)
        if self in Frame.dumped: return T + ' ...'
        else: Frame.dumped.append(self)
        for i in self.attr: T += self.attr[i].dump(depth+1, prefix='%s = ' % i)
        for j in self.nest: T += j.dump(depth+1)
        return T
    
    def __setitem__(self,key,obj): self.attr[key] = obj ; return self
    def __getitem__(self,key): return self.attr[key]
    def __lshift__(self,obj): return self.push(obj)
    
    def push(self,obj): self.nest.append(obj) ; return self
    def pop(self): return self.nest.pop()
    
    def execute(self): S << self
    
class Symbol(Frame): pass

class String(Frame): pass

class Stack(Frame): pass

class Dict(Frame): pass

class Active(Frame): pass

class CMD(Active):
    def __init__(self,F): Active.__init__(self,F.__name__) ; self.fn = F
    def execute(self): self.fn()

######################################################################## parser

import ply.lex as lex

tokens = ['symbol']

t_ignore = ' \t\r\n'
t_ignore_COMMENT = r'[\\\#].*'

def t_symbol(t):
    r'[a-zA-Z0-9_:]+'
    return Symbol(t.value)

def t_error(t): raise SyntaxError(t)

lexer = lex.lex()

######################################################################## FORTH

W = Dict('FORTH')

W['W'] = W

S = Stack('DATA')

W['S'] = S

def WORD():
    token = lexer.token()
    if token: S << token
    return token

def FIND():
    token = S.pop()
    try:
        S << W[token.value] ; return True
    except KeyError:
        S << token ; return False

def EXECUTE(): S.pop().execute()

def INTERPRET():
    lexer.input(S.pop().value)
    while True:
        if not WORD(): break
        if not FIND(): raise SyntaxError(S.pop()) 
        EXECUTE()
        print W
        
########################################################################## META

class Meta(Frame): pass

class Module(Meta): pass

def MODULE(): WORD() ; S << Module(S.pop().value)

W['module:'] = CMD(MODULE)

########################################################################## INIT

if __name__ == '__main__':
    S << String(open('src.src').read())
    INTERPRET()
