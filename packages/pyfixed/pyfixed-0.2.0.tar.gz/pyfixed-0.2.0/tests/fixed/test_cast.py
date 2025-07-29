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

"""Tests casting (e.g. int(Fixed) float(Fixed) etc.)
"""

import numpy
import math
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class CastTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_bool,
            *((self.test_int, m) for m in pyfixed.FixedRounding),
            self.test_mpz,
            self.test_float_complex,
            self.test_numpy_int,
            self.test_numpy_float,
            *((self.test_mpf, m) for m in pyfixed.FixedRounding),
            self.test_mpfr,
            self.test_str,
            self.test_bytes,
        )

    def test_bool(self):
        """Tests boolean casting
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            assert bool(value) == bool(value.value)

    def test_int(self, mode: pyfixed.FixedRounding):
        """Tests Python integer casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)), \
                pyfixed.with_partial_state(rounding=mode):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert int(value) == test_utils.rounding_modes[mode](
                    mpmath.ldexp(
                        value.value,
                        -self.fraction_bits
                    )
                )

    def test_mpz(self):
        """Testing gmpy2.mpz casting
        """

        if pyfixed.mpz_type is not int:
            with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)):
                for value in test_utils.fixed_range(
                    self.fraction_bits,
                    self.integer_bits,
                    self.sign
                ):
                    assert value.mpz() == int(value)

    def test_float_complex(self):
        """Tests Python float casting
        """

        if self.fraction_bits + self.integer_bits <= numpy.finfo(float).nmant + 1:
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert float(value) == math.ldexp(value.value, -self.fraction_bits)
                assert complex(value) == float(value)

    def test_numpy_int(self):
        """Tests NumPy integer casting
        """

        for t in (
            numpy.int8,
            numpy.uint8,
            numpy.int16,
            numpy.uint16,
            numpy.int32,
            numpy.uint32,
            numpy.int64,
            numpy.uint64,
        ):
            iinfo = numpy.iinfo(t)

            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                i = int(value)
                if i > iinfo.max or i < iinfo.min:
                    with pytest.raises(OverflowError):
                        t(value)
                else:
                    assert t(value) == i

    def test_numpy_float(self):
        """Tests NumPy float casting
        """

        for f, c in (
            (numpy.float16, None),
            (numpy.float32, numpy.complex64),
            (numpy.float64, numpy.complex128),
            (numpy.float128, numpy.complex256),
        ):
            if self.fraction_bits + self.integer_bits <= numpy.finfo(f).nmant + 1:
                for value in test_utils.fixed_range(
                    self.fraction_bits,
                    self.integer_bits,
                    self.sign
                ):
                    assert f(value) == numpy.ldexp(f(value.value), -self.fraction_bits)
                    if c:
                        assert c(value) == f(value)

    def test_mpf(self, mode: pyfixed.FixedRounding):
        """Tests mpmath casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        bits = self.fraction_bits + self.integer_bits
        half = int(mpmath.ceil(bits / 2))
        diff = bits - half

        with pyfixed.with_partial_state(rounding=mode), mpmath.workprec(bits):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert value.mpmath() == mpmath.ldexp(value.value, -self.fraction_bits)
                assert mpmath.mpf(value) == mpmath.ldexp(value.value, -self.fraction_bits)
                if half < bits:
                    rounded = test_utils.rounding_modes[mode](mpmath.ldexp(value.value, -diff))
                    if (rounded == 0) == (value.value == 0):
                        with mpmath.workprec(half):
                            assert value.mpmath() == mpmath.ldexp(
                                rounded,
                                diff - self.fraction_bits
                            )

    def test_mpfr(self):
        """Tests gmpy2.mpfr casting
        """

        if pyfixed.mpfr_type is not float:
            with pyfixed.gmpy2.context(pyfixed.gmpy2.get_context()) as ctx:
                ctx.precision = max(self.fraction_bits + self.integer_bits, 1)
                for value in test_utils.fixed_range(
                    self.fraction_bits,
                    self.integer_bits,
                    self.sign
                ):
                    assert pyfixed.mpfr_to_mpf(value.mpfr()) == value.mpmath()

    def test_str(self):
        """Tests string casting
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            assert float(value) == float.fromhex(str(value))

    def test_bytes(self):
        """Tests byte casting
        """

        mod = 1 << (self.fraction_bits + self.integer_bits + self.sign)

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            assert int.from_bytes(
                bytes(value),
                byteorder='little',
                signed=False
            ) == value.value % mod


test = test_utils.run_tests(CastTestSuite)


def test_no_gmpy2():
    """Tests that gmpy2 casting fails when gmpy2 isn't imported
    """

    if pyfixed.mpz_type is int:
        with pytest.raises(ModuleNotFoundError):
            pyfixed.Fixed().mpz()

        with pytest.raises(ModuleNotFoundError):
            pyfixed.Fixed().mpfr()
