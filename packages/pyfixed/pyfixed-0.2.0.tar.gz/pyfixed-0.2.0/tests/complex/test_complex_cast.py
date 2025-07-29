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

"""Tests casting (e.g. int(ComplexFixed) float(ComplexFixed) etc.)
"""

import numpy
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils
import pytest


class CastTestSuite(test_utils.TestSuite):
    def _range(self):
        return test_utils.complex_range(
            test_utils.fixed_range,
            pyfixed.ComplexFixed,
            self.fraction_bits,
            self.integer_bits,
            self.sign
        )

    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_bool,
            *((self.test_int, m) for m in pyfixed.FixedRounding),
            self.test_mpz,
            self.test_float_complex,
            self.test_numpy_int,
            self.test_numpy_float,
            *((self.test_mpf_mpc, m) for m in pyfixed.FixedRounding),
            self.test_mpfr_mpc,
            self.test_str,
            self.test_bytes,
        )

    def test_bool(self):
        """Tests boolean casting
        """

        for value in self._range():
            assert bool(value) == (bool(value.real) or bool(value.imag))

    def test_int(self, mode: pyfixed.FixedRounding):
        """Tests Python integer casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)), \
                pyfixed.with_partial_state(rounding=mode):
            for value in self._range():
                assert int(value) == int(value.real)

    def test_mpz(self):
        """Tests gmpy2.mpz casting
        """

        if pyfixed.mpz_type is not int:
            for value in self._range():
                assert value.mpz() == value.real.mpz()

    def test_float_complex(self):
        """Tests Python float casting
        """

        if self.fraction_bits + self.integer_bits <= numpy.finfo(float).nmant + 1:
            for value in self._range():
                assert float(value) == float(value.real)
                assert complex(value) == complex(float(value.real), float(value.imag))

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
            for value in self._range():
                if int(value.real) > iinfo.max or int(value.real) < iinfo.min:
                    # imag isn't casted
                    with pytest.raises(OverflowError):
                        t(value)
                else:
                    assert t(value) == t(value.real)

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
                for value in self._range():
                    assert f(value) == f(value.real)
                    if c:
                        assert c(value) == f(value.real) + 1j * f(value.imag)

    def test_mpf_mpc(self, mode: pyfixed.FixedRounding):
        """Tests mpmath casting

        Args:
            mode (pyfixed.FixedRounding): Rounding mode to test
        """

        with pyfixed.with_partial_state(rounding=mode), \
                mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)):
            for value in self._range():
                assert value.mpmath() == mpmath.mpc(value.real, value.imag)

    def test_mpfr_mpc(self):
        """Tests gmpy2 casting
        """

        if pyfixed.mpfr_type is not float:
            with pyfixed.gmpy2.context(pyfixed.gmpy2.get_context()) as ctx:
                ctx.precision = max(self.fraction_bits + self.integer_bits, 1)
                for value in self._range():
                    assert value.mpfr() == value.real.mpfr()
                    assert value.mpc() == pyfixed.mpc_type(
                        value.real.mpfr(),
                        value.imag.mpfr()
                    )

    def test_str(self):
        """Tests string casting
        """

        for value in self._range():
            i_sign = "-" if value.imag < 0 else "+"
            r, i = str(value).split(i_sign + ' 1j * ')
            assert float(value) == float.fromhex(r)
            assert float(value.imag) == float.fromhex(i_sign + i)

    def test_bytes(self):
        """Tests byte casting
        """

        for value in self._range():
            assert bytes(value) == bytes(value.real) + bytes(value.imag)


test = test_utils.run_tests(CastTestSuite)


def test_no_gmpy2():
    """Tests that gmpy2 casting fails when gmpy2 isn't imported
    """

    if pyfixed.mpz_type is int:
        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpz()

        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpfr()

        with pytest.raises(ModuleNotFoundError):
            pyfixed.ComplexFixed().mpc()
