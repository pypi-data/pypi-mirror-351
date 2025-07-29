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

"""Tests unary operators (e.g. ~Fixed etc.)
"""

import numpy
import mpmath
import pyfixed
import pyfixed.test_utils as test_utils


class UnaryTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (
            self.test_plus,
            self.test_minus,
            self.test_not,
            self.test_abs,
            self.test_sign,
        )

    def test_plus(self):
        """Test unary +
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            assert (+value).value == value.value

    def test_minus(self):
        """Test unary -
        """

        bits = self.fraction_bits + self.integer_bits

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            if self.sign:
                if value.value == -(1 << bits):
                    test_utils.behavior_check('overflow', lambda: -value)
                    with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                        assert (-value).value == (1 << bits) - 1
                else:
                    assert (-value).value == -(value.value)
            else:
                if value.value != 0:
                    test_utils.behavior_check('overflow', lambda: -value)
                with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                    assert (-value).value == 0

    def test_not(self):
        """Test unary ~
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            if self.sign:
                assert (~value).value == ~(value.value)
            else:
                test_utils.behavior_check('overflow', lambda: ~value)
                with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                    assert (~value).value == 0

    def test_abs(self):
        """Test abs(Fixed)
        """

        bits = self.fraction_bits + self.integer_bits

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            if value.value == -(1 << bits):
                test_utils.behavior_check('overflow', lambda: abs(value))
                with pyfixed.with_partial_state(overflow_behavior=pyfixed.FixedBehavior.IGNORE):
                    v = (1 << bits) - 1
                    assert abs(value).value == v
                    assert numpy.abs(value).value == v
            else:
                v = abs(value.value)
                assert abs(value).value == v
                assert numpy.abs(value).value == v

    def test_sign(self):
        """Tests pyfixed.sign(Fixed)
        """

        for value in test_utils.fixed_range(
            self.fraction_bits,
            self.integer_bits,
            self.sign
        ):
            s = mpmath.sign(value.value)
            assert pyfixed.sign(value) == s
            assert numpy.sign(value) == s


test = test_utils.run_tests(UnaryTestSuite)
