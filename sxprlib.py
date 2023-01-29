# -*- coding:utf-8 -*-
"""S-expression library for Python ver1.0

S-expression data structure parser/manipulator intended for
parsing and manipulating lisp program, lisp data, netlists like EDIF and KiCAD, etc.

This library is tested with the following huge EDIF file.
Filename: 0644.edf (12MB)
File URL: http://web.archive.org/web/20040812175715/http://mint.cs.man.ac.uk/Projects/gertrude/edif-files/index.html
"""
sxpr_version = "1.0"
##################################################################################
# This library is released under the MIT license.                                #
# -------------------------------------------------------                        #
# Copyright (c) 2023 Kitanokitsune                                               #
#                                                                                #
# Permission is hereby granted, free of charge, to any person obtaining a copy   #
# of this software and associated documentation files (the "Software"), to deal  #
# in the Software without restriction, including without limitation the rights   #
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell      #
# copies of the Software, and to permit persons to whom the Software is          #
# furnished to do so, subject to the following conditions:                       #
#                                                                                #
# The above copyright notice and this permission notice shall be included in all #
# copies or substantial portions of the Software.                                #
#                                                                                #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR     #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,       #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE    #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER         #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  #
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  #
# SOFTWARE.                                                                      #
##################################################################################

sxprlib_enableLineComment = True  # treat ";" as line comment if True
sxprlib_enableBlockComment = False  # treat "#|...|#" as block comment if True
sxprlib_enableEscape = False  # treat "\" in a string as an escape char if True
sxprlib_enableQuote = False  # treat "'" as lisp-like special form (quote) if True
sxprlib_enableFuncRef = False  # treat "#'" as lisp's function reference if True

sxprlib_enableBin = False  # enable binary number (like "#b10") if True
sxprlib_enableOct = False  # enable octal number (like "#o76") if True
sxprlib_enableHex = False  # enable hexadecimal number (like "#xFE") if True
sxprlib_enableRadix = False  # enable radix number (like "#36rABCZ") if True
sxprlib_enableComplex = False  # treat "#C(...)" as a complex number if True
sxprlib_enableArray = False  # treat "#(...)" or "#nA(...) as an array if True
sxprlib_enableFrac = False  # treat "[+-]?[0-9]+/[0-9]+" as fractional number if True
sxprlib_enableChar = False  # treat "#\s" as a character if True

sxprlib_ignoreCase = False  # ignore case of Symbol if True

from sys import stdout as __stdout
from json import dumps as _dumps
from unicodedata import east_asian_width as _east_asian_width

# define east_asian_width column count
eawcolumncount = {"W": 2, "F": 2, "A": 2, "H": 1, "Na": 1, "N": 1}


from re import compile as __compile
from re import ASCII as __ASCII

_is_integer = __compile(r"[+-]?\d+", __ASCII).fullmatch
_is_bin = __compile(r"[+-]?#[bB][01]+(/[01]+)?", __ASCII).fullmatch
_is_oct = __compile(r"[+-]?#[oO][0-7]+(/[0-7]+)?", __ASCII).fullmatch
_is_hex = __compile(r"[+-]?#[xX][0-9a-fA-F]+(/[0-9a-fA-F]+)?", __ASCII).fullmatch
_is_radix = __compile(
    r"[+-]?#[1-9][0-9]?[rR][0-9a-zA-Z]+(/[0-9a-zA-Z]+)?", __ASCII
).fullmatch
_is_number = __compile(
    r"[+-]?(\d+(\.\d*)?|\d*\.\d+)([defsDEFS][+-]?\d+)?", __ASCII
).fullmatch
_is_fraction = __compile(r"[+-]?\d+/\d+", __ASCII).fullmatch
_is_arrayprefix = __compile(r"#[0-9]+[aA]", __ASCII).fullmatch
_is_charhex = __compile(r"#\\[uxUX][0-9a-fA-F]+", __ASCII).fullmatch

from weakref import WeakValueDictionary as _WVDic


def _inany(item, lists):
    for l in lists:
        if item in l:
            return True
    return False


def __is_oct_digit(c):
    if ("0" <= c) and (c <= "7"):
        return True
    else:
        return False


def __is_hex_digit(c):
    if ("0" <= c) and (c <= "9"):
        return True
    elif ("a" <= c) and (c <= "f"):
        return True
    elif ("A" <= c) and (c <= "F"):
        return True
    else:
        return False


# ---------------------- data type definition


class _ReadOnlyClassVarMeta(type):
    def __setattr__(self, name, value):
        if not name in self.__dict__:
            raise PermissionError(name)
        if self.__dict__[name] is not None:
            raise PermissionError("{} is read only!".format(name))
        super().__setattr__(name, value)

    def __delattr__(self, name):
        if not name in self.__dict__:
            raise AttributeError(name)
        else:
            raise PermissionError(name)


