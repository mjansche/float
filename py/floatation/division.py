# Copyright 2020, 2021 the floatation authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Long binary division."""


def _div_mod(dividend, divisor, target_precision=64):
    """Perform long division up to the desired target precision.

    Requires that the target ratio (dividend / divisor) falls within
    the interval [1; 2).

    Returns a (quotient, remainder) tuple, where the number of bits in
    the quotient is the requested target precision.
    """
    # Precondition:
    assert dividend > 0
    assert divisor > 0
    assert target_precision >= 1
    assert divisor <= dividend < 2 * divisor

    quotient = 1
    remainder = dividend - divisor
    precision = 1

    def assert_invariant():
        assert quotient >= 1
        assert 0 <= remainder < divisor
        assert 1 <= precision <= target_precision
        prec = precision - 1
        assert (1 << prec) <= quotient < (1 << precision)
        assert quotient * divisor + remainder == dividend << prec
        assert divmod(dividend << prec, divisor) == (quotient, remainder)
        return

    while precision < target_precision:
        assert_invariant()
        quotient <<= 1
        remainder <<= 1
        if remainder >= divisor:
            quotient |= 1
            remainder -= divisor
        precision += 1
    assert_invariant()
    assert precision == target_precision
    return quotient, remainder


def div_mod_exp(dividend, divisor, precision=64):
    """Perform long division with remainder and binary exponent extraction."""
    # Precondition:
    assert dividend >= 0
    assert divisor > 0
    assert precision >= 1

    num = dividend
    den = divisor
    quotient = 0
    remainder = 0
    exponent = 0

    def assert_postcondition():
        assert quotient >= 0
        assert 0 <= remainder < divisor
        assert (quotient == 0) == (dividend == 0)
        scaled_dividend = quotient * divisor + remainder
        effective_exponent = exponent - precision
        if effective_exponent >= 0:
            assert scaled_dividend << effective_exponent == dividend
        else:
            assert scaled_dividend == dividend << abs(effective_exponent)
        return

    def assert_invariant():
        if exponent >= 0:
            assert (num * divisor) << exponent == den * dividend
        else:
            assert num * divisor == (den * dividend) << abs(exponent)
        return

    if dividend == 0:
        assert_postcondition()
        return quotient, remainder, exponent
    assert dividend > 0

    den_shift = 0
    while num >= 2 * den:
        assert_invariant()
        if num & 1 == 0:
            num >>= 1
            exponent += 1
        else:
            den <<= 1
            exponent += 1
            den_shift += 1
    assert_invariant()
    assert num < 2 * den
    while den > num:
        assert_invariant()
        num <<= 1
        exponent -= 1
    assert_invariant()
    assert den <= num < 2 * den

    if num == den:
        quotient = 1 << precision
        quotient >>= 1
        exponent += 1
        assert_postcondition()
        return quotient, remainder, exponent
    assert den < num < 2 * den

    quotient, remainder = _div_mod(num, den, precision)
    # print(num, den, quotient, remainder, den_shift, exponent)
    remainder >>= den_shift
    exponent += 1
    assert_postcondition()
    return quotient, remainder, exponent
