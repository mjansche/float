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

"""Unit test for division."""

import unittest

from floatation.division import div_mod_exp


class DivisionTest(unittest.TestCase):

    DIV_MOD_TESTDATA = {
        (0, 1, 64): (0, 0, 0),
        (1, 2, 64): (0x8000000000000000, 0, 0),
        (1, 3, 64): (0xaaaaaaaaaaaaaaaa, 2, -1),
        (1, 7, 64): (0x9249249249249249, 1, -2),
        (1, 13, 64): (0x9d89d89d89d89d89, 11, -3),
        (45, 3, 64): (0xf000000000000000, 0, 4),
        (45 << 66, 3, 64): (0xf000000000000000, 0, 70),
    }

    def test_div_mod_exp(self):
        for args, expected in DivisionTest.DIV_MOD_TESTDATA.items():
            observed = div_mod_exp(*args)
            self.assertEqual(observed, expected)
        return


if __name__ == '__main__':
    unittest.main()