# data type: Nil
class Nil(metaclass=_ReadOnlyClassVarMeta):
    """Definition of Nil data type"""

    __singleinstance = None
    car = None
    cdr = None

    def __new__(self, *args, **kwargs):
        if Nil.__singleinstance is None:
            Nil.__singleinstance = super().__new__(self)
            Nil.car = Nil.__singleinstance
            Nil.cdr = Nil.__singleinstance
        return Nil.__singleinstance

    def __setattr__(self, name, value):
        if name in {"car", "cdr"}:  # avoid overriding/hiding class variable car and cdr
            raise PermissionError(name)
        # super().__setattr__(name, value)
        self.__dict__[name] = value

    def __str__(self):
        return "()"

    def __repr__(self):
        return "NIL"

    def __len__(self):
        return 0

    def __iter__(self):
        return _ConsIterator(self)

    def __eq__(self, v):
        return self is v

    def __ne__(self, v):
        return self is not v


_NIL = Nil()  # Nil() returns a singleton NIL instance
NIL = Nil()


# data type: Cons
class Cons:
    """Definition of Cons data type"""

    def __init__(self, car=_NIL, cdr=_NIL):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        l = []
        s = Cons.__Sxpr2Str(self, l)
        l.clear()
        del l
        return s

    def __repr__(self):
        l = dict()
        s = Cons.__Sxpr2Repr(self, l)
        l.clear()
        del l
        return s

    def __len__(self):
        n = 1
        c = self
        occurence = {id(c)}
        while type(c.cdr) is Cons and not id(c.cdr) in occurence:
            n = n + 1
            occurence.add(id(c.cdr))
            c = c.cdr
        occurence.clear()
        del occurence
        return n

    def __getitem__(self, n):
        if type(n) is slice:
            raise NotImplementedError("Cons: Slicing Cons object is not implemented.")
        if n < 0:
            raise IndexError("Cons: index out of range")
        m = n
        c = self
        while m > 0:
            if not type(c) in {Cons, Nil}:
                raise IndexError("Cons: index out of range")
            c = c.cdr
            m = m - 1
        if type(c) is not Cons:
            return c
        else:
            return c.car

    def __setitem__(self, n, x):
        if type(n) is slice:
            raise NotImplementedError("Cons: Slicing Cons object is not implemented.")
        if n < 0:
            raise IndexError("Cons: index out of range")
        m = n
        c = self
        p = _NIL
        while m > 0:
            if type(c) is not Cons:
                raise IndexError("Cons: index out of range")
            p = c
            c = c.cdr
            m = m - 1
        if type(c) is not Cons:
            p.cdr = x
        else:
            c.car = x

    def __iter__(self):
        return _ConsIterator(self)

    def __delattr__(self, name):
        if name in {"car", "cdr"}:
            raise PermissionError(name)
        else:
            super().__delattr__(name)

    def __eq__(self, v):
        if type(v) is Cons:
            return repr(self) == repr(v)
        return False

    def __ne__(self, v):
        if type(v) is Cons:
            return repr(self) != repr(v)
        return True

    @staticmethod
    def __Sxpr2Str(ex, occurence):
        if type(ex) is Cons:
            if sxprlib_enableQuote and ex.car == Symbol("quote") and consp(ex.cdr):
                if null(ex.cdr.cdr):
                    return "'{}".format(Cons.__Sxpr2Str(ex.cdr.car, occurence))
            if sxprlib_enableFuncRef and ex.car == Symbol("function") and consp(ex.cdr):
                if null(ex.cdr.cdr) and symbolp(ex.cdr.car):
                    return "#'{}".format(Cons.__Sxpr2Str(ex.cdr.car, occurence))
            return "({})".format(Cons.__Cons2SeqStr(ex, occurence))
        return str(ex)

    @staticmethod
    def __Cons2SeqStr(c, occurence):
        localoccurence = set()
        occurence.append(localoccurence)
        s = []
        while True:
            if type(c) is not Cons:
                oc = []
                oc.extend(occurence)
                s.extend([". ", Cons.__Sxpr2Str(c, oc)])
                oc.clear()
                break
            if _inany(id(c), occurence):
                s.append("...")
                break
            localoccurence.add(id(c))
            oc = []
            oc.extend(occurence)
            s.append(Cons.__Sxpr2Str(c.car, oc))
            oc.clear()
            c = c.cdr
            if type(c) is Nil:
                break
            s.append(" ")
        localoccurence.clear()
        return "".join(s)

    @staticmethod
    def __Sxpr2Repr(s, occurence):
        if s is _NIL:
            return "NIL"
        elif type(s) is not Cons:
            return repr(s)
        sbeg = []
        send = []
        while True:
            if type(s) is Array:
                sbeg.extend(
                    [
                        "Array(",
                        str(s.dim),
                        ", ",
                        Cons.__Sxpr2Repr(s.value, occurence),
                        ")",
                    ]
                )
                break
            elif type(s) is not Cons:
                sbeg.append(repr(s))
                break
            if id(s) in occurence:
                sbeg.extend(["<Cons at #", str(occurence[id(s)]), ">"])
                break
            occurence[id(s)] = len(occurence)
            if type(s.car) is Array:
                sbeg.extend(
                    [
                        "Cons(Array(",
                        str(s.car.dim),
                        ", ",
                        Cons.__Sxpr2Repr(s.car.value, occurence),
                        "), ",
                    ]
                )
                send.append(")")
            else:
                sbeg.extend(["Cons(", Cons.__Sxpr2Repr(s.car, occurence), ", "])
                send.append(")")
            s = s.cdr
        sbeg.extend(send)
        # del send
        return "".join(sbeg)


