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

"""Utilities for working with binary floating point values."""

import math
import re


FLOAT_RE = re.compile(
    r'(-?)0[xX]([0-9a-fA-F]*)(?:.([0-9a-fA-F]*))?(?:[pP]([-+]?[0-9]+)?)?$')

LOG_10_2 = math.log10(2)


class Float:
    """Representation of normal IEEE binary floating point values."""

    def __init__(self, sign, fraction, exponent, precision):
        self.sign = int(math.copysign(1, sign))
        self.fraction = fraction
        self.exponent = exponent
        self.precision = precision
        return

    @staticmethod
    def from_float(value):
        sign = int(math.copysign(1, value))
        f, exp = math.frexp(value)
        fraction = int(f * (1 << 53))
        exponent = exp
        return Float(sign, fraction, exponent, 53)

    @staticmethod
    def fromhex(string):
        match = FLOAT_RE.match(string)
        sign = -1 if match.group(1) else +1
        int_portion = match.group(2)
        frac_portion = match.group(3)
        exp_portion = match.group(4)
        assert int_portion or frac_portion
        exp = int(exp_portion, 10) if exp_portion else 0
        if int_portion:
            frac = int(int_portion, 16)
            prec = 0
            m = frac
            while m:
                prec += 1
                m >>= 1
            exp += prec
        else:
            frac = 0
            prec = 0
        if frac_portion:
            n = 4 * len(frac_portion)
            frac <<= n
            frac |= int(frac_portion, 16)
            prec += n
        return Float(sign, frac, exp, prec)

    def __eq__(self, other):
        return (self.sign == other.sign and
                self.fraction == other.fraction and
                self.exponent == other.exponent and
                self.precision == other.precision)

    def __hash__(self):
        return hash((self.sign, self.fraction, self.exponent, self.precision))

    def __repr__(self):
        sign = '-' if self.sign < 0 else ''
        frac = self.fraction
        exp = self.exponent
        prec = self.precision
        return f'{sign}0x{frac:x}*2**({exp}-{prec})'

    def __format__(self, format_spec):
        if not format_spec or format_spec == 'g':
            return self.decimal()
        if format_spec == 'b':
            return self.binary()
        if format_spec == 'x':
            return self.hex()
        raise ValueError("Unknown format code %r for object of type Float"
                         % format_spec)

    def hex(self):
        shift = (5 - self.precision) % 4
        return self._format_hex(shift, 1)

    def hex_alt(self):
        shift = 4 - (self.precision % 4)
        return self._format_hex(shift, 4)

    def _format_hex(self, shift, exponent_diff):
        sign = '-' if self.sign < 0 else ''
        frac = '%x' % (self.fraction << shift)
        exp = self.exponent - exponent_diff
        return f'{sign}0x{frac[0]}.{frac[1:]}p{exp:+d}'

    def binary(self):
        sign = '-' if self.sign < 0 else ''
        frac = ('{:0%db}' % self.precision).format(self.fraction)
        exp = self.exponent - 1
        return f'{sign}0b{frac[0]}.{frac[1:]}p{exp:+d}'

    def _as_decimal_float(self):
        if self.fraction == 0:
            return self.sign, 0, 1
        num = self.fraction
        exp = self.exponent - self.precision
        if exp >= 0:
            num <<= exp
            exp = 0
        else:
            num *= 5**abs(exp)
        while num % 10 == 0:
            num //= 10
            exp += 1
        return self.sign, num, exp

    def as_integer_ratio_10(self):
        sign, num, exp = self._as_decimal_float()
        if exp >= 0:
            num *= 10**exp
            den = 1
        else:
            den = 10**abs(exp)
        num *= sign
        return num, den

    def decimal_full(self, round_to=None):
        sign = '-' if self.sign < 0 else ''
        if self.fraction == 0:
            return f'{sign}0'
        _, num, exp = self._as_decimal_float()
        decimal_digits = len(str(num))
        exp += decimal_digits - 1
        if round_to is not None and decimal_digits > round_to:
            divisor = 10**(decimal_digits - round_to)
            num, m = divmod(num, divisor)
            # Round away from zero:
            if 2*m >= divisor:
                num += 1
                if num == 10**round_to:
                    num //= 10
                    exp += 1
            assert 10**(round_to-1) <= num < 10**round_to
        frac = str(num)
        return f'{sign}{frac[0]}.{frac[1:]}e{exp:+d}'

    def decimal(self):
        digits = max(1, int(LOG_10_2 * self.precision))
        return self.decimal_full(digits)

    def as_integer_ratio(self):
        num = self.fraction
        den = 1
        exp = self.exponent - self.precision
        if exp >= 0:
            num <<= exp
            exp = 0
        else:
            exp = abs(exp)
            den <<= exp
        assert exp >= 0
        assert den == (1 << exp)
        # No need to compute the GCD here, since den is a power of 2.
        # It suffices that shifts happen:
        while (num & 1) == (den & 1) == 0:
            num >>= 1
            den >>= 1
            exp -= 1
            assert exp >= 0
            assert den == (1 << exp)
        num *= self.sign
        return num, den

    def rational(self):
        num, den = self.as_integer_ratio()
        if den == 1:
            return str(num)
        return f'{num} / {den}'

    def reduced(self):
        if self.fraction == 0:
            sign = '-' if self.sign < 0 else ''
            return f'{sign}0'
        num = self.fraction
        exp = self.exponent - self.precision
        while (num & 1) == 0:
            num >>= 1
            exp += 1
        num *= self.sign
        if exp == 0:
            return str(num)
        return f'{num}*2**{exp:+d}'

    def set_precision(self, prec):
        if prec == self.precision:
            return
        if prec < self.precision:
            n = 1 << (self.precision - prec)
            div, mod = divmod(self.fraction, n)
            self.fraction = div
            if 2 * mod > n:
                self.fraction += 1
            elif 2 * mod == n:
                # Round to even:
                self.fraction += self.fraction & 1
            if self.fraction >= 1 << prec:
                self.fraction >>= 1
                self.exponent += 1
        else:
            self.fraction <<= prec - self.precision
        self.precision = prec
        return

    def is_normal(self):
        m = 1 << self.precision
        return m//2 <= self.fraction < m

    def float(self):
        frac = self.fraction / (1 << self.precision)
        return self.sign * math.ldexp(frac, self.exponent)

    def ldexp(self, i):
        self.exponent += i
        return
