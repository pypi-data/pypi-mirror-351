# MIT License
#
# Copyright (c) 2024-Present Shachar Kraus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Tests initialization (Fixed.__init__)
"""

import numpy
import math
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class InitTestSuite(test_utils.TestSuite):

    def _constructor(self, *args, **kwargs):
        return pyfixed.Fixed(
            *args,
            **kwargs,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign
        )

    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_internal,
            self.test_fixed,
            self.test_bool,
            self.test_int,
            self.test_mpz,
            self.test_numpy_int,
            (self.test_float, float),
            (self.test_float, numpy.float32),
            (self.test_float, numpy.float64),
            (self.test_float, numpy.float128),
            self.test_mpf,
            self.test_mpfr,
            self.test_exceptions,
        )

    def test_internal(self):
        """Tests initialization from an internal value
        """

        bias = -(1 << (self.fraction_bits + self.integer_bits)) if self.sign else 0

        for idx, value in enumerate(
            test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            )
        ):
            assert idx + bias == value.value

    def test_fixed(self):
        """Test initialization from a fixed value
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            assert self._constructor(value).value == value.value

    def test_bool(self):
        """Test initialization from booleans
        """

        if self.integer_bits == 0:
            test_utils.behavior_check('overflow', lambda: self._constructor(True))
            assert self._constructor(False).value == 0
        else:
            for value in (False, True):
                assert self._constructor(value).value == (int(value) << self.fraction_bits)

    def test_int(self):
        """Test initialization from Python integers
        """

        if self.integer_bits + self.sign > 0:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign
            ):
                assert self._constructor(int(value.value)).value == \
                    (value.value << self.fraction_bits)

    def test_mpz(self):
        """Test initialization from gmpy2.mpz
        """

        if pyfixed.mpz_type is not int and self.integer_bits + self.sign > 0:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign
            ):
                assert self._constructor(pyfixed.mpz_type(value.value)).value == \
                    (value.value << self.fraction_bits)

    def test_numpy_int(self):
        """Test initialization from NumPy integers
        """

        int_bits = self.integer_bits + self.sign
        if int_bits > 0 and int_bits <= 64:
            for value in test_utils.fixed_range(
                0,
                self.integer_bits,
                self.sign
            ):
                assert self._constructor(numpy.int64(value.value)).value == \
                    (value.value << self.fraction_bits)

    def test_float(self, float_type: type):
        """Test initialization from floating point

        Args:
            float_type (type): Type to initialize from
        """

        if self.fraction_bits + self.integer_bits <= numpy.finfo(float_type).nmant + 1:
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                f = math.ldexp(value.value, -self.fraction_bits)            \
                    if float_type is float else                             \
                    numpy.ldexp(float_type(value.value), -self.fraction_bits)

                assert self._constructor(f).value == value.value
                assert self._constructor(f + 1j).value == value.value

    def test_mpf(self):
        """Test initialization from mpmath.mpf
        """

        with mpmath.workprec(self.fraction_bits + self.integer_bits + 1):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                f = mpmath.ldexp(value.value, -self.fraction_bits)

                assert self._constructor(f).value == value.value
                assert self._constructor(mpmath.mpc(f, 1)).value == value.value

    def test_mpfr(self):
        """Test initialization from gmpy2.mpfr
        """

        if pyfixed.mpfr_type is not float:
            with pyfixed.gmpy2.context(pyfixed.gmpy2.get_context()) as ctx:
                ctx.precision = self.fraction_bits + self.integer_bits + 1
                for value in test_utils.fixed_range(
                    self.fraction_bits,
                    self.integer_bits,
                    self.sign
                ):
                    f = value.mpfr()
                    assert self._constructor(f).value == value.value
                    assert self._constructor(pyfixed.mpc_type(f, 1)).value == value.value

    def test_exceptions(self):
        """Test initialization exceptions
        """

        # Integers
        test_utils.behavior_check(
            'overflow',
            lambda: self._constructor(1 << self.integer_bits)
        )

        test_utils.behavior_check(
            'overflow',
            lambda: self._constructor(-(1 << self.integer_bits) - 1)
        )

        test_utils.behavior_check(
            'underflow',
            lambda: self._constructor(2 ** (-self.fraction_bits - 1))
        )

        # Floats

        test_utils.behavior_check(
            'overflow',
            lambda: self._constructor(math.ldexp(1, self.integer_bits))
        )

        test_utils.behavior_check(
            'overflow',
            lambda: self._constructor(-math.ldexp(1, self.integer_bits + 1))
        )

        test_utils.behavior_check(
            'underflow',
            lambda: self._constructor(math.ldexp(1, -self.fraction_bits - 1))
        )

        test_utils.behavior_check('overflow', lambda: self._constructor(math.inf))
        test_utils.behavior_check('overflow', lambda: self._constructor(-math.inf))
        test_utils.behavior_check('undefined', lambda: self._constructor(math.nan))


test_all = test_utils.run_tests(InitTestSuite)


def test_config():
    """Tests configuration
    """

    assert pyfixed.Fixed().value == 0

    fraction_bits = 9
    integer_bits = 10
    sign = True

    base = pyfixed.Fixed(fraction_bits=fraction_bits, integer_bits=integer_bits, sign=sign)

    deduced = pyfixed.Fixed(base)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == sign

    deduced = pyfixed.Fixed(base, fraction_bits=fraction_bits + 1)
    assert deduced.fraction_bits == fraction_bits + 1 and\
        deduced.integer_bits == integer_bits and         \
        deduced.sign == sign

    deduced = pyfixed.Fixed(base, integer_bits=integer_bits + 1)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits + 1 and \
        deduced.sign == sign

    deduced = pyfixed.Fixed(base, sign=not sign)
    assert deduced.fraction_bits == fraction_bits and\
        deduced.integer_bits == integer_bits and     \
        deduced.sign == (not sign)

    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(fraction_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(integer_bits=-1)
    with pytest.raises(TypeError):
        _ = pyfixed.Fixed(fraction_bits=0, integer_bits=0, sign=False)