# data type: Char
class Char:
    """Definition of Char data type"""

    __CharInstance = _WVDic({})
    __NameToCharDic = {
        "Backspace": "\x08",
        "Escape": "\x1b",
        "Linefeed": "\n",
        "Newline": "\n",
        "Page": "\x0c",
        "Return": "\r",
        "Rubout": "\x1f",
        "Space": " ",
        "Tab": "\t",
    }
    __CharToNameDic = {
        "\x08": "Backspace",
        "\t": "Tab",
        "\n": "Linefeed",
        "\x0c": "Page",
        "\r": "Return",
        "\x1b": "Escape",
        "\x1f": "Rubout",
        " ": "Space",
    }

    def __new__(self, value="?"):
        if type(value) is Char:
            return value
        elif type(value) is str:
            v = value
        elif type(value) is String:
            v = value.value
        else:
            v = str(value)
        if not Char.IsChar(v):
            raise ValueError('Char(): Illegal argument "{}"!'.format(v))
        if _is_charhex(v):  # "#\\[uxUX][0-9a-fA-F]+"
            v = "{:c}".format(int(v[3:], 16))
        elif v.startswith("#\\"):
            v = v.replace("#\\", "")
        v = Char.__NameToCharDic.get(v.capitalize(), v)
        obj = Char.__CharInstance.get(v)
        if obj is None:
            obj = super().__new__(self)
            obj.value = v
            Char.__CharInstance[v] = obj
        return obj

    def __str__(self):
        v = self.value
        c = ord(v)
        if c <= 32 or (127 <= c and c <= 255):
            v = "#\\{}".format(Char.__CharToNameDic.get(v, "x{:02x}".format(c)))
        else:
            v = _dumps(v, ensure_ascii=False)
            v = "#\\" + v[1:][:-1]
            v = v.replace("\\\\", "\\")
            if len(v) >= 12:
                v = "#\\U{:08x}".format(c)
        return v

    def __repr__(self):
        v = self.value
        c = ord(v)
        if c <= 32 or (127 <= c and c <= 255):
            v = '"{}"'.format(Char.__CharToNameDic.get(v, "\\x{:02x}".format(c)))
        else:
            v = _dumps(v, ensure_ascii=False)
            if len(v) >= 14:
                v = '"\\U{:08x}"'.format(c)
        return "Char({})".format(v)

    def __setattr__(self, name, value):
        if name == "value" and name in self.__dict__:  # avoid overriding 'value'
            raise PermissionError("Char: {} is read only!".format(name))
        # super().__setattr__(name, value)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name == "value":
            raise PermissionError(name)
        else:
            super().__delattr__(name)

    def __hash__(self):
        return hash(("SxprLib Char", self.value))

    def __eq__(self, v):
        if type(v) in {Char, String}:
            return v.value == self.value
        elif type(v) is str:
            return v == self.value
        return False

    def __ne__(self, v):
        if type(v) in {Char, String}:
            return v.value != self.value
        elif type(v) is str:
            return v != self.value
        return True

    @staticmethod
    def listall():
        return [x for x in Char.__CharInstance]

    @staticmethod
    def IsChar(s):
        if type(s) is not str:
            return False
        if _is_charhex(s):  # "#\\[uxUX][0-9a-fA-F]+"
            x = int(s[3:], 16)
            if 0 <= x and x <= 0x10FFFF:
                return True
            else:
                return False
        if s.startswith("#\\"):
            s = s.replace("#\\", "")
        if len(s) == 1:
            return True
        else:
            return s.capitalize() in Char.__NameToCharDic


# data type: Symbol
class Symbol:
    """Definition of Symbol data type"""

    __SymbolInstance = _WVDic({})

    def __new__(self, value="?"):
        if type(value) is Symbol:
            return value
        elif type(value) is str:
            v = value
        elif type(value) is String:
            v = value.value
        else:
            v = str(value)
        if sxprlib_ignoreCase:
            v = v.lower()
        if not v:
            raise ValueError("Symbol(): the argument must be a non-empty string!")
        obj = Symbol.__SymbolInstance.get(v)
        if obj is None:
            obj = super().__new__(self)
            obj.value = v
            Symbol.__SymbolInstance[v] = obj
        return obj

    def __str__(self):
        if self.value == ".":
            return "\\."
        else:
            s = str(self.value).translate(
                str.maketrans(
                    {
                        "(": "\\(",
                        ")": "\\)",
                        " ": "_",
                        "|": "\\|",
                        '"': '\\"',
                        "\a": "\\a",
                        "\b": "\\b",
                        "\f": "\\f",
                        "\n": "\\n",
                        "\r": "\\r",
                        "\t": "\\t",
                        "\v": "\\v",
                    }
                )
            )
            if (
                _is_integer(s)
                or (sxprlib_enableBin and _is_bin(s))
                or (sxprlib_enableOct and _is_oct(s))
                or (sxprlib_enableHex and _is_hex(s))
                or (sxprlib_enableRadix and _is_radix(s))
                or (sxprlib_enableFrac and _is_fraction(s))
                or _is_number(s)
            ):
                s = "|{}|".format(s)
            return "{}".format(s)

    def __repr__(self):
        return "Symbol({})".format(repr(self.value))

    def __setattr__(self, name, value):
        if name == "value" and name in self.__dict__:  # avoid overriding 'value'
            raise PermissionError("Symbol: {} is read only!".format(name))
        # super().__setattr__(name, value)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name == "value":
            raise PermissionError(name)
        else:
            super().__delattr__(name)

    def __hash__(self):
        return hash(("SxprLib Symbol", self.value))

    def __eq__(self, v):
        if type(v) is Symbol:
            return self.value == v.value
        return False

    def __ne__(self, v):
        if type(v) is Symbol:
            return self.value != v.value
        return True

    @staticmethod
    def listall():
        return [x for x in Symbol.__SymbolInstance]


