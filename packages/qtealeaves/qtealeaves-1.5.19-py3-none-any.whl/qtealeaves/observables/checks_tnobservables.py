# This code is part of qtealeaves.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Implement unittest for observables as abstract class.
"""

# pylint: disable=too-many-arguments
# pylint: disable=too-many-instance-attributes

# All the assertX of the unittest class will run into linter checks otherwise
# pylint: disable=no-member

import abc
import os
import tempfile

import numpy as np

import qtealeaves as qtl
import qtealeaves.observables as obs
from qtealeaves.emulator import MPS, TTN
from qtealeaves.operators.spinoperators import TNSpin12Operators
from qtealeaves.simulation.tn_simulation import run_tn_measurements
from qtealeaves.tensors import TensorBackend


class _AbstractTNObservablesChecks(abc.ABC):
    # pylint: disable-next=invalid-name
    def setUp(self):
        """
        Provide some default settings.
        """
        np.random.seed([11, 13, 17, 19])
        self.dtype = None
        self.device = None
        self.tensor_cls = None
        self.base_tensor_cls = None
        self.datamover = None
        self._setup_types_devices()

        self.tensor_backend = TensorBackend(
            tensor_cls=self.tensor_cls,
            base_tensor_cls=self.base_tensor_cls,
            device=self.device,
            dtype=self.dtype,
            datamover=self.datamover,
        )

        self.conv = qtl.convergence_parameters.TNConvergenceParameters(
            max_bond_dimension=16, cut_ratio=1e-16, max_iter=10
        )
        self.ansatz = {5: TTN, 6: MPS}
        self.num_sites = [7, 8]
        self.operators = self.base_tensor_cls.convert_operator_dict(
            TNSpin12Operators(),
            params={},
            symmetries=[],
            generators=[],
            base_tensor_cls=self.base_tensor_cls,
            dtype=self.dtype,
            device=self.device,
        )

        # pylint: disable-next=consider-using-with
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_folder = os.path.join(self.temp_dir.name, "OUTPUT")

        if not os.path.exists(self.out_folder):
            os.mkdir(self.out_folder)

    # pylint: disable-next=invalid-name
    def tearDown(self):
        """Tear down method later used by unittests.TestCase."""
        self.temp_dir.cleanup()

    @abc.abstractmethod
    def _setup_types_devices(self):
        """Define the tensor backend via tensor classes, data type, etc."""

    def _build_state(self, num_sites=8):
        """
        Build GHZ state to use for measurement
        """
        state = np.zeros(2**num_sites)
        state[0] = 1 / np.sqrt(2)
        state[-1] = 1 / np.sqrt(2)
        state = state.reshape([2] * num_sites)
        return state

    def run_measurements(
        self, num_sites, observables, ansatz_id, obsv_id, requires_singvals=True
    ):
        """Measure the given observables using the ghz state"""
        state = self.ansatz[ansatz_id].from_statevector(
            self._build_state(num_sites), tensor_backend=self.tensor_backend
        )
        # Compute singvals for bond_entropy
        if ansatz_id == 5:
            for ii in range(4):
                state.iso_towards(
                    (state.num_layers - 1, ii), keep_singvals=True, trunc=True
                )
            state.iso_towards((state.num_layers - 1, 0), keep_singvals=True, trunc=True)
        else:
            state.iso_towards(state.num_sites - 1, keep_singvals=True, trunc=True)
            state.iso_towards(0, keep_singvals=True, trunc=True)
        if state.is_measured[obsv_id]:
            observables = run_tn_measurements(
                state,
                observables,
                self.operators,
                {},
                self.tensor_backend,
                ansatz_id,
                requires_singvals,
            )
        else:
            observables = None
        return observables

    def test_rho_i(self):
        """test local density matrix, i.e., normalization."""
        for nn in self.num_sites:
            for ansatz_id, ansatz in self.ansatz.items():
                state = ansatz.from_statevector(
                    self._build_state(nn), tensor_backend=self.tensor_backend
                )

                if ansatz_id == 5:
                    for ii in range(4):
                        state.iso_towards(
                            (state.num_layers - 1, ii), keep_singvals=True, trunc=True
                        )
                    state.iso_towards(
                        (state.num_layers - 1, 0), keep_singvals=True, trunc=True
                    )
                else:
                    state.iso_towards(
                        state.num_sites - 1, keep_singvals=True, trunc=True
                    )
                    state.iso_towards(0, keep_singvals=True, trunc=True)

                for ii in range(state.num_sites):
                    rho_i = state.get_rho_i(ii)
                    norm = rho_i.trace(do_get=True)
                    eps = abs(1 - norm)

                    msg = f"Failed on site {ii} for ansatz {ansatz_id}."
                    self.assertLess(eps, 10 * rho_i.dtype_eps, msg=msg)

    def test_local(self):
        """test local observable"""
        obsv = obs.TNObservables()
        obsv += obs.TNObsLocal("X", "sx")
        for nn in self.num_sites:
            true_res = np.zeros(nn)
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 0)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsLocal"].results_buffer["X"]
                cond = np.isclose(res, true_res).all()
                self.assertTrue(
                    cond, msg=f"Local observable failing for ansatz {ansatz_id}"
                )

    def test_correlation(self):
        """test correlation observable"""
        obsv = obs.TNObservables()
        obsv += obs.TNObsCorr("XX", ["sx", "sx"])
        for nn in self.num_sites:
            true_res = np.identity(nn)
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 1)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsCorr"].results_buffer["XX"]
                cond = np.isclose(res, true_res).all()
                self.assertTrue(
                    cond, msg=f"Correlation observable failing for ansatz {ansatz_id}"
                )

    def test_correlation_with_batch_size(self):
        """test correlation observable with batch size."""
        obsv = obs.TNObservables()
        obsv += obs.TNObsCorr("XX", ["sx", "sx"], batch_size=10)
        for nn in self.num_sites:
            true_res = np.identity(nn)
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 1)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsCorr"].results_buffer["XX"]
                cond = np.isclose(res, true_res).all()
                self.assertTrue(
                    cond, msg=f"Correlation observable failing for ansatz {ansatz_id}"
                )

    def test_custom_correlation(self):
        """test custom correlation observable"""
        obsv = obs.TNObservables()
        site_indices = [[1, 2], [3, 6]]
        obsv += qtl.observables.TNObsCustom(
            "custom", ["sx", "sx"], site_indices=site_indices
        )
        for nn in self.num_sites:
            true_res = np.identity(nn)
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 1)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = np.real(obsv.obs_list["TNObsCustom"].results_buffer["custom"])

                # check if custom correlations are correct for TTN
                diff = 0
                for ii, pos in enumerate(site_indices):
                    diff += np.abs(res[ii] - true_res[pos[0], pos[1]])
                self.assertAlmostEqual(
                    diff,
                    0,
                    8,
                    "Custom correlation measurement failing " f"for ansatz {ansatz_id}",
                )

    def test_tensor_product(self):
        """test TNObsTensorProduct observable"""
        for nn in self.num_sites:
            obsv = obs.TNObservables()
            obsv += obs.TNObsTensorProduct(
                "global_flip", ["sx"] * nn, [[ii] for ii in range(nn)]
            )
            true_res = 1
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 4)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsTensorProduct"].results_buffer["global_flip"]
                cond = np.isclose(res, true_res)
                self.assertTrue(
                    cond,
                    msg=f"Tensor product observable failing for ansatz {ansatz_id}",
                )

    def test_weighted_sum(self):
        """test TNObsWeightedSum observable"""
        for nn in self.num_sites:
            obsv = obs.TNObservables()
            tp_1 = obs.TNObsTensorProduct(
                "global_flip", ["sx"] * nn, [[ii] for ii in range(nn)]
            )
            tp_1 += obs.TNObsTensorProduct(
                "parity", ["sz"] * nn, [[ii] for ii in range(nn)]
            )
            obsv += obs.TNObsWeightedSum("obs", tp_1, [1, 2], use_itpo=True)
            true_res = 3 if nn % 2 == 0 else 1
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 5)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsWeightedSum"].results_buffer["obs"]
                cond = np.isclose(res, true_res)
                self.assertTrue(
                    cond, msg=f"Weighted Sum observable failing for ansatz {ansatz_id}"
                )

    def test_projective(self):
        """test TNObsProjective observable"""
        obsv = obs.TNObservables()
        obsv += obs.TNObsProjective(128)
        for nn in self.num_sites:
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 6)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsProjective"].results_buffer[
                    "projective_measurements"
                ]
                cond = "0" * nn in res and "1" * nn in res
                self.assertTrue(
                    cond,
                    msg=f"Projective measurements observable failing for ansatz {ansatz_id}",
                )

    def test_probabilities(self):
        """test TNObsProbabilities observable"""
        prob_types = ["U", "E", "G"]

        for nn in self.num_sites:
            for ansatz_id in self.ansatz:
                for prob_type in prob_types:
                    if (ansatz_id != 6) and (prob_type in ["E", "G"]):
                        continue

                    obsv = obs.TNObservables()
                    obsv += obs.TNObsProbabilities(prob_type=prob_type)

                    obsv = self.run_measurements(nn, obsv, ansatz_id, 7)

                    # Observable not measurable by ansatz
                    if obsv is None:
                        continue

                    file_path = os.path.join(self.out_folder, "observables.dat")
                    with open(file_path, "w+") as fh:
                        obsv.obs_list["TNObsProbabilities"].write_results(fh, True)
                    with open(file_path, "r") as fh:
                        for mode, res in obsv.obs_list["TNObsProbabilities"].read(fh):
                            msg = "Probability measurements observable failing for "
                            msg += f"{ansatz_id=} and {mode=}. \n For a GHZ state the "
                            msg += f"sampled distribution is {res}."
                            cond = "0" * nn in res and "1" * nn in res
                            self.assertTrue(cond, msg=msg)

    def test_bond_entropy(self):
        """test TNObsProbabilities observable"""
        obsv = obs.TNObservables()
        obsv += obs.TNObsBondEntropy()
        for nn in self.num_sites:
            for ansatz_id in self.ansatz:
                obsv = self.run_measurements(nn, obsv, ansatz_id, 8)

                # Observable not measurable by ansatz
                if obsv is None:
                    continue

                res = obsv.obs_list["TNObsBondEntropy"].results_buffer["bond_entropy"]
                entanglement = list(res.values())
                true_ent = 0.6931471805599454
                cond = np.isclose(entanglement, true_ent).all()
                self.assertTrue(
                    cond,
                    msg=f"Entanglement measurements observable failing for ansatz {ansatz_id}",
                )
