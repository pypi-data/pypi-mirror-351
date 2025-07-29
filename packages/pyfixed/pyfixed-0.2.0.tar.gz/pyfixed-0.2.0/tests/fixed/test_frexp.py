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

"""Tests frexp
"""

import mpmath
import pyfixed
import pyfixed.test_utils as test_utils


class FrexpTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)
        self.tests = (self.frexp_test,)

    def frexp_test(self):
        bits = max(self.fraction_bits + self.integer_bits, 1)
        with mpmath.workprec(bits):
            for value in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                f, e = pyfixed.frexp(value)
                assert f.fraction_bits == bits and f.integer_bits == 0 and f.sign == self.sign
                assert isinstance(e, int)

                f = f.mpmath()
                assert (f, e) == mpmath.frexp(value.mpmath())


test = test_utils.run_tests(FrexpTestSuite)