# data type: String
class String:
    """Definition of String data type"""

    def __init__(self, value=""):
        if type(value) is str:
            self.value = value
        elif type(value) in {Symbol, String}:
            self.value = value.value
        else:
            self.value = str(value)

    def __str__(self):
        s = _dumps(self.value, ensure_ascii=False)
        if not sxprlib_enableEscape:
            s = s.replace("\\\\", "\\")
        return s

    def __repr__(self):
        return "String({})".format(repr(self.value))

    def __setattr__(self, name, value):
        if name == "value" and name in self.__dict__:  # avoid overriding 'value'
            raise PermissionError("String: {} is read only!".format(name))
        # super().__setattr__(name, value)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name == "value":
            raise PermissionError(name)
        else:
            super().__delattr__(name)

    def __hash__(self):
        return hash(("SxprLib String", self.value))

    def __eq__(self, v):
        if type(v) is String:
            return self.value == v.value
        else:
            return self.value == v

    def __ne__(self, v):
        if type(v) is String:
            return self.value != v.value
        else:
            return self.value != v


# data type: Int & Float
# use Python built-in int/float type


# data type: Fraction
# use Python standard module fractions.Fraction
from fractions import Fraction


# data type: Complex
from ratcomplex import Complex

Complex.str_format_spec = "#C({0} {1})"


# data type: Array
class Array:
    """Definition of Array data type"""

    def __init__(self, dim, value=_NIL):
        self.dim = int(dim)
        if listp(value):
            self.value = value
        elif type(value) in {list, tuple}:
            self.value = py2sx(value, False)
        else:
            self.value = py2sx(list(value), False)

    def __str__(self):
        if self.dim == 1:
            return "#{}".format(str(self.value))
        else:
            return "#{}A{}".format(self.dim, str(self.value))

    def __repr__(self):
        return "Array({}, {})".format(self.dim, repr(self.value))

    def __setattr__(self, name, value):
        if name == "dim":
            v = int(value)
        elif name == "value":
            if listp(value):
                v = value
            elif type(value) in {list, tuple}:
                v = py2sx(value, False)
            else:
                v = py2sx(list(value), False)
        else:
            v = value
        self.__dict__[name] = v

    def __delattr__(self, name):
        if name in {"dim", "value"}:
            raise PermissionError(name)
        else:
            super().__delattr__(name)


# ------------------------- Cons Iterator


# Cons Iterator: enables S-expression data to be used in 'for v in CONS' form
class _ConsIterator:
    """Cons iterator object"""

    def __init__(self, cons):
        self.__cons = cons
        self.__occurence = set()

    def __next__(self):
        if type(self.__cons) is Nil or id(self.__cons) in self.__occurence:
            self.__occurence.clear()
            raise StopIteration()
        if type(self.__cons) is Cons:
            value = self.__cons.car
            self.__occurence.add(id(self.__cons))
            self.__cons = self.__cons.cdr
        else:
            value = self.__cons
            self.__cons = _NIL
        return value


# ------------------------- Standard Lisp function


def car(c):
    """return car of Cons object"""
    return c.car


def cdr(c):
    """return cdr of Cons object"""
    return c.cdr


def mkcons(a, d):
    """make Cons object"""
    return Cons(a, d)


def mklist(*args):
    """make S-expression List (chained Cons) object"""
    r = _NIL
    for v in args[::-1]:
        r = Cons(v, r)
    return r


def consp(s):
    """check if argument is Cons type"""
    return type(s) is Cons


def null(s):
    """check if argument is Nil type"""
    return s is _NIL


def listp(s):
    """check if argument is Nil or Cons type"""
    return (s is _NIL) or (type(s) is Cons)


def symbolp(s):
    """check if argument is Symbol type"""
    return type(s) is Symbol


def stringp(s):
    """check if argument is String or str type"""
    return type(s) in {String, str}


def characterp(s):
    """check if argument is Char type"""
    return type(s) is Char


def integerp(s):
    """check if argument is int type"""
    return type(s) is int


def floatp(s):
    """check if argument is float type"""
    return type(s) is float


def rationalp(s):
    """check if argument is int or Fraction type"""
    return type(s) in {int, Fraction}


def complexp(s):
    """check if argument is built-in complex or Complex type"""
    return type(s) in {complex, Complex}


def realp(s):
    """check if argument is int or float or Fraction type"""
    return type(s) in {int, float, Fraction}


