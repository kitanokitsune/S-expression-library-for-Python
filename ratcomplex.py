# -*- coding:utf-8 -*-
"""Rational Complex Number Class

This file is a part of S-expression Library for Python (sxprlib.py).
"""
ratcomplex_version = "1.0"
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

from fractions import Fraction
from weakref import WeakValueDictionary as _WVDic

# data type: Complex
class Complex:
    """Definition of Complex data type"""

    # str_format_spec:
    #  {0}:value_real, {1}:value_imag
    #  {2}:sign_real,  {3}:sign_imag
    #  {4}:abs_real,   {5}:abs_imag
    str_format_spec = "{0}{3}{5}i"
    repr_format_spec = "Complex({}, {})"
    __ComplexInstance = _WVDic({})

    def __new__(self, real=0, imag=0):
        v1 = real
        v2 = imag
        if type(v1) in {complex, Complex}:
            if type(v2) in {complex, Complex}:
                real = v1.real - v2.imag
                imag = v1.imag + v2.real
            else:
                real = v1.real
                imag = v1.imag + v2
        else:
            if type(v2) in {complex, Complex}:
                real = v1 - v2.imag
                imag = v2.real
            else:
                real = v1
                imag = v2
        real = Complex.__reduce_frac(real)
        imag = Complex.__reduce_frac(imag)
        if imag == 0:
            return real
        if type(real) is Fraction:
            rnu = real.numerator
            rde = real.denominator
        else:
            rnu = real
            rde = 1
        if type(imag) is Fraction:
            inu = imag.numerator
            ide = imag.denominator
        else:
            inu = imag
            ide = 1
        v = (rnu, rde, inu, ide)
        obj = Complex.__ComplexInstance.get(v)
        if obj is None:
            obj = super().__new__(self)
            obj.real = real
            obj.imag = imag
            Complex.__ComplexInstance[v] = obj
        return obj

    def __str__(self):
        ### str_format_spec:
        ###  {0}:value_real, {1}:value_imag
        ###  {2}:sign_real,  {3}:sign_imag
        ###  {4}:abs_real,   {5}:abs_imag
        if self.real < 0:
            realsgn = "-"
        else:
            realsgn = "+"
        if self.imag < 0:
            imagsgn = "-"
        else:
            imagsgn = "+"
        real = str(self.real)
        realabs = str(abs(self.real))
        imag = str(self.imag)
        imagabs = str(abs(self.imag))
        return Complex.str_format_spec.format(
            real, imag, realsgn, imagsgn, realabs, imagabs
        )

    def __repr__(self):
        return Complex.repr_format_spec.format(repr(self.real), repr(self.imag))

    def __setattr__(self, name, value):
        if name in {"real", "imag"} and name in self.__dict__:
            raise PermissionError("Complex: {} is read only!".format(name))
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in {"real", "imag"}:
            raise PermissionError(name)
        else:
            super().__delattr__(name)

    def __hash__(self):
        if self.imag == 0:
            return hash(self.real)
        elif self == complex(self):
            return hash(complex(self))
        else:
            return hash((self.real, self.imag))

    def __eq__(self, v):
        if type(v) in {complex, Complex}:
            return self.real == v.real and self.imag == v.imag
        else:
            return self.real == v and self.imag == 0

    def __ne__(self, v):
        if type(v) in {complex, Complex}:
            return self.real != v.real or self.imag != v.imag
        else:
            return self.real != v or self.imag != 0

    def __complex__(self):
        return float(self.real) + 1.0j * float(self.imag)

    def __abs__(self):
        if self.real == 0:
            return abs(self.imag)
        elif self.imag == 0:  # this case might not occur
            return abs(self.real)
        else:
            return abs(float(self.real) + 1.0j * float(self.imag))

    def __pos__(self):
        return Complex.__reduce_comp(self.real, self.imag)

    def __neg__(self):
        return Complex.__reduce_comp(-self.real, -self.imag)

    def __add__(self, v):
        if type(v) in {complex, Complex}:
            real = self.real + v.real
            imag = self.imag + v.imag
        else:
            real = self.real + v
            imag = self.imag
        return Complex.__reduce_comp(real, imag)

    def __radd__(self, v):
        if type(v) in {complex, Complex}:
            real = self.real + v.real
            imag = self.imag + v.imag
        else:
            real = self.real + v
            imag = self.imag
        return Complex.__reduce_comp(real, imag)

    def __sub__(self, v):
        if type(v) in {complex, Complex}:
            real = self.real - v.real
            imag = self.imag - v.imag
        else:
            real = self.real - v
            imag = self.imag
        return Complex.__reduce_comp(real, imag)

    def __rsub__(self, v):
        if type(v) in {complex, Complex}:
            real = -self.real + v.real
            imag = -self.imag + v.imag
        else:
            real = -self.real + v
            imag = -self.imag
        return Complex.__reduce_comp(real, imag)

    def __mul__(self, v):
        if type(v) in {complex, Complex}:
            real = self.real * v.real - self.imag * v.imag
            imag = self.real * v.imag + self.imag * v.real
        else:
            real = self.real * v
            imag = self.imag * v
        return Complex.__reduce_comp(real, imag)

    def __rmul__(self, v):
        if type(v) in {complex, Complex}:
            real = self.real * v.real - self.imag * v.imag
            imag = self.real * v.imag + self.imag * v.real
        else:
            real = self.real * v
            imag = self.imag * v
        return Complex.__reduce_comp(real, imag)

    def __truediv__(self, v):
        if type(v) in {complex, Complex}:
            d = v.real * v.real + v.imag * v.imag
            real = (self.real * v.real + self.imag * v.imag) / d
            imag = (self.imag * v.real - self.real * v.imag) / d
        else:
            real = self.real / v
            imag = self.imag / v
        return Complex.__reduce_comp(real, imag)

    def __rtruediv__(self, v):
        if type(v) in {complex, Complex}:
            d = self.real * self.real + self.imag * self.imag
            real = (self.real * v.real + self.imag * v.imag) / d
            imag = (-self.imag * v.real + self.real * v.imag) / d
        else:
            d = self.real * self.real + self.imag * self.imag
            real = self.real * v / d
            imag = -self.imag * v / d
        return Complex.__reduce_comp(real, imag)

    def __pow__(self, v):
        s = complex(self)
        if type(v) is Complex:
            v = complex(v)
        return s**v

    def __rpow__(self, v):
        s = complex(self)
        if type(v) is Complex:
            v = complex(v)
        return v**s

    def conjugate(self):
        return Complex(self.real, -self.imag)

    @staticmethod
    def __reduce_frac(x):
        if type(x) is Fraction:
            if x.denominator == 1:
                return x.numerator
        return x

    @staticmethod
    def __reduce_comp(real, imag):
        real = Complex.__reduce_frac(real)
        imag = Complex.__reduce_frac(imag)
        if imag == 0:
            return real
        else:
            return Complex(real, imag)

    @staticmethod
    def listall():
        return [x for x in Complex.__ComplexInstance]


# [EOF]
