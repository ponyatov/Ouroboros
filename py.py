import os,sys

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
        return '%s<%s:%s> @%x' % (prefix, self.type, self.str(), id(self))
    def str(self):
        return str(self.value)
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
    def top(self): return self.nest[-1]
    def dup(self): return self.push(self.top())
    def dropall(self): self.nest = []
    
    def execute(self): S << self
    
    def src(self): return self.value
    
class Symbol(Frame): pass

class String(Frame):
    def str(self):
        T = ''
        for c in self.value:
            if c == '\n': T += '\\n'
            elif c == '\t': T += '\\t'
            else: T += c
        return T
    def add(self,obj):
        return String(self.value + obj.value)

class Stack(Frame): pass

class Dict(Frame):
    def __lshift__(self,obj):
        if callable(obj): self[obj.__name__] = CMD(obj) ; return self
        else: return Frame.__lshift__(self, obj)

class Active(Frame): pass

class CMD(Active):
    def __init__(self,F): Active.__init__(self,F.__name__) ; self.fn = F
    def execute(self): self.fn()
    
######################################################################## parser

import ply.lex as lex

tokens = ['symbol','string']

t_ignore = ' \t\r\n'
t_ignore_COMMENT = r'[\\\#].*'

states = (('str','exclusive'),)
t_str_ignore = ''

def t_string(t):
    r'\''
    t.lexer.lexstring=''
    t.lexer.push_state('str')
def t_str_string(t):
    r'\''
    t.lexer.pop_state()
    return String(t.lexer.lexstring)
def t_str_lf(t):
    r'\\n'
    t.lexer.lexstring += '\n'
def t_str_tab(t):
    r'\\t'
    t.lexer.lexstring += '\t'
def t_str_char(t):
    r'.'
    t.lexer.lexstring += t.value

def t_symbol(t):
    r'`|[a-zA-Z0-9_:;@!.,<>+\-*/^?]+'
    return Symbol(t.value)

def t_ANY_error(t): raise SyntaxError(t)

lexer = lex.lex()

######################################################################## FORTH

W = Dict('FORTH')

W['W'] = W

S = Stack('DATA')

W['S'] = S

def DUP(): S.dup()
W << DUP

def DROPALL(): S.dropall()
W['.'] = CMD(DROPALL)

def BYE(): sys.exit(0)
W << BYE

def Q(): print S
W['?'] = CMD(Q)

def QQ(): Q() ; BYE()
W['??'] = CMD(QQ)

def ST(): idx = S.pop().value ; W[idx] = S.pop()
W['!'] = CMD(ST)

def PUSH(): B = S.pop() ; S.top() << B
W['<<'] = CMD(PUSH)

def ADD(): B = S.pop() ; A = S.pop() ; S << A.add(B)
W['+'] = CMD(ADD)

def QUOTE(): WORD()
W['`'] = CMD(QUOTE)

def WORD():
    token = lexer.token()
    if token: S << token
    return token

def FIND():
    token = S.pop()
    try: S << W[token.value] ; return True
    except KeyError:
        try: S << W[token.value.upper()] ; return True
        except KeyError: S << token ; return False

def EXECUTE(): S.pop().execute()

def INTERPRET():
    lexer.input(S.pop().value)
    while True:
        if not WORD(): break
        if isinstance(S.top(), Symbol):
            if not FIND(): raise SyntaxError(S.pop()) 
            EXECUTE()

def REPL():
    while True:
        S << String(raw_input('ok> '))
        INTERPRET()
W << REPL
        
########################################################################## META

class Meta(Frame): pass

class Module(Meta): pass

def MODULE(): WORD() ; S << Module(S.pop().value)

W['module:'] = CMD(MODULE)

class File(Meta):
    def src(self):
        T  = '===== %s =====\n' % self.head()
        for i in self.nest: T += i.src() + '\n'
        T += '='*40+'\n'
        return T

def FILE(): S << File(S.pop().value)
W << FILE

def SRC(): print S.pop().src()
W['>src'] = CMD(SRC)

class Section(Meta): pass

def SECTION(): WORD() ; S << Section(S.pop().value)
W['section:'] = CMD(SECTION)

########################################################################## INIT

if __name__ == '__main__':
    for src in sys.argv[1:]:
        S << String(open(src).read())
        INTERPRET()
    REPL()