def numberp(s):
    """check if argument is int or float or Fraction or complex or Complex type"""
    return type(s) in {int, float, Fraction, complex, Complex}


def atom(s):
    """check if argument is NOT Cons type"""
    return not (consp(s))


def arrayp(s):
    """check if argument is Array type"""
    return type(s) is Array


def vectorp(s):
    """check if argument is Array type and dimension is 1"""
    if type(s) is Array:
        return s.dim == 1
    return False


def mkreverse(l):
    """make reversed S-expression List"""
    if not listp(l):
        raise TypeError(
            "mkreverse(): Not a valid S-expression List! {}".format(repr(l))
        )
    n = len(l)
    r = _NIL
    for v in l:
        if n < 1:
            break
        r = Cons(v, r)
        n = n - 1
    return r


def mkappend(l1, l2):
    """make appended S-expression List"""
    if null(l1):
        return l2
    elif consp(l1):
        n = len(l1) - 1
        ret = Cons(l1.car)
        c = ret
        l = l1.cdr
        while n > 0:
            c.cdr = Cons(l.car)
            c = c.cdr
            l = l.cdr
            n = n - 1
        c.cdr = l2
        return ret
    else:
        raise TypeError("mkappend(): Not a List!")


def nconc(l1, l2):  # destructive append
    """concatenate two S-expression Lists destructively"""
    if null(l1):
        return l2
    elif consp(l1):
        n = len(l1) - 1
        ret = l1
        while n > 0:
            l1 = l1.cdr
            n = n - 1
        l1.cdr = l2
        return ret
    else:
        raise TypeError("nconc(): Not a List!")


def member(s, l):
    """search S-expression List for item"""
    if not consp(l):
        return _NIL
    n = len(l)
    while not (s == l.car):
        l = l.cdr
        n = n - 1
        if n < 1:
            return _NIL
    return l


# ------------------------- miscellaneous tools


# sx2py: convert S-expression object to Python object
def sx2py(s, native=True):
    """convert S-expression object to Python object"""
    occurence = set()
    listdic = dict()
    s = __sx2py(s, native, occurence, listdic)
    listdic.clear()
    occurence.clear()
    return s


def __sx2py(s, native, occurence, listdic):
    if s is _NIL:
        return []
    elif native and (type(s) in {String, Symbol, Char}):
        return s.value
    elif type(s) is Cons:
        # if (
        #    sxprlib_enableQuote
        #    and s.car == Symbol("quote")
        #    and consp(s.cdr)
        #    and null(s.cdr.cdr)
        # ):
        #    return __sx2py(s.cdr.car, native, occurence, listdic)
        # if (
        #    sxprlib_enableFuncRef
        #    and s.car == Symbol("function")
        #    and consp(s.cdr)
        #    and null(s.cdr.cdr)
        #    and symbolp(s.cdr.car)
        # ):
        #    return __sx2py(s.cdr.car, native, occurence, listdic)
        if id(s) in listdic:
            return listdic[id(s)]
        else:
            l = []
            listdic[id(s)] = l
            while type(s) is Cons:
                if id(s) in occurence:
                    raise ValueError("sx2py(): unresolvable recursion found.")
                occurence.add(id(s))
                l.append(__sx2py(s.car, native, occurence, listdic))
                s = s.cdr
            if s is not _NIL:
                l.append(__sx2py(s, native, occurence, listdic))
            return l
    elif type(s) is Fraction:
        if s.denominator == 1:
            return s.numerator
        else:
            return s
    elif type(s) is Complex:
        return complex(s)
    elif type(s) is Array:
        return __sx2py(s.value, native, occurence, listdic)
    else:
        return s


# py2sx: convert Python list/tuple to S-expression object
def py2sx(l, strassym=True):
    """convert Python list/tuple to S-expression object"""
    occurence = dict()
    s = __py2sx(l, strassym, occurence)
    occurence.clear()
    return s


def __py2sx(l, strassym, occurence):
    if type(l) in {list, tuple}:
        if id(l) in occurence:
            return occurence[id(l)]
        else:
            if l:
                ret = Cons(__py2sx(l[0], strassym, occurence))
                occurence[id(l)] = ret
                s = ret
                for i in l[1:]:
                    s.cdr = Cons(__py2sx(i, strassym, occurence))
                    s = s.cdr
                s.cdr = _NIL
            else:
                ret = _NIL
            return ret
    elif type(l) is str:
        if strassym:
            return Symbol(l)
        else:
            return String(l)
    elif type(l) is complex:
        return Complex(l.real, l.imag)
    elif type(l) in {
        int,
        float,
        Fraction,
        Nil,
        Cons,
        Char,
        Symbol,
        String,
        Complex,
        Array,
    }:
        return l
    else:
        return String(str(l))


# sxpprint: simple pretty-print for S-expression data structure
def sxpprint(s, file=__stdout):
    """simple pretty-print for S-expression"""
    out = file
    occurence = []
    __sxpprint_sub(s, 0, occurence, out)
    out.write("\n")
    occurence.clear()
    del occurence


