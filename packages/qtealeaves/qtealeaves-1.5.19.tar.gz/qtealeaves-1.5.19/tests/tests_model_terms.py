# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import unittest
from pprint import pprint

import numpy as np

from qtealeaves.modeling import LocalTerm, PlaquetteTerm2D, TwoBodyTerm3D, _ModelTerm


class TestsModelTerms(unittest.TestCase):
    def test_get_interactions_TwoBodyTerm3D(self):
        """
        Test the method for periodic and open boundary conditions
        for the TwoBodyTerm3D
        """
        ll = 4
        ll3 = [ll, ll, ll]
        params = {}

        # isotropy_xyz = True
        # -------------------

        bc0_dic = {4: 16 * 4 * 3, 2: 24}
        bc1_dic = {4: 144, 2: 12}

        term = TwoBodyTerm3D(["sx", "sx"], [1, 0, 0], has_obc=False)
        term.map_type = "HilbertCurveMap"
        lst = [ii for ii in term.get_interactions(ll3, params)]
        if len(lst) != bc0_dic[ll]:
            pprint(lst)
        self.assertEqual(len(lst), bc0_dic[ll])

        term = TwoBodyTerm3D(["sx", "sx"], [1, 0, 0], has_obc=True)
        term.map_type = "HilbertCurveMap"
        lst = [ii for ii in term.get_interactions(ll3, params)]
        self.assertEqual(len(lst), bc1_dic[ll])

        # isotropy_xyz = False
        # --------------------

        bc0_dic = {4: 16 * 4, 2: 8}
        bc1_dic = {4: 16 * 3, 2: 4}

        term = TwoBodyTerm3D(["sx", "sx"], [1, 0, 0], has_obc=False, isotropy_xyz=False)
        term.map_type = "HilbertCurveMap"
        lst = [ii for ii in term.get_interactions(ll3, params)]
        if len(lst) != bc0_dic[ll]:
            pprint(lst)
        self.assertEqual(len(lst), bc0_dic[ll])

        term = TwoBodyTerm3D(["sx", "sx"], [1, 0, 0], has_obc=True, isotropy_xyz=False)
        term.map_type = "HilbertCurveMap"
        lst = [ii for ii in term.get_interactions(ll3, params)]
        self.assertEqual(len(lst), bc1_dic[ll])

    def test_get_interactions_PlaquetteTerm(self):
        """
        Test the method for periodic and open boundary conditions
        for the PlaquetteTerm
        """
        ll = 4
        ll2 = [ll, ll]
        params = {}

        plaquettes = np.array(
            [
                [[0, 3, 1, 2], [1, 2, 14, 13], [14, 13, 15, 12], [15, 12, 0, 3]],
                [[3, 4, 2, 7], [2, 7, 13, 8], [13, 8, 12, 11], [12, 11, 3, 4]],
                [[4, 5, 7, 6], [7, 6, 8, 9], [8, 9, 11, 10], [11, 10, 4, 5]],
                [[5, 0, 6, 1], [6, 1, 9, 14], [9, 14, 10, 15], [10, 0, 5, 15]],
            ]
        )
        operators = ["sz"] * 4

        # No mask, zzzz
        # -------------

        term = PlaquetteTerm2D(operators, has_obc=False)
        term.map_type = "HilbertCurveMap"
        lst = [ii[1] for ii in term.get_interactions(ll2, params)]

        correct = []
        for elem in term.get_interactions(ll2, params):
            coord = elem[1]
            correct.append(coord in plaquettes)
        correct = all(correct) and (len(correct) == 16)
        if not correct:
            pprint(lst)
        self.assertTrue(
            correct, "Plaquette term with no mask and periodic boundary is wrong"
        )

        term = PlaquetteTerm2D(operators, has_obc=True)
        term.map_type = "HilbertCurveMap"
        correct = []
        for elem in term.get_interactions(ll2, params):
            coord = elem[1]
            correct.append(coord in plaquettes)
        correct = all(correct) and (len(correct) == 9)
        self.assertTrue(
            correct, "Plaquette term with no mask and open boundary is wrong"
        )

        # Mask, only even plaquettes
        # --------------------------

        mask = lambda x: np.array(
            [[(ii + jj) % 2 == 0 for ii in range(ll)] for jj in range(ll)]
        )
        plaquettes = plaquettes[mask(None)]

        term = PlaquetteTerm2D(operators, has_obc=False, mask=mask)
        term.map_type = "HilbertCurveMap"
        lst = [ii[1] for ii in term.get_interactions(ll2, params)]

        correct = []
        for elem in term.get_interactions(ll2, params):
            coord = elem[1]
            correct.append(coord in plaquettes)
        correct = all(correct) and (len(correct) == 8)
        if not correct:
            pprint(lst)
        self.assertTrue(
            correct, "Plaquette term with mask and periodic boundary is wrong"
        )

        term = PlaquetteTerm2D(operators, has_obc=True, mask=mask)
        term.map_type = "HilbertCurveMap"
        correct = []
        for elem in term.get_interactions(ll2, params):
            coord = elem[1]
            correct.append(coord in plaquettes)
        correct = all(correct) and (len(correct) == 5)
        self.assertTrue(correct, "Plaquette term with mask and open boundary is wrong")

    def test_eval_strength(self):
        """
        Test the method for evaluating terms strength.
        """
        term = _ModelTerm()
        key, val = "key", 1.0
        params = {key: val}
        func = lambda params: params[key]
        for strength in (val, key, func):
            term.strength = strength
            self.assertEqual(term.eval_strength(params), val)

    def test_count(self):
        """
        Test the method for counting number of terms.
        """
        ll = 4
        params = {"L": ll}

        def staggered(params):
            return (np.arange(params["L"]) % 2).astype(bool)

        term = LocalTerm("ID", mask=staggered)
        self.assertEqual(term.count(params), ll // 2)
