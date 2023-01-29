
S-expression Library for Python - sxprlib.py
=======================
**S-expression Library for Python** is a library for Python to parse, read and manipulate *S-expression* data structures such as *lisp programs*, *lisp data*, netlists like *EDIF* and *KiCAD*, etc.  

This library was tested with [0644.edf](http://web.archive.org/web/20040812175715/http://mint.cs.man.ac.uk/Projects/gertrude/edif-files/index.html) EDIF file (12MB).


# DEMO

### Parse a text:
```Python
>>> from sxprlib import *
>>> x = sxparse("(prices (apple 3.6) (orange 2.5))")
>>> x
Cons(Symbol('prices'), Cons(Cons(Symbol('apple'), Cons(3.6, NIL)), Cons(Cons(Symbol('orange'), Cons(2.5, NIL)), NIL)))
```
### Print a S-expression
```Python
>>> print(x)
(prices (apple 3.6) (orange 2.5))
>>> sxpprint(x)

(prices
  (apple 3.6)
  (orange 2.5))
```
### Read from a file:
```Python
>>> with sxopen('sxsample.txt') as f:
...     for s in f:
...         sxpprint(s)
...
(prices
  (apple 3.6)
  (orange 2.5)
  (banana 1.4))
(netlist
  (netname "VCC"
    (node 1
      (ref "U1")
      (pin 1))
    (node 2
      (ref "R1")
      (pin 2)))
  (netname "GND"
    (node 3
      (ref "U1")
      (pin 4))
    (node 4
      (ref "R1")
      (pin 1))))
(a b c d)
```
### List Access
```Python
>>> print(x)
(prices (apple 3.6) (orange 2.5))
>>> print(car(x))
prices
>>> print(cdr(x))
((apple 3.6) (orange 2.5))
>>> print(x[2])
(orange 2.5)
>>> for v in x:
...     print(v)
...
prices
(apple 3.6)
(orange 2.5)
```
### Convert from/to S-expression objects:
```Python
>>> x
Cons(Symbol('prices'), Cons(Cons(Symbol('apple'), Cons(3.6, NIL)), Cons(Cons(Symbol('orange'), Cons(2.5, NIL)), NIL)))
>>> print(x)
(prices (apple 3.6) (orange 2.5))
>>> l = sx2py(x)
>>> l
['prices', ['apple', 3.6], ['orange', 2.5]]
>>> y = py2sx(l)
>>> y
Cons(Symbol('prices'), Cons(Cons(Symbol('apple'), Cons(3.6, NIL)), Cons(Cons(Symbol('orange'), Cons(2.5, NIL)), NIL)))
```
### Construct a S-expression data structure
```Python
>>> z = Cons(Symbol("abc"), 2)
>>> print(z)
(abc . 2)
>>> z.cdr = Cons(3, NIL)
>>> print(z)
(abc 3)
>>> w = mklist(10, z, String("xyz"))
>>> print(w)
(10 (abc 3) "xyz")
```

# Features
**S-expression Library for Python** provides the following features:

* [S-expression Primitives](./API.md#primitive-data-type)
* [Text String Parser](./API.md#reader-and-parser-functions) (**sxparse** function and **SxprStringReader** class)
* [File Reader](./API.md#reader-and-parser-functions) (**sxopen** function and **SxprFileReader** class)
* [Standard Lisp Predicates](./API.md#standard-lisp-predicates) such as **null**, **consp**, **listp**, **atom**, etc.
* [Standard Lisp Functions](./API.md#standard-lisp-functions) such as **car**, **cdr**, **cons**, **append**, etc.
* [Utilities](./API.md#utility-functions) such as Converters (**py2sx**, **sx2py**) and Pretty-Print (**sxpprint**)
* [Option Switches](./API.md#global-option-switches) to change parser behaviors


# Requirement
* Python 3


# Installation
* Place "*sxprlib.py*" and "*ratcomplex.py*" in the same directory where your program source is there.


# Usage
* Import "*sxprlib.py*" in your python code. Please see [*API Reference*](./API.md) for details.


# Author
* Kitanokitsune

# License
This library is released under the [MIT license](https://en.wikipedia.org/wiki/MIT_License).  
```text
Copyright (c) 2023 Kitanokitsune

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```