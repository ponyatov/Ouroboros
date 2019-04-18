" Language: metaL
" Maintainer: Dmitry Ponyatov <dponyatov@gmail.com>

if exists("b:current_syntax")
  finish
endif

syn keyword Statement	dup drop swap over 
syn keyword Operator	@ ! <<
syn keyword Statement	? ?? bye

syn region 	String		start="'" end="'"
syn region 	String		start="<string:" end=">"

syn match	Constant	"\`[a-zA-Z0-0_.]+"

syn match	Class		'\v[a-z]+:' nextgroup=Constant skipwhite
syn match	Class		"\v\<[a-z]+\:"

syn match	Comment		"\v[\\#].*$"
syn match	Comment		"\v\@[a-f0-9]+"

let b:current_syntax = "metaL"