def __sxpprint_sub(s, n, occurence, out):
    localoccurence = set()
    occurence.append(localoccurence)
    quote = ""
    while sxprlib_enableQuote and consp(s):
        if s.car == Symbol("quote") and consp(s.cdr):
            if null(s.cdr.cdr):
                quote = quote + "'"
                s = s.cdr.car
                continue
        break
    if sxprlib_enableFuncRef and consp(s):
        if s.car == Symbol("function") and consp(s.cdr):
            if null(s.cdr.cdr) and symbolp(s.cdr.car):
                quote = quote + "#'"
                s = s.cdr.car
    if consp(s) or arrayp(s):
        if consp(s):
            if n > 0:
                out.write("\n" + " " * n + quote + "(")  # LF + Indent + '('
            else:
                out.write(quote + "(")  # '('
        else:  #   arrayp(s)
            if s.dim == 1:
                dim = ""
            else:
                dim = "{}A".format(s.dim)
            if n > 0:
                out.write("\n" + " " * n + quote + "#{}(".format(dim))
            else:
                out.write(quote + "#{}(".format(dim))
            s = s.value
        if _inany(id(s), occurence):
            out.write("...)")
            localoccurence.clear()
            return
        localoccurence.add(id(s))
        if consp(s.car):
            occurence2 = []
            occurence2.extend(occurence)
            __sxpprint_sub(s.car, n + 2, occurence2, out)
            occurence2.clear()
        else:
            out.write(str(s.car))
        s = s.cdr
        while consp(s):
            occurence2 = []
            occurence2.extend(occurence)
            __sxpprint_sub(s.car, n + 2, occurence2, out)
            occurence2.clear()
            if _inany(id(s), occurence):
                out.write(" ...)")
                localoccurence.clear()
                return
            localoccurence.add(id(s))
            s = s.cdr
        if null(s):
            out.write(")")
        else:
            out.write(" . " + str(s) + ")")
    else:
        out.write(" " + quote + str(s))
    localoccurence.clear()


# ------------------------------- S-expression Tokenizer


# define token type (LPar, RPar, Dot, Quote, Complex)
class __TokenType:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "{}".format(str(self.value))


__LPar = __TokenType("(")
__RPar = __TokenType(")")
__Dot = __TokenType(".")
__Quote = __TokenType("'")
__FuncRef = __TokenType("#'")
__Complex = __TokenType("#C")
_Undef = __TokenType("<undef>")


# tokenizer
def _next_token(streamer):
    if streamer.lookahead_token is _Undef:
        streamer.lookahead_token = _sxpr_tokenizer(streamer)
    r = streamer.lookahead_token
    streamer.col = streamer.lookahead_col
    streamer.line = streamer.lookahead_line
    if r is not None:
        streamer.lookahead_token = _sxpr_tokenizer(streamer)
    return r


