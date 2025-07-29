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
Dense Matrix Product Operators representing Hamiltonians.
"""
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-public-methods

import logging
import warnings
from copy import deepcopy

import numpy as np

from qtealeaves.abstracttns.abstract_matrix_tn import _AbstractMatrixTN
from qtealeaves.convergence_parameters import TNConvergenceParameters
from qtealeaves.operators import TNOperators
from qtealeaves.tensors import TensorBackend
from qtealeaves.tensors.abstracttensor import _AbstractQteaTensor
from qtealeaves.tooling import QTeaLeavesError
from qtealeaves.tooling.parameterized import _ParameterizedClass
from qtealeaves.tooling.restrictedclasses import _RestrictedList

__all__ = ["MPOSite", "DenseMPO", "DenseMPOList"]

logger = logging.getLogger(__name__)


class MPOSite(_ParameterizedClass):
    """
    One site in a dense MPO term.

    **Arguments**

    site : integer
        Site index.

    str_op : str
        Key for the operator.

    pstrength : pstrength, callable, numeric
        Containing the parameterization of the term.

    weight : scalar
        Scalar constant prefactor.

    operators : :class:`TNOperators` or None
        If present, operators will be directly extracted.

    params : dict or None
        If present, parameterization will be directly extracted.
    """

    def __init__(self, site, str_op, pstrength, weight, operators=None, params=None):
        self.site = site
        self.str_op = str_op
        self.pstrength = pstrength

        self.operator = (
            None if operators is None else deepcopy(operators[(site, str_op)])
        )
        self.strength = (
            None if params is None else self.eval_numeric_param(self.pstrength, params)
        )
        if self.pstrength is None:
            self.strength = 1.0
        self.weight = weight

    @property
    def total_scaling(self):
        """Returns the scaling combining params and weight."""
        return self.strength * self.weight

    def copy_with_new_op(self, operator):
        """
        Create a copy of self, but without replacing the operator with the one passed.
        Corresponding string identifier will be set to `None`.
        """
        obj = deepcopy(self)
        obj.operator = operator
        obj.str_op = None

        return obj

    def initialize(self, operators, params):
        """Resolve operators and parameterization for the given input."""
        self.set_op(operators)
        self.set_param(params)

    def set_op(self, operators):
        """Resolve operators for the given input."""
        if self.str_op is None:
            raise QTeaLeavesError("Operator string no longer available.")
        self.operator = operators[(self.site, self.str_op)]

    def set_param(self, params):
        """Resolve parameterization for the given input."""
        if self.pstrength is None:
            self.strength = 1.0
            return

        strength = self.eval_numeric_param(self.pstrength, params)

        if hasattr(strength, "__len__"):
            raise QTeaLeavesError("Strength cannot be a list.")

        if strength == 0.0:
            warnings.warn("Adding term with zero-coupling.")

        self.strength = strength


class DenseMPO(_AbstractMatrixTN, _RestrictedList):
    """Dense MPO as a list of :class:`MPOSite's."""

    class_allowed = MPOSite

    def __init__(
        self,
        sites=None,
        convergence_parameters=None,
        is_oqs=False,
        tensor_backend=TensorBackend(),
        require_singvals=False,
        local_dim=2,
    ):
        if convergence_parameters is None:
            # Not really allowed in the next step
            convergence_parameters = TNConvergenceParameters()
        if sites is None:
            sites = []
        _RestrictedList.__init__(self, sites)
        _AbstractMatrixTN.__init__(
            self,
            num_sites=1,
            convergence_parameters=convergence_parameters,
            local_dim=local_dim,
            requires_singvals=require_singvals,
            tensor_backend=tensor_backend,
        )

        self.is_oqs = is_oqs

    @property
    def num_sites(self):
        """Length of the Dense MPO"""
        return len(self)

    @property
    def sites(self):
        """Generate list of site indices."""
        sites = [elem.site for elem in self]
        return sites

    def get_tensor_of_site(self, idx):
        """
        Return the tensor representing the MPO operator at site `idx`
        """
        return self[idx].operator

    def _iter_tensors(self):
        """Iterate over all tensors forming the tensor network (for convert etc)."""
        for ii in range(self.num_sites):
            yield self.get_tensor_of_site(ii)

    def __len__(self):
        return super(_RestrictedList, self).__len__()

    def __setitem__(self, index, elem):
        """
        New setitem with the possibility of just setting the tensor
        """
        if isinstance(elem, _AbstractQteaTensor):
            site = self[index]
            site.operator = elem
            site.str_op = f"MPO_{index}"
        else:
            site = elem
        super(_RestrictedList, self).__setitem__(index, self._check_class(site))

    def append(self, elem):
        """Overwriting append to extend as well the list of singvals."""
        super().append(elem)

        # Copy last singvals - assumption: cannot change with local operators
        self._singvals.append(self._singvals[-1])

    def compress_links(self, idx_start, idx_end, trunc=False, conv_params=None):
        """
        Compresses links between sites in a dense MPO by performing a QR or SVD,
        optionally performs the additional truncation along the way.

        Parameters
        ----------
        idx_start : int
            MPO site from which to start the compression.

        idx_end : int
            MPO site on which to end the compression.

        trunc : Boolean, optional
            If True, the truncation will be done according to the `conv_params`.
            Default to False.

        conv_params : :py:class:`TNConvergenceParameters`, optional
            Convergence parameters for the truncation. Must be specified if
            `trunc` is set to True.
            Default to `None`.
        """
        # pylint: disable=access-member-before-definition
        if len(self) > len(self._singvals):
            # Note: the linter does not recognize the call to
            # super, which initializes _singlvals in the _AbstractMatrixTN
            # pylint: disable=attribute-defined-outside-init, access-member-before-definition
            self._singvals = [None] * (len(self) * 2)
        self.iso_towards(idx_start, True)
        self.iso_towards(idx_end, True, trunc, conv_params)

    def add_identity_on_site(self, idx, link_vertical):
        """
        Add identity with the correct links to neighboring terms on site `idx`.

        Parameters
        ----------
        idx : int
            Site to which add the identity. Goes from 0 to num sites in a system.

        link_vertical : link as returned by corresponding QteaTensor
            Needed to build the local Hilbert space (in case it is different across
            the system).
        """
        if len(self) == 0:
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on empty DenseMPO."
            )

        sites = np.array(self.sites)
        if np.any(sites[1:] - sites[:-1] <= 0):
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on unsorted DenseMPO."
            )

        if idx in self.sites:
            raise QTeaLeavesError("Site is already in DenseMPO.")

        sites = np.array(self.sites + [idx])

        # Figure out the index where to insert
        # the identity, and the index of the site
        # on the left of it.
        # This takes care of the periodic boundary
        # conditions on the indices of the dense_mpo.
        sites_sorted = sorted(sites)
        insert_site_index = sites_sorted.index(idx)
        left_index = insert_site_index - 1

        op = self[left_index].operator
        if op is None:
            raise QTeaLeavesError(
                "Cannot use `add_identity_on_site` on uninitialized DenseMPO."
            )

        eye_horizontal = op.eye_like(op.links[3])
        eye_vertical = op.eye_like(link_vertical)

        # Contract together
        eye_horizontal.attach_dummy_link(0, False)
        eye_vertical.attach_dummy_link(0, True)

        eye = eye_horizontal.tensordot(eye_vertical, ([0], [0]))
        eye.transpose_update([0, 2, 3, 1])

        key = str(id(eye))
        op_dict = TNOperators()
        op_dict[key] = eye

        # add it to the correct site
        site = MPOSite(idx, key, None, 1.0, operators=op_dict, params={})

        self.insert(insert_site_index, site)

        # add the singular values, identity cannot change them, so insert
        # the same ones
        self._singvals.insert(insert_site_index, self._singvals[insert_site_index])

    def initialize(self, operators, params):
        """Resolve operators and parameterization for the given input for each site."""
        for elem in self:
            elem.initialize(operators, params)

    def sort_sites(self):
        """Sort sites while and install matching link for symmetries."""

        sites = [elem.site for elem in self]

        # Potentially no fast return possible here, because even if the sites
        # are sorted, we need to manage the links for symmetric tensor
        # networks
        if not self[0].operator.has_symmetry:
            if all(sites[ii] <= sites[ii + 1] for ii in range(len(sites) - 1)):
                # sites already sorted, return
                return self

        inds = np.argsort(sites)

        dims_l = [elem.operator.shape[0] for elem in self]
        dims_r = [elem.operator.shape[3] for elem in self]

        max_l = np.max(dims_l)
        max_r = np.max(dims_r)

        max_chi = max(max_l, max_r)

        if max_chi == 1:
            return self._sort_sites_chi_one(inds)

        raise QTeaLeavesError("For now, we only sort product terms.")

    def pad_identities(self, num_sites, eye_ops):
        """Pad identities on sites which are not in MPO yet respecting the symmetry."""
        sites = np.array([elem.site for elem in self])
        if np.any(sites[1:] - sites[:-1] < 1):
            sorted_mpo = self.sort_sites()
            return sorted_mpo.pad_identities(num_sites, eye_ops)

        raise QTeaLeavesError("Not implemtented yet.")

    def _sort_sites_chi_one(self, inds):
        """Sorting sites in the case of bond dimension equal to one."""
        new_mpo = DenseMPO(is_oqs=self.is_oqs, tensor_backend=self._tensor_backend)
        link = self[0].operator.dummy_link(self[0].operator.links[0])

        for ii in inds:
            # Trivial tensor porting the sector
            one = self._tensor_backend(
                [link, link],
                ctrl="O",
                are_links_outgoing=[False, True],
                device=self[ii].operator.device,
                dtype=self[ii].operator.dtype,
            )
            one.attach_dummy_link(2, True)

            op = self[ii].operator.copy().attach_dummy_link(4, is_outgoing=False)
            tens = one.tensordot(op, ([2], [4]))

            # We have six links [left, right-1, right-former-left, bra, ket, right-2]
            tens.transpose_update([0, 3, 4, 1, 2, 5])
            tens.fuse_links_update(3, 5)

            mpo_site = self[ii].copy_with_new_op(tens)
            new_mpo.append(mpo_site)

            # For the next loop iteration
            link = new_mpo[-1].operator.links[-1]

        # Check that MPO does conserve symmetry
        if not self.is_oqs:
            new_mpo[-1].operator.assert_identical_irrep(3)

        return new_mpo

    @classmethod
    def from_matrix(
        cls,
        matrix,
        sites,
        dim,
        conv_params,
        tensor_backend=TensorBackend(),
        operators=TNOperators(),
        pad_with_identities=False,
    ):
        """
        For a given matrix returns dense MPO form decomposing with SVDs

        Parameters
        ----------
        matrix : QteaTensor | ndarray
            Matrix to write in (MPO) format
        sites : List[int]
            Sites to which the MPO is applied
        dim : int
            Local Hilbert space dimension
        conv_params : :py:class:`TNConvergenceParameters`
            Input for handling convergence parameters.
            In particular, in the LPTN simulator we
            are interested in:
            - the maximum bond dimension (max_bond_dimension)
            - the cut ratio (cut_ratio) after which the
            singular values in SVD are neglected, all
            singular values such that
            :math:`\\lambda` /:math:`\\lambda_max`
            <= :math:`\\epsilon` are truncated
        tensor_backend : instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        pad_with_identities: bool, optional
            If True, pad with identities the sites between min(sites) and max(sites)
            that have no operator. Default to False.

        Return
        ------
        DenseMPO
            The MPO decomposition of the matrix
        """

        if not isinstance(matrix, tensor_backend.tensor_cls):
            matrix = tensor_backend.tensor_cls.from_elem_array(matrix)

        mpo = cls(
            convergence_parameters=conv_params,
            tensor_backend=tensor_backend,
            local_dim=dim,
        )
        bond_dim = 1
        names = []
        work = matrix

        op_set_name = operators.set_names[0]

        if len(operators.set_names) > 1:
            raise QTeaLeavesError(
                "Can use matrix to MPO decomposition only for one set of operators."
            )

        site_cnt = 0
        for ii in range(sites[0], sites[-1], 1):
            if ii in sites:
                #                dim  dim**(n_sites-1)
                #  |                 ||
                #  O  --[unfuse]-->  O   --[fuse upper and lower legs]-->
                #  |                 ||
                #
                # ==O==  --[SVD, truncating]-->  ==O-o-O==
                #
                #                 | |
                #  --[unfuse]-->  O-O           ---iterate
                #                 | |
                #             dim   dim**(n_sites-1)
                work = np.reshape(
                    work,
                    (
                        bond_dim,
                        dim,
                        dim ** (len(sites) - 1 - site_cnt),
                        dim,
                        dim ** (len(sites) - 1 - site_cnt),
                    ),
                )
                tens_left, work, _, _ = work.split_svd(
                    [0, 1, 3], [2, 4], contract_singvals="R", conv_params=conv_params
                )
                bond_dim = deepcopy(work.shape[0])
                operators[(op_set_name, f"mpo{ii}")] = tens_left
                names.append(f"mpo{ii}")
                site_cnt += 1
            elif pad_with_identities:
                operators[(op_set_name, f"id{ii}")] = DenseMPO.generate_mpo_identity(
                    bond_dim, dim, bond_dim, tensor_backend
                )
                names.append((op_set_name, f"id{ii}"))

        work = work.reshape((work.shape[0], dim, dim, 1))
        operators[(op_set_name, f"mpo{sites[-1]}")] = work
        names.append(f"mpo{sites[-1]}")
        # Note: the linter does not recognize the call to
        # super, which initializes _local_dim in the _AbstractMatrixTN
        # pylint: disable=attribute-defined-outside-init
        mpo._local_dim = np.zeros(len(sites), dtype=int)

        cnt = 0
        for site, name in zip(sites, names):
            mpo.append(MPOSite(site, name, 1, 1, operators=operators))

            mpo._local_dim[cnt] = mpo[cnt].operator.shape[1]
            mpo._singvals.append(None)
            cnt += 1
        # pylint: disable=attribute-defined-outside-init
        mpo._iso_center = (cnt - 1, cnt)
        return mpo

    @classmethod
    def from_tensor_list(
        cls,
        tensor_list,
        conv_params=None,
        iso_center=None,
        tensor_backend=TensorBackend(),
        operators=TNOperators(),
        sites=None,
    ):
        """
        Initialize the dense MPO from a list of tensors.

        Parameters
        ----------
        tensor_list : List[QteaTensor] | List[MPOSite]
            Matrix to write in (MPO) format
        conv_params : :py:class:`TNConvergenceParameters`, None
            Input for handling convergence parameters. Default to None
        iso_center : None, int, List[int], str, optional
            If None, the center is None.
            If str, the iso center is installed
            If int, the iso center is that integer.
            Default is None
        tensor_backend : instance of :class:`TensorBackend`
            Default for `None` is :class:`QteaTensor` with np.complex128 on CPU.
        operators: TNOperators, optional
            Operator class
        sites : List[int], None
            Sites to which the MPO is applied. If None, they are assumed to be
            [0, 1, ..., len(tensorlist)-1]. Default to None

        Return
        ------
        DenseMPO
            The MPO decomposition of the matrix
        """
        if sites is None:
            sites = list(range(len(tensor_list)))

        mpo = cls(convergence_parameters=conv_params, tensor_backend=tensor_backend)

        # Check if they are MPOSites
        if isinstance(tensor_list[0], MPOSite):
            tensor_list = [ss.operator * ss.weight for ss in tensor_list]

        names = []
        for ii, tens in enumerate(tensor_list):
            operators[f"mpo{ii}"] = tens
            names.append(f"mpo{ii}")

        # pylint: disable=attribute-defined-outside-init
        mpo._local_dim = np.zeros(len(tensor_list), dtype=int)
        cnt = 0
        for site, name in zip(sites, names):
            mpo.append(
                MPOSite(site, name, pstrength=None, weight=1, operators=operators)
            )
            mpo._local_dim[cnt] = mpo[cnt].operator.shape[1]
            mpo._singvals.append(None)
            cnt += 1

        if isinstance(iso_center, str):
            mpo.install_gauge_center()
        elif isinstance(iso_center, int):
            # Note: the linter does not recognize the call to
            # super, which initializes iso_center in the _AbstractMatrixTN
            # pylint: disable=attribute-defined-outside-init
            mpo._iso_center = (iso_center, iso_center + 2)
        elif isinstance(iso_center, (list, tuple)):
            # pylint: disable=attribute-defined-outside-init
            mpo.iso_center = iso_center

        return mpo

    @staticmethod
    def generate_mpo_identity(left_bd, local_dim, right_bd, tensor_backend):
        """
        Generate an identity in MPO form with given dimensions.
        """
        id_tens = tensor_backend([left_bd, local_dim, local_dim, right_bd])
        for ii in range(min(left_bd, right_bd)):
            id_tens.set_subtensor_entry(
                [ii, 0, 0, ii],
                [ii + 1, local_dim, local_dim, ii + 1],
                id_tens.eye_like(local_dim),
            )

        return id_tens

    ############################################################
    # Abstract methods that should not work with the DenseMPO
    ############################################################
    @classmethod
    def from_density_matrix(
        cls, rho, n_sites, dim, conv_params, tensor_backend=None, prob=False
    ):
        """Conversion of density matrix to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_lptn(cls, lptn, conv_params=None, **kwargs):
        """Conversion of LPTN to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_mps(cls, mps, conv_params=None, **kwargs):
        """Conversion of MPS to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_ttn(cls, ttn, conv_params=None, **kwargs):
        """Conversion of TTN to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def from_tto(cls, tto, conv_params=None, **kwargs):
        """Conversion of TTO to DenseMPO (not implemented yet)."""
        raise NotImplementedError("Feature not yet implemented.")

    @classmethod
    def product_state_from_local_states(
        cls,
        mat,
        padding=None,
        convergence_parameters=None,
        tensor_backend=None,
    ):
        """
        Construct a product (separable) state in a suitable tensor network form, given the local
        states of each of the sites.
        """
        raise NotImplementedError(
            "DenseMPO cannot be initialized from local product state."
        )

    @classmethod
    def ml_initial_guess(
        cls, convergence_parameters, tensor_backend, initialize, ml_data_mpo, dataset
    ):
        """
        Generate an initial guess for a tensor network machine learning approach.

        Arguments
        ---------

        convergence_parameters : :py:class:`TNConvergenceParameters`
            Class for handling convergence parameters. In particular, the parameter
            `ini_bond_dimension` is of interest when aiming to tune the bond dimension
            of the initial guess.

        tensor_backend : :class:`TensorBackend`
            Selecting the tensor backend to run the simulations with.

        initialize : str
            The string ``superposition-data`` will trigger the superposition of the
            data set. All other strings will be forwarded to the init method of the
            underlying ansatz.

        ml_data_mpo : :class:`MLDataMPO`
            MPO of the labeled data set to be learned including the labels.

        dataset : List[:class:`MPS`]
            Data set represented as list of MPS states. Same order as in
            `ml_data_mpo`.

        Returns
        -------

        ansatz : :class:`_AbstractTN`
            Standard initialization of TN ansatz or Weighted superposition of the
            data set, wehere the weight is the label-value plus an offset of 0.1.
        """
        raise NotImplementedError("DenseMPO has no support for machine learning yet.")

    @classmethod
    def mpi_bcast(cls, state, comm, tensor_backend, root=0):
        """
        Broadcast a whole tensor network.

        Arguments
        ---------

        state : :class:`DenseMPO` (for MPI-rank root, otherwise None is acceptable)
            State to be broadcasted via MPI.

        comm : MPI communicator
            Send state to this group of MPI processes.

        tensor_backend : :class:`TensorBackend`
            Needed to identity data types and tensor classes on receiving
            MPI threads (plus checks on sending MPI thread).

        root : int, optional
            MPI-rank of sending thread with the state.
            Default to 0.
        """
        raise NotImplementedError("DenseMPO cannot be broadcasted yet.")

    @classmethod
    def from_statevector(
        cls, statevector, local_dim=2, conv_params=None, tensor_backend=None
    ):
        """No statevector for operators"""
        raise NotImplementedError("No statevector for operators")

    def get_rho_i(self, idx):
        """No density matrix for operators"""
        raise NotImplementedError("No density matrix for operators")

    # pylint: disable-next=unused-argument
    def to_dense(self, true_copy=False):
        """Convert into a TN with dense tensors (without symmetries)."""
        return

    @classmethod
    def read(cls, filename, tensor_backend, cmplx=True, order="F"):
        """Read a MPO from a formatted file."""
        raise NotImplementedError("No read method for DenseMPO")

    def apply_projective_operator(self, site, selected_output=None, remove=False):
        """No measurements in MPO"""
        raise NotImplementedError("No apply_projective_operator method for DenseMPO")

    def ml_get_gradient_single_tensor(self, pos):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version. Not implemented.
        """
        raise NotImplementedError("ML gradient for DenseMPO.")

    def ml_get_gradient_two_tensors(self, pos, pos_p=None):
        """
        Get the gradient w.r.t. to the tensor at ``pos`` similar to the
        two-tensor version. Not implemented.
        """
        raise NotImplementedError("ML gradient for DenseMPO.")

    def ml_two_tensor_step(self, pos, num_grad_steps=1):
        """
        Do a gradient descent step via backpropagation with two tensors
        and the label link in the environment.
        """
        raise NotImplementedError("ML gradient descent for DenseMPO.")

    # pylint: disable-next=unused-argument
    def build_effective_operators(self, measurement_mode=False):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _convert_singvals(self, dtype, device):
        """Pass"""
        return

    def _iter_physical_links(self):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def get_bipartition_link(self, pos_src, pos_dst):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def get_pos_links(self, pos):
        """Pass"""
        return

    def norm(self):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def set_singvals_on_link(self, pos_a, pos_b, s_vals):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _update_eff_ops(self, id_step):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def _partial_iso_towards_for_timestep(self, pos, next_pos, no_rtens=False):
        """Pass"""
        return

    # pylint: disable-next=unused-argument
    def get_pos_partner_link_expansion(self, pos):
        """
        Get the position of the partner tensor to use in the link expansion
        subroutine

        Parameters
        ----------
        pos : int | Tuple[int]
            Position w.r.t. which you want to compute the partner

        Returns
        -------
        int | Tuple[int]
            Position of the partner
        int
            Link of pos pointing towards the partner
        int
            Link of the partner pointing towards pos
        """

    def to_statevector(self, qiskit_order=False, max_qubit_equivalent=20):
        """No statevector for operators"""
        raise NotImplementedError("No statevector for operators")

    def write(self, filename, cmplx=True):
        """Write the TN in python format into a FORTRAN compatible format."""
        raise NotImplementedError("No write method for DenseMPO")


class DenseMPOList(_RestrictedList):
    """Collection of dense MPOs, i.e., for building iTPOs or other MPOs."""

    class_allowed = DenseMPO

    @property
    def has_oqs(self):
        """Return flag if the `DenseMPOList` contains any open system term."""
        has_oqs = False
        for elem in self:
            logger.debug("elem.is_oqs %s %s", has_oqs, elem.is_oqs)
            has_oqs = has_oqs or elem.is_oqs

        return has_oqs

    @classmethod
    def from_model(cls, model, params, tensor_backend=TensorBackend()):
        """Fill class with :class:`QuantumModel` and its parameters."""
        obj = cls()

        lx_ly_lz = model.eval_lvals(params)
        for term in model.hterms:
            for elem, coords in term.get_interactions(lx_ly_lz, params, dim=model.dim):
                weight = term.prefactor
                if "weight" in elem:
                    weight *= elem["weight"]

                pstrength = term.strength
                mpo = DenseMPO(is_oqs=term.is_oqs, tensor_backend=tensor_backend)

                for idx, coord in enumerate(coords):
                    site_term = MPOSite(
                        coord, elem["operators"][idx], pstrength, weight
                    )
                    mpo.append(site_term)
                    # pylint: disable-next=protected-access
                    mpo._singvals.append(None)

                    # Only needed on first site
                    pstrength = None
                    weight = 1.0

                obj.append(mpo)

        return obj

    def initialize(self, operators, params, do_sort=True):
        """Resolve operators and parameterization for the given input."""
        for elem in self:
            elem.initialize(operators, params)

        if do_sort:
            mpos_sorted = self.sort_sites()

            for ii, elem in enumerate(mpos_sorted):
                self[ii] = elem

    def sort_sites(self):
        """Sort the sites in each :class:`DenseMPO`."""
        mpos_sorted = DenseMPOList()

        for elem in self:
            elem_sorted = elem.sort_sites()
            mpos_sorted.append(elem_sorted)

        return mpos_sorted
