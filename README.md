# Nand2Tetris IJack

## Description

Jack-like indent-based programming language. This is a toy language made for the Computer Organization Course in Universidad EAFIT for academic purposes and it is not meant to be used in a serious way. 


## Literals
- "(", ")", "\[", "\]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "!"

## Keywords
- class
- method
- init
- fun
- field 
- static
- var
- num
- char
- bool
- void
- true
- false
- none
- self
- let
- do
- if 
- else
- while
- return

## Tokens
- KEYWORD
- INTEGER_CONSTANT
- IDENTIFIER
- ARROW
- SYMBOL
- COLON
- STRING_CONSTANT
- WS
- NEWLINE

## Requirements
You'll need to have installed <code>Python3</code> and <code>Python-pip</code> as well.  

To set up the project run <code>python3 -m pip -r requirements.txt</code> to install all required python libraries, it is recomended to use a virtual environment.  

## Usage

The project works in a similar way to Jack's own compiler, but with some syntactic sugar to make it look more like Python.  

Now to use the compiler it is necessary to have a program written in IJack, all IJack files have an <code>.ijk</code> extension, for example:  <code>Example.ijk</code>  

Now to run the compiler and compile the program to a .vm file run the following command in a terminal emulator:

```sh
python3 ijkcompiler.py /path/to/your/File.ijk
```

To compile an entire directory just run:
```sh
python3 ijkcompiler.py /path/to/your/directory
```

If the program "example.ijk" is well written according to the IJack language and does not generate any error in its compilation, a .vm file such as "example.vm" will be generated  

Please note that the compiler won't tell in most cases if it finds an error, it will simply stop writing to the .vm file, so make sure the compiler actually wrote code to your .vm file before testing.

This programming language works basically in the same way as Jack besides some minor changes in structure, some of those changes are:

- The language now works with indentations instead of curly braces, each indented block start when a colon is used.
- The language does not use semicolons as eol indicator, instead uses linebreaks (\\n).
- <code>constructor</code> function kind is now <code>init</code> .
- <code>function</code> function kind is now <code>fun</code>.
- <code>int</code> is now <code>num</code>.
- <code>boolean</code> is now <code>bool</code>.
- function signature changed from <code>\<function-kind\> \<return-type\> \<function-name\>(\<args\>)</code> to <code><function-kind\> <function-name\>(\<args\>) -> \<return-type\></code>.

## Language specfication

A brief explaination on the basics of the language:

### Classes
All files in IJack represent a Class and must be named acordingly.

In <code>Example.ijk</code>:
```
class Example:
    ...
```

Multiple classes can be used in a program by writing their respective files in the same directory

### Functions and Methods

All functions in IJack follow the following pattern:
```
<function-kind> <function-name>([<arguments>]) -> <return-type>: 
    <function-body>
```
There are three function kinds in IJack:
        - <code>init</code>: used as a constructor or initializer for the class, each class must only have one initializer and the function name must always be <code>new</code>, return type is always the classname.  
        - <code>fun</code>: represents a class level static function.  
        - <code>method</code>: defines a behaviour for an instance of the class.  

The function body is where all calculations and calls are done, must always end with a <code>return</code>.

#### Statements
There are 5 statement keywords in IJack:

##### if
```
if (<condition>):
    # Do something
    <statements>
[else:]
```
#### while
```
while (<condition>):
    # Do something
    <statements>
```
#### let
```
let <var-name> = <expression>
```
#### do 
```
do <subroutine-call>
```
#### return
```
return <expression>
```
\<expression\> may be empty

## Functioning
The program works in the following way, when a .ijk file is sent to the compiler "ijkcompiler.py", this first verifies if the file is a .ijk and then it begins to read it to send it to the "ijkcompilationengine.py" while it reads it internally, what happens is that the "lexer.py" takes a word which identifies and assigns a token accordingly, as soon as a token is generated, it is sent to "ijkcompilationengine.py" which is responsible for managing the functions, classes and variables in the language and then passing this information to "vm.py" which is responsible for writing the format of the .vm file, all this process is done in parallel such that for each word that is read a token is generated which is sent to the compilationengine so that it gives the information corresponding to the vm and at the end there is the corresponding .vm file.