def _sxpr_tokenizer(streamer):
    WHITESPACES = {" ", "\t", "\r", "\n"}
    DELIMITERS = {"(", ")", '"'}.union(WHITESPACES)
    d = streamer.read()
    while d in WHITESPACES:
        d = streamer.read()
    if sxprlib_enableLineComment and d == ";":
        while not d in {"\r", "\n", ""}:
            d = streamer.read()
        return _sxpr_tokenizer(streamer)
    elif sxprlib_enableBlockComment and d == "#" and streamer.lookahead_char == "|":
        _ = streamer.read()  # skip "|"
        d = streamer.read()
        while d != "|" or streamer.lookahead_char != "#":
            d = streamer.read()
            if d == "":
                raise EOFError(
                    "Unexpected EOF: line={}, col={}".format(
                        streamer.line, streamer.col
                    )
                )
        _ = streamer.read()  # skip "#"
        return _sxpr_tokenizer(streamer)
    if d == "":  #                                            #  Empty
        return None
    elif sxprlib_enableQuote and d == "'":  #                 #  Quote
        if streamer.lookahead_char in WHITESPACES:
            return Symbol(d)
        else:
            return __Quote
    elif (
        sxprlib_enableFuncRef and d == "#" and streamer.lookahead_char == "'"
    ):  #  FuncRef
        _ = streamer.read()  # skip "'"
        if streamer.lookahead_char in DELIMITERS:
            return Symbol("#'")
        else:
            return __FuncRef
    elif d == "(":  #                                         #  L-Par
        return __LPar
    elif d == ")":  #                                         #  R-Par
        return __RPar
    elif d == "." and streamer.lookahead_char in DELIMITERS:  #  Dot
        return __Dot
    elif d == '"':  #                                         #  String
        s = ""
        while streamer.lookahead_char != "" and streamer.lookahead_char != '"':
            d = streamer.read()
            if sxprlib_enableEscape and d == "\\":
                d = streamer.read()
                if __is_oct_digit(d):
                    digit = d
                    for _ in (1, 2):
                        if not __is_oct_digit(streamer.lookahead_char):
                            break
                        digit = digit + streamer.read()
                    n = int(digit, 8)
                    d = "{:c}".format(n)
                elif d.lower() == "x" and __is_hex_digit(streamer.lookahead_char):
                    digit = streamer.read()
                    for _ in (1,):
                        if not __is_hex_digit(streamer.lookahead_char):
                            break
                        digit = digit + streamer.read()
                    n = int(digit, 16)
                    d = "{:c}".format(n)
                elif d == "u" and __is_hex_digit(streamer.lookahead_char):
                    digit = streamer.read()
                    for _ in (1, 2, 3):
                        if not __is_hex_digit(streamer.lookahead_char):
                            break
                        digit = digit + streamer.read()
                    n = int(digit, 16)
                    d = "{:c}".format(n)
                elif d == "U" and __is_hex_digit(streamer.lookahead_char):
                    digit = streamer.read()
                    for _ in (1, 2, 3, 4, 5, 6, 7):
                        if not __is_hex_digit(streamer.lookahead_char):
                            break
                        digit = digit + streamer.read()
                    n = int(digit, 16)
                    d = "{:c}".format(n)
                else:
                    d = {
                        "a": "\x07",  # BEL
                        "b": "\x08",  # BS
                        "e": "\x1b",  # ESC
                        "f": "\x0c",  # FF
                        "n": "\n",  # LF
                        "r": "\r",  # CR
                        "t": "\t",  # TAB
                        "v": "\x0b",  # VTAB
                    }.get(d, d)
            s = s + d
        if streamer.lookahead_char == "":
            raise EOFError(
                "Unexpected EOF: line={}, col={}".format(streamer.line, streamer.col)
            )
        _ = streamer.read()  #  skip a trailing '"' character
        return String(s)
    else:
        s = d
        while streamer.lookahead_char != "" and not (
            streamer.lookahead_char in DELIMITERS
        ):
            d = streamer.read()
            s = s + d
        if _is_integer(s):
            return int(s)
        elif _is_number(s):
            return float(
                s.lower().replace("d", "e").replace("f", "e").replace("s", "e")
            )
        elif _is_bin(s) and sxprlib_enableBin:
            val = s.split("/")
            ret = int(val[0].lower().replace("#b", ""), 2)
            if len(val) == 2:
                x = int(val[1], 2)
                ret = Fraction(ret, x)
                if ret.denominator == 1:
                    ret = ret.numerator
            return ret
        elif _is_oct(s) and sxprlib_enableOct:
            val = s.split("/")
            ret = int(val[0].lower().replace("#o", ""), 8)
            if len(val) == 2:
                x = int(val[1], 8)
                ret = Fraction(ret, x)
                if ret.denominator == 1:
                    ret = ret.numerator
            return ret
        elif _is_hex(s) and sxprlib_enableHex:
            val = s.split("/")
            ret = int(val[0].lower().replace("#x", ""), 16)
            if len(val) == 2:
                x = int(val[1], 16)
                ret = Fraction(ret, x)
                if ret.denominator == 1:
                    ret = ret.numerator
            return ret
        elif _is_radix(s) and sxprlib_enableRadix:  #       -#BBrNNNN
            sgnval = s.lower().split("#")  #            ['-', 'BBrNNNN']
            if sgnval[0] == "-":
                sgn = -1
            else:
                sgn = 1
            valstr = sgnval[1].split("r", 1)  #         ['BB', 'NNNN']
            val = valstr[1].split("/")
            base = int(valstr[0], 10)
            try:
                ret = sgn * int(val[0], base)
                if len(val) == 2:
                    x = int(val[1], base)
                    ret = Fraction(ret, x)
                    if ret.denominator == 1:
                        ret = ret.numerator
            except:
                ret = Symbol(s)
            return ret
        elif _is_fraction(s) and sxprlib_enableFrac:
            d = Fraction(s)
            if d.denominator == 1:
                return d.numerator
            else:
                return d
        # elif s.upper() == 'NIL':
        #      return _NIL
        elif s.startswith("#"):
            if sxprlib_enableChar and s.startswith("#\\"):
                if Char.IsChar(s):
                    return Char(s)
                else:
                    return Symbol(s)
            elif sxprlib_enableArray and s == "#" and streamer.lookahead_char == "(":
                return Array(1)
            while streamer.lookahead_char in WHITESPACES:
                d = streamer.read()
            if (
                sxprlib_enableComplex
                and s.upper() == "#C"
                and streamer.lookahead_char == "("
            ):
                return __Complex
            elif (
                sxprlib_enableArray
                and _is_arrayprefix(s)
                and streamer.lookahead_char == "("
            ):
                n = int(s.upper().replace("#", "").replace("A", ""))
                return Array(n)
            return Symbol(str(s))
        else:
            return Symbol(str(s))


# ------------------------------- S-expression Parser

# SXPR : "'" SXPR | real | symbol | string | prfxc '(' real real ')' | prfxc '(' LISTBODY | '(' LISTBODY ;
# LISTBODY : ')' | SXPR CONSSEQ ;
# CONSSEQ : CONSSEQ '.' SXPR ')' | CONSSEQ SXPR ')' ;


