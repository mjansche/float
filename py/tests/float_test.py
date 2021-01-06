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

"""Unit test for Float class."""

import unittest

from floatation import Float


class FloatTest(unittest.TestCase):

    DOUBLE_FLOAT = {
        '0x1.fffff70000000p+0': '0x1.fffff8p+0',  # midpoint, round up to even
        '0x1.fffff70000001p+0': '0x1.fffff8p+0',
        '0x1.fffff7fffffffp+0': '0x1.fffff8p+0',
        '0x1.fffff80000000p+0': '0x1.fffff8p+0',  # exact, evem
        '0x1.fffff80000001p+0': '0x1.fffff8p+0',
        '0x1.fffff8fffffffp+0': '0x1.fffff8p+0',
        '0x1.fffff90000000p+0': '0x1.fffff8p+0',  # midpoint, round down to even
        '0x1.fffff90000001p+0': '0x1.fffffap+0',
        '0x1.fffff9fffffffp+0': '0x1.fffffap+0',
        '0x1.fffffa0000000p+0': '0x1.fffffap+0',  # exact, odd
        '0x1.fffffa0000001p+0': '0x1.fffffap+0',
        '0x1.fffffafffffffp+0': '0x1.fffffap+0',
        '0x1.fffffb0000000p+0': '0x1.fffffcp+0',  # midpoint, round up to even
        '0x1.fffffb0000001p+0': '0x1.fffffcp+0',
        '0x1.fffffbfffffffp+0': '0x1.fffffcp+0',
        '0x1.fffffc0000000p+0': '0x1.fffffcp+0',  # exact, even
        '0x1.fffffc0000001p+0': '0x1.fffffcp+0',
        '0x1.fffffcfffffffp+0': '0x1.fffffcp+0',
        '0x1.fffffd0000000p+0': '0x1.fffffcp+0',  # midpoint, round down to even
        '0x1.fffffd0000001p+0': '0x1.fffffep+0',
        '0x1.fffffdfffffffp+0': '0x1.fffffep+0',
        '0x1.fffffe0000000p+0': '0x1.fffffep+0',  # exact, odd
        '0x1.fffffe0000001p+0': '0x1.fffffep+0',
        '0x1.fffffefffffffp+0': '0x1.fffffep+0',
        '0x1.ffffff0000000p+0': '0x1.000000p+1',  # midpoint, round up to even
    }

    def test_round_to_nearest_or_even(self):
        for d, f in FloatTest.DOUBLE_FLOAT.items():
            x = Float.from_float(float.fromhex(d))
            y = Float.fromhex(d)
            self.assertEqual(x, y)
            self.assertEqual(x.hex(), d)
            self.assertEqual(y.hex(), d)
            x.set_precision(24)
            self.assertEqual(x.hex(), f)
        return


if __name__ == '__main__':
    unittest.main()
