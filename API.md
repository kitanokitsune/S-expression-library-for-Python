
S-expression Library for Python - API Reference
=======================

**S-expression Library for Python** (hereinafter called *SxprLib*) is a library for Python to parse, read and manipulate *S-expression* data structures.
This document describes *SxprLib* APIs.

Table of contents:
+ [Primitive Data Type](#primitive-data-type)
+ [Reader and Parser Functions](#reader-and-parser-functions)
+ [Standard Lisp Predicates](#standard-lisp-predicates)
+ [Standard Lisp Functions](#standard-lisp-functions)
+ [Utility Functions](#utility-functions)
+ [Global Option Switches](#global-option-switches)


# Primitive Data Type
*SxprLib* supports the following minimal data types in Lisp:

| Lisp data type | SxprLib data class | Description |
| :---:          | :---               | :---------- |
| *nil* | sxprlib.**Nil**()  | **Nil** means *empty list*.<br>The representation of **Nil** object in *S-expression* is **()**.<br>**Nil()** always returns a singleton instance of class **Nil**, and a global variable **NIL** is defined as **Nil()** so that you can use **NIL** instead of **Nil()**.<br>The operators '**==**' and '**is**' are the same meaning on **Nil**.<br>&ensp; **Nil() == NIL** &ensp; results in ***True***.<br>&ensp; **Nil() is NIL** &ensp; results in ***True***.<br>&ensp; **Nil() is Nil()** &ensp; results in ***True***.<br>&ensp; **len(Nil())** &ensp; results in **0**. |
| *cons* | sxprlib.**Cons**(*car*=**NIL**, *cdr*=**NIL**) | **Cons** is the elementary component of binary tree. It has two leaves, *car* and *cdr*, with objects.<br>The objects of *car* and *cdr* can be accessed by _x_**.car** and _x_**.cdr**.<br>The representation of **Cons(X, Y)** in *S-expression* is **(X . Y)**.<br>The *car* and *cdr* objects can be anything including **Cons** objects so that larger tree can be built with multiple **Cons** objects. For instance, **Cons(X, Cons(Y, Cons(Z, NIL)))** is possible and its representation in *S-expression* is **(X . (Y . (Z . NIL)))** or **(X Y Z)**, which is called **List**.<br>*SxprLib* provides indexing and iterator for **List** to access each element in the **List** object by index or iteration.<br>The operator '**==**' compares two **Cons** (**List**) objects whether they have the same tree structures or not.<br>The **len()** function tells the length of **List** object. |
| *symbol* | sxprlib.**Symbol**(*value*="?") | **Symbol**'s *value* should be a non-empty string.<br>The representation of **Symbol("XYZ")** in *S-expression* is **XYZ**.<br>The operator '**==**' compares both *object type* and *value*.<br>Two **Symbol** objects are identical if they have the same *value*.<br>&ensp; **Symbol("ABC") == "ABC"** &ensp; results in ***False***.<br>&ensp; **Symbol("ABC") == Symbol("ABC")** &ensp; results in ***True***.<br>&ensp; **Symbol("ABC") is Symbol("ABC")** &ensp; results in ***True***.|
| *string* | sxprlib.**String**(*value*="") | **String**'s *value* should be a string.<br>Python has its built-in string type *str*, however, its representation is usually enclosed with single quotes like **'XYZ'**, which is inconvenient for *S-expression*. The representation of **String("XYZ")** in *S-expression* is **"XYZ"**, which is always enclosed with double quotes.<br>The operator '**==**' compares *value*.<br>&ensp; **String("ABC") == "ABC"** &ensp; results in ***True***.<br>&ensp; **String("ABC") == String("ABC")** &ensp; results in ***True***.<br>&ensp; **String("ABC") == Symbol("ABC")** &ensp; results in ***False***.<br>&ensp; **String("ABC") is String("ABC")** &ensp; results in ***False***. |
| *character* | sxprlib.**Char**(*value*="?") | **Char** is a character.<br>The *value* should be 1-character string or one of the following special character names:<br>**"Backspace"**, **"Escape"**, **"Linefeed"**, **"Newline"**, **"Page"**, **"Return"**, **"Rubout"**, **"Space"**, **"Tab"**<br>The representation of **Char("**`X`**")** in *S-expression* is **#\\**`X`, where `X` is a single character or one of the above special character names.<br>You can access the real character string by *obj*.**value**.<br>The operator '**==**' compares *value*.<br>&ensp; **Char("Space") == " "** &ensp; results in ***True***.<br>&ensp; **Char("Space") == "Space"** &ensp; results in ***False***.<br>&ensp; **Char("A") == "A"** &ensp; results in ***True***.<br>&ensp; **Char("X") is Char("X")** &ensp; results in ***True***. |
| *int*<br>*float*<br>*rational* | -  | *SxprLib* does not provide these number types so that Python's built-in [*int*](https://docs.python.org/3/library/functions.html#int), [*float*](https://docs.python.org/3/library/functions.html#float) and standard module [*fractions.Fraction*](https://docs.python.org/3/library/fractions.html) are used instead. |
| *complex* | sxprlib.**Complex**(*real*=0, *imag*=0) | Python has its built-in *complex* type, however, its representation, such as **(1+2j)**, does not match for *S-expression* style **#C(1.0 2.0)**. Therefore *SxprLib* provides **Complex** data type which has a configurable representation function so that it can match for *S-expression*. <br>The operator '**==**' compares *value*.<br>&ensp; **Complex(1, 2) == 1+2j** &ensp; results in ***True***.<br>&ensp; **Complex(1, 2) == Complex(1, 2)** &ensp; results in ***True***.<br>&ensp; **Complex(1, 2) is Complex(1, 2)** &ensp; results in ***True***. <br>The **Complex** supports *fraction* and arithmetic operations such as *add*, *sub*, *mul*, *truediv*, *abs*, *power*, *pos*, *neg* and *conjugate*.<br>***Note:*** The **Complex** data type is provided by a supplementary file "*ratcomplex.py*", which also can be used as a stand-alone module. |
| *array*<br>*vector* | sxprlib.**Array**(*dim*, *value*=**NIL**) | *SxprLib* does not provide proper array type, however, provides *fake-array* type named **Array**.<br>The **Array** object stores a **List** object instead of an array object in itself.<br>The *dim* is a positive integer intended to be dimension. The *value* is a **List** object (*i.e.* **Nil** or **Cons** object) intended to be an array.<br>The *SxprLib* parser, [which is mentioned below](#reader-and-parser-functions), translates an array notation in *S-expression* ( *e.g.* **#2A((1 2) (3 4))** )  into a **List** object, and sets it to the *value* member of **Array**.<br>***Please be aware*** that the *SxprLib* does not check the validation of **Array** contents. |




#### Example
```python
>>> from sxprlib import *
>>> 
>>> print(String("XYZ"))
"XYZ"
>>> print("XYZ")
XYZ
>>>
>>> z=Cons(1, 2)
>>> print(z)
(1 . 2)
>>> z.cdr=Cons(3, NIL)
>>> print(z)
(1 3)
>>> 
>>> x=Cons(Symbol("a"), Cons(String("b"), Cons(100, NIL)))
>>> print(x)
(a "b" 100)
>>> len(x)
3
>>> print(x[0])
a
>>> print(x[1])
"b"
>>> print(x[2])
100
>>> for v in x:
...     print(v)
...
a
"b"
100
>>> 
>>> print(x)
(a "b" 100)
>>> x[1]=Symbol("XY")
>>> print(x)
(a XY 100)
>>> 
>>> y=Cons(Symbol("a"), Cons(Symbol("XY"), Cons(100, NIL)))
>>> print(y)
(a XY 100)
>>> x == y
True
>>> x is y
False
```  


# Reader and Parser Functions
*SxprLib* provides text parser function and file reader function.  
They read *S-expression* notations and translate them into objects mentioned in the previous section ([**Data Type**](#primitive-data-type)).

| Function  | Description |
| :---      | :---        |
| sxprlib.**sxparse**(*text*) | The **sxparse** parses a *text* string and returns a *S-expression* object.<br>If the *text* contains multiple S-expressions, only the first data will be returned.<br>If the *text* is empty, ***None*** is returned.<br>The **sxparse** is a wrapper function of **SxprStringReader** class instance. |
| sxprlib.**sxopen**(*filename*) | The **sxopen** opens *filename* and returns a reader object for reading *S-expression*s from the file.<br>The reader object has two member functions:<br>&ensp; \+ **read**()&ensp;: read one *S-expression* for each call. ***None*** is returned if *EOF*.<br>&ensp; \+ **close**()&ensp;: close a file.<br>The **sxopen** supports **with**-statement and the reader object can be used as an *iterator*. |
| sxprlib.**SxprReaderBaseClass** | Reader base class providing *callable* and *iterable* attributes. |
| sxprlib.**SxprStringReader**(*text*) | *S-expression* Text Reader class derived from **SxprReaderBaseClass**.<br>The *text* can be multiline string and can contain multiple S-expressions.<br>A single *S-expression* is read from the *text* for each call or iteration of the instance of this class.<br>If the parser reaches the end of the string, ***None*** is returned.|
| sxprlib.**SxprFileReader**(*fd*) | *S-expression* File Reader class derived from **SxprReaderBaseClass**.<br>A single *S-expression* is read from a file for each call or iteration of the instance of this class.<br>If the parser reaches *EOF*, ***None*** is returned.<br>*fd* must be a file object opend by **open**() not **sxopen**(). |

#### Example
```python
>>> import sxprlib as sx
>>> from sxprlib import *
>>> sx.sxprlib_enableBin = True
>>> sx.sxprlib_enableOct = True
>>> sx.sxprlib_enableHex = True
>>>
>>> x=sxparse("(1 (#b10 3) . (#o13 #x1f))")
>>> x
Cons(1, Cons(Cons(2, Cons(3, NIL)), Cons(11, Cons(31, NIL))))
>>> print(x)
(1 (2 3) 11 31)
>>> len(x)
4
>>> for v in x:
...     print(v)
...
1
(2 3)
11
31
>>>
>>> with sxopen('sxsample.txt') as f:
...     for s in f:
...         print(s)
...
(prices (apple 3.6) (orange 2.5) (banana 1.4))
(netlist (netname "VCC" (node 1 (ref "U1") (pin 1)) (node 2 (ref "R1") (pin 2))) (netname "GND" (node 3 (ref "U1") (pin 4)) (node 4 (ref "R1") (pin 1))))
(a b c d)
```  

> ***NOTE***
> 
> The parser supports *binary*, *octal* and *hexadecimal* formats in the style of Lisp/Scheme such as **#b10**, **#o13**, **#x1f**, etc.
> To treat them as symbols instead of numbers, set the global variables [***sxprlib_enableBin***](#global-option-switches), [***sxprlib_enableOct***](#global-option-switches) and [***sxprlib_enableHex***](#global-option-switches) to ***False***.


# Standard Lisp Predicates
*SxprLib* provides major Lisp predicates. Each predicate accepts any data object, and returns ***True*** or ***False*** depending on the result.

| Lisp Predicates | Description |
| :---               | :---        |
| sxprlib.**consp**(*obj*) | check if **type**(*obj*) is **Cons**. |
| sxprlib.**null**(*obj*) | check if **type**(*obj*) is **Nil**. |
| sxprlib.**listp**(*obj*) | check if **type**(*obj*) is **Cons** or **Nil**. |
| sxprlib.**symbolp**(*obj*) | check if **type**(*obj*) is **Symbol**. |
| sxprlib.**stringp**(*obj*) | check if **type**(*obj*) is **String** or *str*. |
| sxprlib.**characterp**(*obj*) | check if **type**(*obj*) is **Char**. |
| sxprlib.**integerp**(*obj*) | check if **type**(*obj*) is *int*. |
| sxprlib.**floatp**(*obj*) | check if **type**(*obj*) is *float*. |
| sxprlib.**rationalp**(*obj*) | check if **type**(*obj*) is *int* or *Fraction*. |
| sxprlib.**complexp**(*obj*) | check if **type**(*obj*) is *complex* or **Complex**. |
| sxprlib.**realp**(*obj*) | check if **type**(*obj*) is *int* or *float* or *Fraction*. |
| sxprlib.**numberp**(*obj*) | check if **type**(*obj*) is *int* or *float* or *Fraction* or *complex* or **Complex**. |
| sxprlib.**atom**(*obj*) | check if **type**(*obj*) is *not* **Cons**. |
| sxprlib.**arrayp**(*obj*) | check if **type**(*obj*) is **Array**. |
| sxprlib.**vectorp**(*obj*) | check if **type**(*obj*) is **Array** and *obj.dim* == *1*. |


#### Example
```python
>>> from sxprlib import *
>>> 
>>> x=sxparse('(1 a "b")')
>>> x
Cons(1, Cons(Symbol('a'), Cons(String('b'), NIL)))
>>> x.car
1
>>> x.cdr
Cons(Symbol('a'), Cons(String('b'), NIL))
>>>
>>> consp(x)
True
>>> numberp(x.car)
True
>>> atom(x.car)
True
>>> atom(x.cdr)
False
```


# Standard Lisp Functions
*SxprLib* provides fundamental Lisp functions as below.

| Lisp Functions | Description |
| :---           | :---        |
| sxprlib.**car**(*list*) | return *car* of *list*.<br>If *list* is not **Cons** nor **Nil**, **AttributeError** will occur. |
| sxprlib.**cdr**(*list*) | return *cdr* of *list*.<br>If *list* is not **Cons** nor **Nil**, **AttributeError** will occur. |
| sxprlib.**member**(*item*, *list*) | search *list* for *item* and return tail of the *list* starting from found *item*.<br>If *list* is not **Cons** or *item* not found, return **NIL**. |
| sxprlib.**mkcons**(*obj1*, *obj2*) | create a new **Cons** instance that *car* is *obj1* and *cdr* is *obj2*. |
| sxprlib.**mklist**(\*_args_) | create a new **List** (concatenation of **Cons**) object which elements consist of \*_args_. |
| sxprlib.**mkreverse**(*list*) | create a new **List** (concatenation of **Cons**) object which is reverse of *list*.<br>If *list* is not **Cons** nor **Nil**, **TypeError** will occur. |
| sxprlib.**mkappend**(*list1*, *list2*) | create a new **List** (concatenation of **Cons**) object.<br>**mkappend** copies *list1* and appends *list2* to the end of the copied list.<br>If *list1* is not **Cons** nor **Nil**, **TypeError** will occur. |
| sxprlib.**nconc**(*list1*, *list2*) | append *list1* and *list2* destructively.<br>**nconc** replaces *cdr* of the last **Cons** in *list1* by *list2*.<br>If *list1* is not **Cons** nor **Nil**, **TypeError** will occur. |

> ***NOTE***
> 
>  Neither **rplaca**(*x*, *obj*) nor **rplacd**(*x*, *obj*) is provided, however, equivalent operations are possible with _x_**.car**=*obj* and _x_**.cdr**=*obj*.


#### Example
```python
>>> from sxprlib import *
>>> 
>>> x=mklist(1,2,3,4,5)
>>> print(x)
(1 2 3 4 5)
>>> print(car(x))
1
>>> print(cdr(x))
(2 3 4 5)
>>> print(member(3, x))
(3 4 5)
>>> print(mkreverse(x))
(5 4 3 2 1)
>>> y=sxparse("(a b c)")
>>> print(y)
(a b c)
>>> print(mkappend(x,y))
(1 2 3 4 5 a b c)
>>> print(x)
(1 2 3 4 5)
>>> print(nconc(x,y))
(1 2 3 4 5 a b c)
>>> print(x)
(1 2 3 4 5 a b c)
```

# Utility Functions
*SxprLib* provides useful tools for working with *S-expression* data in Python.

| Function | Description |
| :---     | :---        |
| sxprlib.**py2sx**(*pyobj*, *strassym*=*True*) | The **py2sx** converts a Python object to a *S-expression* object.<br>Python's *list*s and *tuple*s are translated into *S-expression*'s **List** objects.<br>Python's *str* is translated into **Symbol** instead of **String** if *strassym* is ***True***. |
| sxprlib.**sx2py**(*sobj*, *native*=*True*) | The **sx2py** converts a *S-expression* object to a Python object.<br>*S-expression*'s **List** objects are translated into Python's *list*s.<br>**Symbol** and **String** objects are converted into Python's *str* if *native* is ***True***, or left unconverted if ***False***. |
| sxprlib.**sxpprint**(*sobj*, *file*=*sys.stdout*) | Simple (and slipshod) pretty-print.<br>If *file* is a file object opened by **open**() with *write-mode* or *append-mode*, the output is redirected to the file. |

#### Example
```python
>>> from sxprlib import *
>>> 
>>> pobj = [1,2,3,("a","b","c",4),5]
>>> sobj = py2sx(pobj)
>>> sobj
Cons(1, Cons(2, Cons(3, Cons(Cons(Symbol('a'), Cons(Symbol('b'), Cons(Symbol('c'), Cons(4, NIL)))), Cons(5, NIL)))))
>>> print(sobj)
(1 2 3 (a b c 4) 5)
>>>
>>> sx2py(sobj)
[1, 2, 3, ['a', 'b', 'c', 4], 5]
>>>
>>> with sxopen("sxsample.txt") as f:
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

# Global Option Switches
Setting these global variables changes parser behavior.

| Variable | Description |
| :---     | :---        |
| sxprlib.**sxprlib_enableLineComment** | If ***True***, semicolon ( **;** ) is treated as a line comment like Lisp. If ***False***, it is treated as one of the characters that constitute *symbol*.<br>The default value is ***True***. |
| sxprlib.**sxprlib_enableBlockComment** | If ***True***, a text enclosed by **#\|** and **\|#** is treated as a block comment like Lisp. If ***False***, **#\|** and **\|#** are treated as *symbol*s.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableEscape** | If ***True***, a backslash chracter **\\** in a string is treated as an escape character. If ***False***, it is treated as a normal character.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableQuote** | If ***True***, single quote ( **'** ) is treated as a special form like Lisp. For example `'foo` is translated into `(quote foo)`. If ***False***, it is treated as one of the characters that constitute *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableFuncRef** | If ***True***, "**#'**" is treated as a special form like Lisp. For example `#'foo` is translated into `(function foo)`. If ***False***, it is treated as a part of a *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableComplex** | If ***True***, complex number form (*e.g.* **#C(1/2 -1/2)**) is treated as a **Complex** data. If ***False***, it is treated as a *symbol* "**#C**" and *List* **(1/2 -1/2)** separately.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableChar** | If ***True***, a character type such as **#\\X** is enabled. If ***False***, it is treated as a symbol.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableArray** | If ***True***, array forms like **#(...)**, **#2A(...)**, **#3A(...)**, etc. are treated as **Array** data. If ***False***, it is treated as *symbol* "**#**", "**#2A**", "**#3A**", etc. and *List* separately.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableBin** | If ***True***, binary notation (*e.g.* **#b10**) that matches the regular expression **"[+-]?#[bB][01]+"** is treated as an integer. If ***False***, it is treated as a *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableOct** | If ***True***, octal notation (*e.g.* **#o17**) that matches the regular expression **"[+-]?#[oO][0-7]+"** is treated as an integer. If ***False***, it is treated as a *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableHex** | If ***True***, hexadecimal notation (*e.g.* **#x2f**) that matches the regular expression **"[+-]?#[xX][0-9a-fA-F]+"** is treated as an integer. If ***False***, it is treated as a *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableRadix** | If ***True***, radix notation (*e.g.* **#36r12z**) that matches the regular expression **"[+-]?#[1-9][0-9]?[0-9a-zA-Z]+"** is treated as an integer. If ***False***, it is treated as a *symbol*.<br>The default value is ***False***. |
| sxprlib.**sxprlib_enableFrac** | If ***True***, fractional form (*e.g.* **355/113**) that matches the regular expression **"[+-]?[0-9]+/[0-9]+"** is treated as a fractional number. If ***False***, it is treated as a *symbol*.<br>The default value is ***False***. |
| sxprlib.**eawcolumncount** | A dictionary which defines the number of columns that the [*East Asian Width*](https://www.unicode.org/reports/tr11/) character occupies for display.<br>For now, this variable only affects error messages.<br>The default value is &ensp; **{ "W": 2, "F": 2, "A": 2, "H": 1, "Na": 1, "N": 1 }** . |