def _sxpr_read_obj(streamer):
    # ----------
    if streamer is None:
        return None
    # ----------
    tkn = _next_token(streamer)
    # ----------
    if tkn is None:
        return None
    # ----------
    if tkn is __Quote:
        return Cons(Symbol("quote"), Cons(_sxpr_read_obj(streamer)))
    elif tkn is __FuncRef:
        return Cons(Symbol("function"), Cons(_sxpr_read_obj(streamer)))
    elif type(tkn) in {int, float, Fraction, Symbol, String, Char}:
        return tkn
    elif tkn is __Complex:
        tkn = _next_token(streamer)
        if tkn is __LPar:
            tkn = _next_token(streamer)
            if realp(tkn):
                re = tkn
                tkn = _next_token(streamer)
                if realp(tkn):
                    im = tkn
                    tkn = _next_token(streamer)
                    if tkn is __RPar:
                        return Complex(re, im)
        raise SyntaxError(
            "Invalid Complex expression: line={}, col={}".format(
                streamer.line, streamer.col
            )
        )
    elif type(tkn) is Array:
        if streamer.lookahead_token is __LPar:
            _ = _next_token(streamer)
            tkn.value = _sxpr_read_list(streamer)
            return tkn
        _ = _next_token(streamer)
        raise SyntaxError(
            "Invalid Array expression: line={}, col={}".format(
                streamer.line, streamer.col
            )
        )
    elif tkn is __LPar:
        return _sxpr_read_list(streamer)
    raise SyntaxError(
        "Unexpected token '{}': line={}, col={}".format(
            tkn, streamer.line, streamer.col
        )
    )


def _sxpr_read_list(streamer):
    if streamer.lookahead_token is __RPar:
        _ = _next_token(streamer)  # Skip ')'
        return _NIL
    ret = Cons(_sxpr_read_obj(streamer))
    c = ret
    # ---- CONSSEQ
    while streamer.lookahead_token is not __RPar:
        if streamer.lookahead_token is None:
            _ = _next_token(streamer)  # Skip token to consist with error location
            raise SyntaxError(
                "Unexpected EOF: line={}, col={}".format(streamer.line, streamer.col)
            )
        if streamer.lookahead_token is __Dot:
            _ = _next_token(streamer)  # Skip DOT '.'
            c.cdr = _sxpr_read_obj(streamer)
            if streamer.lookahead_token is not __RPar:
                _ = _next_token(streamer)
                raise SyntaxError(
                    "')' is expected: line={}, col={}".format(
                        streamer.line, streamer.col
                    )
                )
            break
        c.cdr = Cons(_sxpr_read_obj(streamer))
        c = c.cdr
    _ = _next_token(streamer)  # Skip ')'
    return ret


# ------------------------------- Streamer


class SxprStreamerBaseClass:
    def __init__(self):
        self.lookahead_token = _Undef
        self.lookahead_line = 1
        self.lookahead_col = 0
        self.lookahead_char = self._getchar()
        self.line = 1
        self.col = 0

    def read(self):
        v = self.lookahead_char
        if self.lookahead_char != "":
            self.lookahead_char = self._getchar()
        if v in {"\r", "\n"}:
            self.lookahead_col = 0
            self.lookahead_line = self.lookahead_line + 1
        elif v != "":
            self.lookahead_col = (
                self.lookahead_col + eawcolumncount[_east_asian_width(v)]
            )
        return v


# read a character from file and return it one by one
class _FileStreamer(SxprStreamerBaseClass):
    def __init__(self, fd):
        self.__fd = fd
        super().__init__()  # <- required

    def _getchar(self):
        ret = self.__fd.read(1)
        return ret


# read a character from text string and return it one by one
class _StringStreamer(SxprStreamerBaseClass):
    def __init__(self, text):
        if type(text) is not str:
            raise TypeError("_StringStreamer(): {} is not a string".format(repr(text)))
        self.__text = text
        self.__length = len(text)
        self.__index = 0
        super().__init__()  # <- required

    def _getchar(self):
        if self.__index < self.__length:
            v = self.__text[self.__index]
            self.__index = self.__index + 1
        else:
            v = ""
        return v


# ------------------------------- S-expression Reader class


# S-expression Reader Base class
class SxprReaderBaseClass:
    """S-expression Reader Base class"""

    def __call__(self):
        return _sxpr_read_obj(self._streamer)

    def __iter__(self):
        return self

    def __next__(self):
        s = _sxpr_read_obj(self._streamer)
        if s is None:
            raise StopIteration()
        return s


# S-expression File Reader class
class SxprFileReader(SxprReaderBaseClass):
    """S-expression File Reader class"""

    def __init__(self, fd):
        self._streamer = _FileStreamer(fd)


# S-expression String Reader class
class SxprStringReader(SxprReaderBaseClass):
    """S-expression String Reader class"""

    def __init__(self, text):
        self._streamer = _StringStreamer(text)


# ------------------------------- utilities for convenience


# sxparse: read a single S-expression object from a text string
def sxparse(text):
    """S-expression text reader"""
    if type(text) is not str:
        raise TypeError("sxparse(): argument should be a string")
    return SxprStringReader(text)()


# sxopen: read S-expression objects from a file
class sxopen:
    """S-expression file reader"""

    def __init__(self, filename):
        self.__fd = open(filename, "r")
        self.__reader = SxprFileReader(self.__fd)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.__reader is None:
            raise StopIteration()
        s = self.__reader()
        if s is None:
            raise StopIteration()
        return s

    def close(self):
        if self.__fd is not None:
            self.__fd.close()
            self.__fd = None
            del self.__reader
            self.__reader = None

    def read(self):
        if self.__reader is None:
            return None
        return self.__reader()


# [EOF]
