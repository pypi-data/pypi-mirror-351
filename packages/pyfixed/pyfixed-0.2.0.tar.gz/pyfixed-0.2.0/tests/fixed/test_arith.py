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

"""Tests basic arithmetics
"""

import math
import mpmath
import numpy
import pyfixed
import pyfixed.test_utils as test_utils
import pytest

# Operations dictionary for mpmath
OP_DICT = {
    '__iadd__': lambda a, b: a + b,
    '__isub__': lambda a, b: a - b,
    '__imul__': lambda a, b: a * b,
    '__itruediv__': lambda a, b: a / b,
    '__ifloordiv__': lambda a, b: mpmath.floor(a / b),
    '__floordiv__': lambda a, b: mpmath.floor(a / b),
    '__rfloordiv__': lambda a, b: mpmath.floor(b / a),
    '__imod__': lambda a, b: test_utils.mpmath_divmod(a, b)[1],
    '__mod__': lambda a, b: test_utils.mpmath_divmod(a, b)[1],
    '__rmod__': lambda a, b: test_utils.mpmath_divmod(b, a)[1],
    '__divmod__': test_utils.mpmath_divmod,
    '__rdivmod__': lambda a, b: test_utils.mpmath_divmod(b, a),
    # Avoid mpz infecting mpmath's exponents
    '__ilshift__': lambda a, b: mpmath.ldexp(a, int(b)),
    '__lshift__': lambda a, b: mpmath.ldexp(a, int(b)),
    '__irshift__': lambda a, b: mpmath.ldexp(a, -int(b)),
    '__rshift__': lambda a, b: mpmath.ldexp(a, -int(b)),
    '__iand__': test_utils.mpmath_and,
    '__and__': test_utils.mpmath_and,
    '__rand__': lambda a, b: test_utils.mpmath_and(b, a),
    '__ior__': test_utils.mpmath_or,
    '__or__': test_utils.mpmath_or,
    '__ror__': lambda a, b: test_utils.mpmath_or(b, a),
    '__ixor__': test_utils.mpmath_xor,
    '__xor__': test_utils.mpmath_xor,
    '__rxor__': lambda a, b: test_utils.mpmath_xor(b, a),
}


