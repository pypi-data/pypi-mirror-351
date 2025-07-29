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

"""Tests rounding (e.g. floor(Fixed) round(Fixed) etc.)
"""

import math
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils


class RoundingTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)

        self.tests = (
            self.test_floor,
            self.test_ceil,
            self.test_trunc,
            *(
                (self.test_round, None, mode)
                for mode in pyfixed.FixedRounding
            ),
            *(
                (self.test_round, ndigits, mode)
                for ndigits in range(-self.integer_bits, self.fraction_bits + 2)
                for mode in pyfixed.FixedRounding
            ),
            self.test_round_overflow,
        )

    def test_floor(self):
        """Test fixed-point flooring
        """

        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert math.floor(value) == mpmath.floor(
                    mpmath.ldexp(value.value, -self.fraction_bits)
                )

    def test_ceil(self):
        """Test fixed-point ceiling
        """

        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert math.ceil(value) == mpmath.ceil(
                    mpmath.ldexp(value.value, -self.fraction_bits)
                )

    def test_trunc(self):
        """Test fixed-point truncating
        """

        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                assert math.trunc(value) == test_utils.mpmath_trunc(
                    mpmath.ldexp(value.value, -self.fraction_bits)
                )

    def test_round(self, ndigits: int, mode: pyfixed.FixedRounding):
        """Test rounding to closest integer

        Args:
            ndigits (int): Number of binary digits after the point to round to
            mode (pyfixed.FixedRounding): Rounding mode
        """

        digits = 0 if ndigits is None else ndigits
        scale = digits - self.fraction_bits
        rounder = test_utils.rounding_modes[mode]
        with mpmath.workprec(max(self.fraction_bits + self.integer_bits, 1)), \
                pyfixed.with_partial_state(rounding=mode):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                expected = mpmath.ldexp(
                    rounder(
                        mpmath.ldexp(
                            value.value,
                            digits - self.fraction_bits
                        )
                    ),
                    0 if ndigits is None else (self.fraction_bits - digits)
                )
                try:
                    assert (
                        round(value) if ndigits is None else round(value, digits).value
                    ) == expected
                except pyfixed.FixedOverflow:
                    assert ndigits is not None and (
                        expected > value._max_val or expected < value._min_val
                    )

    def test_round_overflow(self):
        """Test overflow when rounding to outside the fixed-point range
        """

        # Overflow occurs when ndigits isn't None and the value is rounded above _max_val.
        # Possible rounding modes are CEIL, AWAY, ROUND_HALF_UP, ROUND_HALF_AWAY and
        # ROUND_HALF_TO_EVEN (other modes can't overflow).

        if self.fraction_bits:
            value = pyfixed.Fixed(
                fraction_bits=self.fraction_bits,
                integer_bits=self.integer_bits,
                sign=self.sign
            )
            value.value = value._max_val

            for mode in (
                pyfixed.FixedRounding.CEIL,
                pyfixed.FixedRounding.AWAY,
                pyfixed.FixedRounding.ROUND_HALF_UP,
                pyfixed.FixedRounding.ROUND_HALF_AWAY,
                pyfixed.FixedRounding.ROUND_HALF_TO_EVEN,
            ):
                if mode == pyfixed.FixedRounding.ROUND_HALF_TO_EVEN and value._max_val == 1:
                    continue
                with pyfixed.with_partial_state(rounding=mode):
                    test_utils.behavior_check(
                        'overflow',
                        lambda: round(value, 0)
                    )


test = test_utils.run_tests(RoundingTestSuite)
