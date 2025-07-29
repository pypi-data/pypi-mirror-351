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
Efficient operators to be used in TTN python simulator
"""

import logging
from copy import deepcopy

import numpy as np

from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.permutations import (
    _transpose_idx,
    _transpose_idx1,
    _transpose_idx2,
)

from .abstracteffop import _AbstractEffectiveOperators

logger = logging.getLogger(__name__)

__all__ = ["TensorProductOperator", "IndexedOperator"]


class IndexedOperator:
    """
    Class of operator with an index, to keep track
    of tensor product operators in the TTN, i.e.
    MPOs where the bond dimension is 1

    Parameters
    ----------
    op : np.ndarray or str
        Numpy array representing the operator or string of the
        operator
    op_id : int
        Integer op_id of the operator. Operators with the same
        op_id are considered to belong to the same MPO
    coeff : complex
        Coefficient of the operator
    """

    def __init__(self, op, op_id, coeff):
        self._op = op
        self._op_id = op_id
        self._coeff = coeff

        # Enforce rank-four terms
        if self.op.ndim == 2:
            # Reshape
            new_shape = [1] + list(self.op.shape) + [1]
            self._op = self.op.reshape(new_shape)

    @property
    def device(self):
        """Device where the tensor is stored."""
        return self._op.device

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        return self._op.dtype

    @property
    def op(self):
        """Operator property"""
        return self._op

    @property
    def op_id(self):
        """Operator ID property"""
        return self._op_id

    @property
    def coeff(self):
        """Coefficient property"""
        return self._coeff

    def convert(self, dtype, device, stream=None):
        """Convert data type and device of relevant attributes in this instance."""
        self._op.convert(dtype, device, stream)

    def is_gpu(self, query=None):
        """Check if object itself or a device string `query` is a GPU."""
        self._op.is_gpu(query=query)


# pylint: disable-next=too-many-instance-attributes
class TensorProductOperator(_AbstractEffectiveOperators):
    """
    Effective operator class.
    It contains the effective operators in a vector with
    as many entries as links. The first `num_physical_links`
    are always used to store the physical hamiltonian.

    TODO: add read/write method for fortran

    Parameters
    ----------
    params:
        The simulation parameters
    model: QuantumModel
        Quantum model defining the quantum operator
    operators: TNOperators
        Class containing the tensors of the operators
    tensor_network: tensor network class
        Tensor network on which links the efficient operator is defined
    device : str, optional
        Device of the computation. Default to "cpu".
    """

    # pylint: disable-next=super-init-not-called
    # pylint: disable-next=too-many-arguments
    def __init__(self, params, model, operators, tensor_network, device="cpu"):
        if model is None:
            # for @classmethod inits
            return

        self._tensor_network = tensor_network

        # Initialize variables
        self.params = params
        self.model = model
        self.numx = self.model.get_number_of_sites_xyz(params)
        self._ops = operators
        self.num_physical_links = model.get_number_of_sites(params)
        self.num_links = tensor_network.num_links
        self.site_terms = None

        self.eff_ops = {}  # [] for _ in range(self.num_links)]
        # Initialize the pysical layer
        self._extract_physical_terms(tensor_network)
        tensor_network.eff_op = self
        tensor_network.build_effective_operators()

        self.convert(None, device)

    # --------------------------------------------------------------------------
    #                               Properties
    # --------------------------------------------------------------------------

    @property
    def device(self):
        """Device where the tensor is stored."""
        for _, elem_list in self.eff_ops.items():
            for elem in elem_list:
                return elem.device

        raise QTeaLeavesError("Running inquiery on empty effective operator.")

    @property
    def dtype(self):
        """Data type of the underlying arrays."""
        for _, elem_list in self.eff_ops.items():
            for elem in elem_list:
                return elem.dtype

        raise QTeaLeavesError("Running inquiery on empty effective operator.")

    @property
    def num_sites(self):
        """Return the number of sites in the underlying system."""
        return len(self.site_terms)

    @property
    def ops(self):
        """Retrieve the dictionary of operators"""
        return self._ops

    # --------------------------------------------------------------------------
    #                       Classmethod, classmethod-like
    # --------------------------------------------------------------------------

    @classmethod
    def from_mpo_list(cls, dense_mpo_list, tensor_network):
        """Construct a TPO from :Class:`DenseMPOList`."""
        obj = cls(None, None, None, None)
        obj.params = None
        obj.model = None
        obj.numx = None
        obj._ops = None
        obj.num_physical_links = None
        obj.num_links = None
        obj._tensor_network = tensor_network

        obj.eff_ops = {}

        tpo_lists = [[] for _ in range(tensor_network.num_sites)]

        for ii, mpo in enumerate(dense_mpo_list):
            for site in mpo:
                kk = site.site
                tpo_lists[kk] += [
                    IndexedOperator(site.operator, ii, site.total_scaling)
                ]

        obj.site_terms = tpo_lists

        # pylint: disable-next=protected-access
        for ii, key in enumerate(tensor_network._iter_physical_links()):
            obj[key] = tpo_lists[ii]

        tensor_network.eff_op = obj
        tensor_network.build_effective_operators()

        return obj

    @classmethod
    def from_mpo_list_num_sites(cls, dense_mpo_list, num_sites):
        """Construct a TPO from :Class:`DenseMPOList` and the number of sites."""
        obj = cls(None, None, None, None)
        obj.params = None
        obj.model = None
        obj.numx = None
        obj._ops = None
        obj.num_physical_links = None
        obj.num_links = None
        # obj.device = None

        obj.eff_ops = {}

        tpo_lists = [[] for _ in range(num_sites)]

        for ii, mpo in enumerate(dense_mpo_list):
            for site in mpo:
                kk = site.site
                tpo_lists[kk] += [
                    IndexedOperator(site.operator, ii, site.total_scaling)
                ]

        obj.site_terms = tpo_lists

        return obj

    # --------------------------------------------------------------------------
    #                          Overwritten operators
    # --------------------------------------------------------------------------

    def __getitem__(self, key):
        """
        Get the hamiltonian term at index idxs.
        If one index is passed, you receive ALL the hamiltonian
        terms on link `idxs`. If a tuple is passed, then the
        second index is the index of the operator

        Parameters
        ----------
        idxs : int or tuple of ints
            Index of the link and optionally of the operator
            to retrieve

        Returns
        -------
        list of Operator
            efficient operator on the link
        """
        return self.eff_ops[key]

    def __setitem__(self, key, value):
        """
        Set the efficient operator on link idx

        Parameters
        ----------
        idx : int
            Index of the link where to substitute the
            effective operator
        other : list
            New list of effective operators in that link
        """
        self.eff_ops[key] = value

    def __repr__(self):
        """
        Return the class name as representation.
        """
        return self.__class__.__name__

    def __len__(self):
        """
        Provide number of links in efficient operator
        """
        return self.num_links

    def __iter__(self):
        """Iterator protocol"""
        return iter(self.eff_ops)

    # --------------------------------------------------------------------------
    #     Abstract effective operator methods requiring implementation here
    # --------------------------------------------------------------------------

    # pylint: disable-next=too-many-statements, too-many-locals
    def contr_to_eff_op(self, tensor, pos, pos_links, idx_out):
        """
        Contract operators lists with tensor T and its dagger. Return effective
        Hamiltonian operators along idx_out (relative to T),
        resulting from contraction.

        Parameters
        ----------
        T: np.ndarray
                Tensor of the TTN to contract
        ops_list: list of lists of Operator
            list of local operator lists, each corresponding to a
            specific link.
        idx_list:   list of ints
            link indices (relative to T), each corresponding to
            a local operator list in ops_list.

        Returns
        ---------
        list
            list of Operators after contractions
        """
        ops_list = []
        idx_list = []
        pos_link_out = None
        for ii, pos_link in enumerate(pos_links):
            if ii == idx_out:
                pos_link_out = pos_link
                continue

            if pos_link is None:
                continue

            pos_jj = self[(pos_link, pos)]
            ops_list.append(pos_jj)
            idx_list.append(ii)

        if pos_link_out is None:
            raise QTeaLeavesError(
                "Arguments for contraction effective operator mismatch."
            )

        # Put everything in the correct order
        sorting = np.argsort(idx_list)
        ops_list = np.array(ops_list, dtype=object)
        idx_list = np.array(idx_list)
        ops_list = ops_list[sorting]
        idx_list = idx_list[sorting]

        # Retrieve the ID of all the operator passed
        ops_ids = np.array(
            [[opjj.op_id for opjj in opii] for opii in ops_list], dtype=object
        )
        ops_ids_flattened = [op for ops_list in ops_ids for op in ops_list]
        # Get a list of unique IDs
        ids = np.sort(np.unique(ops_ids_flattened))

        tensor_len = len(tensor.shape)
        avail_idx = np.arange(tensor_len, dtype=int)
        avail_idx = np.delete(avail_idx, idx_out)

        tensor_len = len(tensor.shape) + 2
        avail_idx_temp = np.arange(tensor_len, dtype=int)
        avail_idx_temp = np.delete(avail_idx_temp, tensor_len - 1)
        avail_idx_temp = np.delete(avail_idx_temp, idx_out + 1)
        avail_idx_temp = np.delete(avail_idx_temp, 0)

        c_idx_fun = lambda ii, last, is_entered: [last, ii + 1] if is_entered else [ii]

        new_ops = []
        # We could run this for cycle in parallel
        for op_id in ids:
            idxs = [np.nonzero(ops_id == op_id)[0] for ops_id in ops_ids]
            temp = deepcopy(tensor)
            entered = False
            c_idx_o = [2]
            coeff = 1.0
            for ii, common_id in enumerate(idxs):
                # If that ID is present in the list
                if len(common_id) == 1:
                    # Perform the contraction
                    c_idx_t = c_idx_fun(idx_list[ii], temp.ndim - 1, entered)
                    temp = temp.tensordot(
                        ops_list[ii][common_id[0]].op, (c_idx_t, c_idx_o)
                    )

                    if not entered:
                        # Move the link to the left (horizontal) upfront
                        temp = temp.transpose(_transpose_idx2(tensor_len, 0))

                    temp = temp.transpose(_transpose_idx1(tensor_len, idx_list[ii] + 1))
                    # Record the coefficient
                    coeff *= ops_list[ii][common_id[0]].coeff
                    entered = True

                    # For next one, contract as well over right operator link
                    c_idx_o = [0, 2]

            if entered:
                # Perform the contraction with the complex conjugate
                # This order avoids an extra transposition
                new_t = tensor.conj().tensordot(temp, (avail_idx, avail_idx_temp))
                # new_t = xp.tensordot(xp.conj(tensor), temp, (avail_idx, avail_idx))

                # Still need to transpose now for four-link operators
                new_t = new_t.transpose([1, 0, 2, 3])

                # Append to the new operators
                new_ops.append(IndexedOperator(new_t, op_id, coeff))

        if (pos_link_out, pos) in self:
            del self.eff_ops[(pos_link_out, pos)]

        self[(pos, pos_link_out)] = new_ops

    # pylint: disable-next=too-many-statements, too-many-branches, too-many-locals, too-many-arguments
    def contract_tensor_lists(
        self, tensor, pos, pos_links, custom_ops=None, pre_return_hook=None
    ):
        """
        Linear operator to contract all the effective operators
        around the tensor in position `pos`. Used in the optimization.

        Parameters
        ----------
        vector : instance of :class:`_AbstractQteaTensor`
            tensor in position pos in vector form
        pos : list of int
            list of [layer_idx, tensor_idx]
        custom_ops : list of effective operators
            Must be sorted, must match number of links

        Returns
        -------
        np.ndarray
            vector after the contraction of the effective operators
        """
        if not isinstance(tensor, _AbstractQteaTensor):
            raise TypeError("Needs QteaTensor.")

        if custom_ops is None:
            ops_list = []
            idx_list = []
            for ii, pos_link in enumerate(pos_links):
                if pos_link is None:
                    continue
                pos_jj = self[(pos_link, pos)]
                ops_list.append(pos_jj)
                idx_list.append(ii)
        else:
            # Required for time evolution backwards step on R-tensor
            ops_list = custom_ops
            idx_list = list(range(len(ops_list)))

        # Put everything in the correct order
        sorting = np.argsort(idx_list)
        ops_list = np.array(ops_list, dtype=object)
        idx_list = np.array(idx_list)
        ops_list = ops_list[sorting]
        idx_list = idx_list[sorting]

        # Retrieve the ID of all the operator passed
        ops_ids = np.array(
            [[opjj.op_id for opjj in opii] for opii in ops_list], dtype=object
        )
        # Get a list of unique IDs
        ops_ids_flattened = [op for ops_list_id in ops_ids for op in ops_list_id]
        ids = np.sort(np.unique(ops_ids_flattened))

        c_idx_fun = lambda ii, last, is_entered: [last, ii + 1] if is_entered else [ii]

        # new_tens = xp.zeros_like(tensor, dtype=complex)
        new_tens = tensor.zeros_like()
        # We could run this for cycle in parallel
        for op_id in ids:
            idxs = [np.nonzero(ops_id == op_id)[0] for ops_id in ops_ids]
            temp = deepcopy(tensor)
            entered = False
            c_idx_o = [2]
            coeff = 1.0
            for ii, common_id in enumerate(idxs):
                last = ii + 1 == len(idxs)

                if last and entered:
                    c_idx_o = [0, 2, 3]
                    c_idx_t = [temp.ndim - 1, idx_list[ii] + 1, 0]
                elif last:
                    # Last but not entered - local term
                    c_idx_o = [2]
                    c_idx_t = [idx_list[ii]]
                else:
                    c_idx_t = c_idx_fun(idx_list[ii], temp.ndim - 1, entered)

                # If that ID is present in the list
                if len(common_id) == 1:
                    # Perform the contraction
                    temp = temp.tensordot(
                        ops_list[ii][common_id[0]].op, (c_idx_t, c_idx_o)
                    )
                    # temp = xp.tensordot(
                    #    temp, ops_list[ii][common_id[0]].op, ([idx_list[ii]], [1])
                    # )
                    if last and (not entered):
                        # local term
                        temp.trace_one_dim_pair([temp.ndim - 3, temp.ndim - 1])

                        perm = _transpose_idx(temp.ndim, idx_list[ii])
                    elif not entered:
                        # Move the link to the left (horizontal) upfront
                        temp = temp.transpose(_transpose_idx2(temp.ndim, 0))
                        perm = _transpose_idx1(temp.ndim, idx_list[ii] + 1)
                    elif last:
                        perm = _transpose_idx(temp.ndim, idx_list[ii])
                    else:
                        perm = _transpose_idx1(temp.ndim, idx_list[ii] + 1)

                    temp.sanity_check()
                    temp = temp.transpose(perm)
                    # Record the coefficient
                    coeff *= ops_list[ii][common_id[0]].coeff
                    entered = True

                    # For next one, contract as well over right operator link
                    c_idx_o = [0, 2]

            # Fix dimension problem on the fly
            if new_tens.ndim != temp.ndim:
                logger.warning("Fixing left-over dummy legs on the fly.")
                temp.trace_one_dim_pair([0, temp.ndim - 1])

            # Update the tensor
            if entered:
                new_tens.add_update(temp, factor_other=coeff)

        if pre_return_hook is not None:
            ctens = pre_return_hook(ctens)

        return new_tens

    def convert(self, dtype, device):
        """
        Convert underlying array to the speificed data type inplace. Original
        site terms are preserved.
        """

        # We could detect up-conversion and down-conversion. Only for
        # conversion to higher precisions, we have to copy from the
        # site terms again which are in double precision
        if self._tensor_network is None:
            raise QTeaLeavesError("convert needs tensor network to be set.")

        # pylint: disable-next=protected-access
        for ii, key in enumerate(self._tensor_network._iter_physical_links()):
            self[key] = self.site_terms[ii].copy()

        for _, elem_list in self.eff_ops.items():
            for elem in elem_list:
                elem.convert(dtype, device)

    # --------------------------------------------------------------------------
    #                    Overwriting methods from parent class
    # --------------------------------------------------------------------------
    #
    # inheriting: print_summary

    # --------------------------------------------------------------------------
    #                          Methods specific to TPO
    # --------------------------------------------------------------------------

    def update_couplings(self, params):
        """Update term with new parameter dictionary."""
        raise NotImplementedError("Cannot update couplings.")

    def setup_as_eff_ops(self, tensor_network, measurement_mode=False):
        """Set this sparse MPO as effective ops in TN and initialize."""
        if measurement_mode:
            raise ValueError("TPO (old-style) has no measurement mode.")

        self._tensor_network = tensor_network

        # pylint: disable-next=protected-access
        for ii, key in enumerate(tensor_network._iter_physical_links()):
            self[key] = self.site_terms[ii]

        tensor_network.eff_op = self
        tensor_network.build_effective_operators()

    def add_operator(self, name, op):
        """
        Add an operator op named name to the list of
        operators

        Parameters
        ----------
        name : str
            String identifier of the operator
        op : np.ndarray
            Matrix of the operator
        """

        self._ops[name] = op

    def _extract_physical_terms(self, tensor_network):
        """
        Compute the physical hamiltonians on the physical indexes
        of the tensor network based on the input model

        Parameters
        ----------
        tensor_network: tensor network class
            Tensor network on which links the efficient operator is defined
        """
        op_id = 0
        tpo_lists = [[] for _ in range(self.numx[0])]

        # Cycle over the operator terms
        for term in self.model.hterms:
            # Cycle over each element of the terms
            for elem, coords in term.get_interactions(
                self.model.eval_lvals(self.params), self.params, dim=self.model.dim
            ):
                if len(coords) > 2:
                    raise QTeaLeavesError("Problem with symmetry.")

                total_scaling = term.prefactor * term.eval_strength(self.params)
                if "weight" in elem:
                    total_scaling *= elem["weight"]

                for idx, coord in enumerate(coords):
                    op = deepcopy(self.ops[elem["operators"][idx]])
                    if idx == 1 and op.ndim == 4:
                        # Have to shuffle links a bit around for symmetries
                        op.transpose_update([3, 1, 2, 0])
                        op.flip_links_update([0, 3])

                    tpo_lists[coord] += [
                        IndexedOperator(
                            op,
                            op_id,
                            total_scaling,
                        )
                    ]

                    # scaling goes into the first site
                    total_scaling = 1.0

                op_id += 1

        self.site_terms = tpo_lists
        # pylint: disable-next=protected-access
        for ii, key in enumerate(tensor_network._iter_physical_links()):
            elem = tpo_lists[ii].copy()
            self[key] = elem