def op_template(lhs, rhs, op: str, mod_mode: pyfixed.FixedRounding):
    """Operation test template

    Args:
        lhs (any): Left hand side argument
        rhs (any): Right hand side argument
        op (str): Operation to perform (Python function)
        mod_mode (pyfixed.FixedRounding): Modulo rounding mode
    """

    rhs_float = isinstance(rhs, (float, numpy.floating, mpmath.mpf, pyfixed.mpfr_type))
    op_assign = op.startswith('__i')
    float_result = not op_assign and not op in (
        '__eq__', '__ne__', '__gt__', '__ge__', '__lt__', '__le__'
    ) and rhs_float

    def run_op():
        return test_utils.operation_executer(lhs, rhs, op)

    if op.startswith('__r') and not 'shift' in op and isinstance(rhs, pyfixed.Fixed):
        assert getattr(lhs, op)(rhs) is NotImplemented
        return

    if ('div' in op or 'mod' in op) and not (bool(lhs) if op.startswith('__r') else bool(rhs)):
        if op_assign or not rhs_float:
            # Check how pyfixed handles division by 0
            test_utils.behavior_check('undefined', run_op)
        # else skip
        return

    # Calculate expected result
    conv_lhs = lhs.mpmath()
    # Convert to mpf
    if isinstance(rhs, pyfixed.Fixed):
        conv_rhs = rhs.mpmath()
    elif isinstance(rhs, (int, numpy.integer, pyfixed.mpz_type)):
        conv_rhs = pyfixed.backend(rhs)
    elif isinstance(rhs, (float, numpy.floating)):
        conv_rhs = mpmath.mpmathify(rhs)
    elif isinstance(rhs, pyfixed.mpfr_type):
        conv_rhs = pyfixed.mpfr_to_mpf(rhs)
    else:
        conv_rhs = rhs

    # Calculate the precise result, without fixed-point simulation
    if hasattr(conv_lhs, op) and not 'mod' in op:
        precise_expected = getattr(conv_lhs, op)(conv_rhs)
    else:
        if float_result:
            # pyfixed doesn't control rounding when using floats, and test_utils needs to know that
            with pyfixed.with_partial_state(modulo_rounding=pyfixed.FixedRounding.FLOOR):
                precise_expected = OP_DICT[op](conv_lhs, conv_rhs)
        else:
            precise_expected = OP_DICT[op](conv_lhs, conv_rhs)

    # Get the result and its type
    with pyfixed.with_partial_state(
            overflow_behavior=pyfixed.FixedBehavior.IGNORE,
            underflow_behavior=pyfixed.FixedBehavior.IGNORE,
            undefined_behavior=pyfixed.FixedBehavior.IGNORE
    ):
        actual = run_op()

    assert actual is not NotImplemented

    if float_result:
        # Result should be float

        if pyfixed.mpfr_type is not float and isinstance(rhs, pyfixed.mpfr_type):
            def fixed_to_rhs(x):
                return x.mpfr()
        else:
            fixed_to_rhs = type(rhs)

        if not isinstance(rhs, mpmath.mpf):
            # mpmath differs in the way it handles infinite values
            precise_expected = test_utils.operation_executer(fixed_to_rhs(lhs), rhs, op)

        if 'divmod' in op:
            assert all([type(a) == type(rhs) for a in actual])
            assert all([p == a or (p != p and a != a)
                       for p, a in zip(precise_expected, actual)])
        else:
            assert type(actual) == type(rhs)
            assert precise_expected == actual or (
                precise_expected != precise_expected and actual != actual)
        return

    # Simulate fixed-point behavior
    def sim(x, a):
        # Round like pyfixed
        result = mpmath.ldexp(
            test_utils.rounding_modes[pyfixed.get_fixed_state().rounding](
                mpmath.ldexp(
                    x,
                    a.fraction_bits
                )
            ),
            -a.fraction_bits
        )

        has_underflow = (
            (
                '__divmod__' != op and
                'div' in op and
                not op.startswith('__r') and
                mpmath.isinf(conv_rhs) and
                not mpmath.isnan(conv_rhs)
            ) or
            (
                (
                    'add' in op or
                    'sub' in op or
                    'mul' in op or
                    'div' in op and op.startswith('__r') or
                    'mod' in op and op.startswith('__r')
                ) and conv_rhs and abs(conv_rhs) < mpmath.ldexp(1, -a.fraction_bits)
            ) or
            x and abs(x) < mpmath.ldexp(1, -a.fraction_bits) or
            (result == 0 and x != 0)
        )

        # Saturate

        sat_result = min(
            max(
                result,
                mpmath.ldexp(a._min_val, -a.fraction_bits)
            ),
            mpmath.ldexp(a._max_val, -a.fraction_bits)
        )

        return (
            sat_result,
            has_underflow,
            (
                'add' in op or
                'sub' in op or
                ('mul' in op and conv_lhs != 0)
            ) and mpmath.isinf(conv_rhs) or
            not mpmath.isnan(result) and result != sat_result
        )

    if isinstance(precise_expected, tuple):
        # divmod can't raise underflow, and rdivmod only raises for rmod
        e1, _, has_overflow1 = sim(precise_expected[0], actual[0])
        e2, has_underflow, has_overflow2 = sim(precise_expected[1], actual[1])
        expected = e1, e2
        has_overflow = has_overflow1 or has_overflow2
    elif not isinstance(precise_expected, bool):
        expected, has_underflow, has_overflow = sim(precise_expected, actual)
    else:
        expected = precise_expected
        has_underflow = False  # precise_expected is bool
        has_overflow = False

    with pyfixed.with_partial_state(
        overflow_behavior=pyfixed.FixedBehavior.STICKY,
        underflow_behavior=pyfixed.FixedBehavior.STICKY,
        undefined_behavior=pyfixed.FixedBehavior.STICKY
    ):
        # Run operation
        run_op()
        # Read exception flags
        of, uf, ud = pyfixed.get_sticky()

    if of or uf or ud:
        underflow_value = 0
        undefined_value = 0

        error = []
        if of:
            error.append('overflow')
        if uf:
            error.append('underflow')
        if ud:
            error.append('undefined')

        assert ud or of == has_overflow
        assert (
            uf == has_underflow or
            has_overflow and not uf or
            (
                'mod' in op and
                not 'r' in op and
                not 'div' in op and
                has_underflow and
                conv_rhs and abs(conv_rhs) < mpmath.ldexp(1, -lhs.fraction_bits - 1)
            )
            or
            (
                'rmod' in op and
                not 'div' in op and
                has_underflow and
                abs(conv_rhs) > mpmath.ldexp(1, 2 * lhs.integer_bits)
            )
            or
            (
                op == '__divmod__' and
                ud and
                conv_rhs and abs(conv_rhs) < mpmath.ldexp(1, -lhs.fraction_bits - 1)
            )
        )

        if 'divmod' in op:
            with pyfixed.with_partial_state(
                overflow_behavior=pyfixed.FixedBehavior.IGNORE,
                underflow_behavior=pyfixed.FixedBehavior.IGNORE,
                undefined_behavior=pyfixed.FixedBehavior.IGNORE
            ):
                if op == '__divmod__':
                    tmp = lhs._common_copy(rhs)           \
                        if isinstance(rhs, pyfixed.Fixed) \
                        else lhs._create_copy()
                    assert tmp._div(
                        rhs,
                        rounded_bits=tmp.fraction_bits,
                        rounding=mod_mode,
                        check_underflow=False
                    ) == actual[0] and lhs.__mod__(rhs) == actual[1]
                else:
                    assert lhs._reverse_div(
                        rhs,
                        rounded_bits=lhs.fraction_bits,
                        rounding=mod_mode,
                        check_underflow=False
                    ) == actual[0] and lhs.__rmod__(rhs) == actual[1]
                test_utils.behavior_check(
                    error,
                    run_op,
                    check_values=False
                )
                return

        if ud:
            # Remove NaNs
            expected = 0

            if op in ('__imod__', '__mod__'):
                assert not mpmath.isfinite(conv_rhs) or \
                    abs(conv_rhs) < mpmath.ldexp(1, -lhs.fraction_bits - 1)
            elif op == '__rmod__':
                assert not mpmath.isfinite(conv_rhs) or (
                    isinstance(rhs, (float, numpy.floating, mpmath.mpf, pyfixed.mpfr_type)) and
                    abs(conv_rhs) > (pyfixed.backend_one << (2 * lhs.integer_bits))
                )
            else:
                assert not mpmath.isfinite(precise_expected)
                undefined_value = mpmath.ldexp(expected, actual.fraction_bits)

        if uf:
            underflow_value = mpmath.ldexp(expected, actual.fraction_bits)

        test_utils.behavior_check(
            error,
            run_op,
            underflow_value=underflow_value,
            undefined_value=undefined_value
        )

    # Extract internal value and convert for comparison
    if not isinstance(expected, bool):
        actual = (
            mpmath.ldexp(actual[0].value, -actual[0].fraction_bits),
            mpmath.ldexp(actual[1].value, -actual[1].fraction_bits)
        ) if isinstance(actual, tuple)\
            else mpmath.ldexp(actual.value, -actual.fraction_bits)

    # Compare
    assert expected == actual


# Shared ranges
FLOAT_RANGES = (
    # Floating types
    (test_utils.float_range, float),
    (test_utils.float_range, numpy.float32),
    (test_utils.float_range, numpy.float64),
    (test_utils.float_range, numpy.float128),
    (test_utils.cast_range, test_utils.float_range, mpmath.mpf, float),
    (test_utils.cast_range, test_utils.float_range, pyfixed.mpfr_type, float)
    if pyfixed.mpfr_type is not float
    else None,
    # Invalid floats
    (test_utils.iterator, math.inf, -math.inf, math.nan),
    (test_utils.iterator, numpy.inf, -numpy.inf, numpy.nan),
    (test_utils.iterator, mpmath.inf, -mpmath.inf, mpmath.nan),
    (
        test_utils.iterator,
        pyfixed.mpfr_type(math.inf),
        pyfixed.mpfr_type(-math.inf),
        pyfixed.mpfr_type(math.nan)
    )
    if pyfixed.mpfr_type is not float
    else None,
)


class ArithmeticsTestSuite(test_utils.TestSuite):
    def __init__(self, *args, **kwargs):
        test_utils.TestSuite.__init__(self, *args, **kwargs)

        self.workprec = max(
            2 * (self.fraction_bits + self.integer_bits),
            # mpmath rounds to even internally, so to avoid that we need to
            # be able to represent every possible input with exact precision
            int(
                numpy.finfo(numpy.float128).maxexp -
                numpy.log2(numpy.finfo(numpy.float128).smallest_subnormal)
            )
        )

        dummy_fixed = pyfixed.Fixed(
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign
        )

        fixed_min = pyfixed.Fixed(
            value=dummy_fixed._min_val,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            internal=True
        )
        fixed_max = pyfixed.Fixed(
            value=dummy_fixed._max_val,
            fraction_bits=self.fraction_bits,
            integer_bits=self.integer_bits,
            sign=self.sign,
            internal=True
        )

        fixed_int_range = (4 * math.floor(fixed_min), 4 * (math.ceil(fixed_max) + 1))

        self.int_ranges = (
            # Same type
            (
                test_utils.fixed_range,
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ),
            # Bigger fixed
            (
                test_utils.fixed_range,
                self.fraction_bits + self.integer_bits + self.sign,
                self.fraction_bits + self.integer_bits + self.sign,
                True
            ),
            # Smaller fixed
            (
                test_utils.fixed_range,
                self.fraction_bits // 2,
                self.integer_bits // 2,
                True
            ),
            # Integral types
            (test_utils.iterator, False, True),
            (test_utils.int_range, int, *fixed_int_range),
            (test_utils.int_range, numpy.int64, *fixed_int_range),
            (test_utils.int_range, numpy.uint64, *fixed_int_range),
            (test_utils.int_range, pyfixed.mpz_type, *fixed_int_range)
            if pyfixed.mpz_type is not int
            else None,
        )

        self.ranges = self.int_ranges + FLOAT_RANGES

        bits = self.fraction_bits + self.integer_bits + self.sign
        shift_range = (-2 * bits, 2 * (bits+1))
        self.shift_ranges = (
            (test_utils.int_range, int, *shift_range),
            (test_utils.int_range, numpy.int64, *shift_range),
            (test_utils.int_range, numpy.uint64, *shift_range),
            (test_utils.int_range, pyfixed.mpz_type, *shift_range)
            if pyfixed.mpz_type is not int
            else None,
        )

        self.tests = (
            *(
                (
                    self.test_op,
                    mode,
                    None,
                    op,
                    rhs
                )
                for rhs in self.ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__iadd__',
                    '__add__',
                    '__radd__',
                    '__isub__',
                    '__sub__',
                    '__rsub__',
                    '__imul__',
                    '__mul__',
                    '__rmul__',
                    '__itruediv__',
                    '__truediv__',
                    '__rtruediv__',
                    '__ifloordiv__',
                    '__floordiv__',
                    '__rfloordiv__',
                )
            ),
            *(
                (
                    self.test_op,
                    None,  # No rounding is performed
                    None,
                    op,
                    rhs
                )
                for rhs in self.ranges
                for op in (
                    '__eq__',
                    '__ne__',
                    '__lt__',
                    '__le__',
                    '__gt__',
                    '__ge__',
                )
            ),
            *(
                (
                    self.test_op,
                    mode,
                    mod_mode,
                    op,
                    rhs
                )
                for rhs in self.ranges
                for mode in pyfixed.FixedRounding
                for mod_mode in pyfixed.FixedRounding
                for op in (
                    '__imod__',
                    '__mod__',
                    '__rmod__',
                    '__divmod__',
                    '__rdivmod__',
                )
            ),
            *(
                (
                    self.test_op,
                    mode,
                    None,
                    op,
                    rhs
                )
                for rhs in self.shift_ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__ilshift__',
                    '__lshift__',
                    '__irshift__',
                    '__rshift__',
                )
            ),
            *(
                (
                    self.test_op,
                    mode,
                    None,
                    op,
                    rhs
                )
                for rhs in self.int_ranges
                for mode in pyfixed.FixedRounding
                for op in (
                    '__iand__',
                    '__and__',
                    '__rand__',
                    '__ior__',
                    '__or__',
                    '__ror__',
                    '__ixor__',
                    '__xor__',
                    '__rxor__',
                )
            ),
            *(
                (
                    self.test_not_implemented,
                    op,
                    rhs
                )
                for rhs in (
                    float,
                    numpy.float32,
                    numpy.float64,
                    numpy.float128,
                    mpmath.mpf,
                    pyfixed.mpfr_type,
                )
                for op in (
                    '__ilshift__',
                    '__lshift__',
                    '__irshift__',
                    '__rshift__',
                    '__iand__',
                    '__and__',
                    '__rand__',
                    '__ior__',
                    '__or__',
                    '__ror__',
                    '__ixor__',
                    '__xor__',
                    '__rxor__',
                )
            ),
        )

    def test_op(self, mode: pyfixed.FixedRounding, mod_mode: pyfixed.FixedRounding, op: str, rhs):
        """Tests a single operation under a certain configuration

        Args:
            mode (pyfixed.FixedRounding): Rounding mode
            mod_mode (pyfixed.FixedRounding): Modulo rounding mode
            op (str): Operation to test
            rhs (iterable): RHS values
        """

        if rhs is None:
            return

        with mpmath.workprec(self.workprec),                                       \
                pyfixed.with_partial_state(rounding=mode, modulo_rounding=mod_mode):
            for lhs in test_utils.fixed_range(
                self.fraction_bits,
                self.integer_bits,
                self.sign
            ):
                for val in rhs[0](*(rhs[1:])):
                    op_template(lhs, val, op, mod_mode)

    def test_not_implemented(self, op: str, rhs: type):
        """Tests a single operation with an unsupported data type

        Args:
            op (str): Operation to test
            rhs (type): Unsupported type to test
        """

        with pytest.raises(TypeError):
            assert test_utils.operation_executer(
                pyfixed.Fixed(
                    fraction_bits=self.fraction_bits,
                    integer_bits=self.integer_bits,
                    sign=self.sign
                ),
                rhs(0),
                op
            ) is NotImplemented


test = test_utils.run_tests(ArithmeticsTestSuite)
