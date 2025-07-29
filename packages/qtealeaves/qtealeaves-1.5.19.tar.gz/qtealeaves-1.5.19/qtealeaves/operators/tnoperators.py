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
Generic base class for operators.
"""

# pylint: disable=too-many-locals

import os

# pylint: disable-next=no-name-in-module
import os.path
from collections import OrderedDict
from copy import deepcopy

import numpy as np

from qtealeaves.tooling import QTeaLeavesError, StrBuffer, write_symtensor, write_tensor
from qtealeaves.tooling.parameterized import _ParameterizedClass

__all__ = ["TNOperators"]


class TNOperators(_ParameterizedClass):
    """
    Generic class to write operators. This class contains no pre-defined
    operators. It allows you to start from scratch if no other operator
    class fulfills your needs.

    **Arguments**

    set_names : list of str, optional
        Name of the operators sets.
        Default to `default`

    mapping_func : callable (or `None`), optional
        Mapping the site index to an operator. Arguments
        `site_idx` must be accepted.
        Default to `None` (default mapping to only operator set)
    """

    def __init__(self, set_names="default", mapping_func=None):
        if isinstance(set_names, str):
            set_names = [set_names]

        self._ops_dicts = {}
        for name in set_names:
            if not isinstance(name, str):
                raise TypeError(f"Set names must be str, but got `{type(name)}`.")
            self._ops_dicts[name] = OrderedDict()

        # Trivial mapping as None resolved in property
        self._mapping_func = None
        if mapping_func is not None:
            self._mapping_func = mapping_func

    @property
    def one_unique(self):
        """Flag if only one operators set exists (True) or multiple (False)."""
        return len(self) == 1

    @property
    def mapping_func(self):
        """Mapping function for site to operator set name."""
        if self._mapping_func is None:
            default_key = self.set_names[0]

            # pylint: disable-next=unused-argument
            def default_mapping(site_idx, default_key=default_key):
                return default_key

            return default_mapping

        return self._mapping_func

    @property
    def set_names(self):
        """Return operator set names as list of strings."""
        return list(self._ops_dicts.keys())

    def __len__(self):
        """Lenght of TNOperators defined as number of operator sets."""
        return len(self._ops_dicts)

    def __contains__(self, key):
        """Check if a key is inside the operators."""
        key_a, key_b = self._parse_key(key)
        if key_a not in self._ops_dicts:
            return False

        return key_b in self._ops_dicts[key_a]

    def __delitem__(self, key):
        """Delete entry in operators."""
        key_a, key_b = self._parse_key(key)
        del self._ops_dicts[key_a][key_b]

    def __getitem__(self, key):
        """Extract entry by key."""
        key_a, key_b = self._parse_key(key)
        return self._ops_dicts[key_a][key_b]

    def __setitem__(self, key, value):
        """Set entry by key."""
        key_a, key_b = self._parse_key(key, callee_set=True)
        self._ops_dicts[key_a][key_b] = value

    def __iter__(self):
        """Iterate through all keys (of all operators sets)."""
        for key, value in self._ops_dicts.items():
            for subkey in value:
                yield (key, subkey)

    def items(self):
        """Iterate throught all (key, value) pairs of all operators sets."""
        for key, value in self._ops_dicts.items():
            for subkey, subvalue in value.items():
                yield (key, subkey), subvalue

    def _parse_key(self, key, callee_set=False):
        """
        Parse the key and split into operator set key and operator name key.

        **Arguments**

        key : tuple (or str)
            Key as tuple of length two (or operator name).

        callee_set : bool, optional
            Indicate if callee is `__setitem__`.
            Default to `False`.
        """
        if isinstance(key, str) and self.one_unique:
            default_key = self.set_names[0]
            return default_key, key

        if isinstance(key, str):
            raise ValueError("Operators are not unique, indicate index.")

        if len(key) != 2:
            raise ValueError("Operators are not unique, indicate index.")

        if isinstance(key[0], str):
            # str for operator set name
            key_0 = key[0]
        elif isinstance(key[0], (int, np.int64)) and callee_set:
            raise ValueError("Cannot set entry via integer entry (per site).")
        elif isinstance(key[0], (int, np.int64)):
            # int for site, use mapping
            # pylint: disable-next=not-callable
            key_0 = self.mapping_func(key[0])
        else:
            raise ValueError(f"First entry must be set name or int, but `{key[0]}`.")

        if not isinstance(key[1], str):
            raise ValueError(
                f"Second entry must specify operator name, but `{key[1]}`."
            )

        return key_0, key[1]

    def get_operator(self, site_idx_1d, operator_name, params):
        """
        Provide a method to return any operator, either defined via
        a callable or directly as a matrix.

        **Arguments**

        site_idx_1d : int, str
            If int, site where we need the operator. Mapping will evaluate what
            to return.
            If str, name of operator set.

        operator_name : str
            Tag/identifier of the operator.

        params : dict
            Simulation parameters as a dictionary; dict is passed
            to callable.
        """
        if isinstance(site_idx_1d, (int, np.int64)):
            # pylint: disable-next=not-callable
            key_0 = self.mapping_func(site_idx_1d)
        else:
            key_0 = site_idx_1d
        op_mat = self.eval_numeric_param(self[(key_0, operator_name)], params)
        return op_mat

    def get_local_links(self, num_sites, params):
        """
        Extract the local links from the operators.

        **Arguments**

        num_sites : integer
            Number of sites.

        params : dict
            Dictionary with parameterization of the simulation.
        """
        local_links = []
        for ii in range(num_sites):
            eye = self.get_operator(ii, "id", params)

            if hasattr(eye, "links"):
                local_links.append(eye.links[1])
            else:
                # When constructing H, we call this with numpy tensors
                local_links.append(eye.shape[0])

        return local_links

    def transform(self, transformation, **kwargs):
        """
        Generate a new :class:`TNOperators` by transforming the
        current instance.

        **Arguments**

        transformation : callable
            Accepting key and value as arguments plus potential
            keyword arguments.

        **kwargs : key-word arguments
            Will be passed to `transformation`
        """
        new_ops = TNOperators(set_names=self.set_names, mapping_func=self.mapping_func)
        for key, value in self.items():
            new_ops[key] = transformation(key, value, **kwargs)

        return new_ops

    # --------------------------------------------------------------------------
    #                     Fortran support / Fortran i/o
    # --------------------------------------------------------------------------

    def keys(self):
        """Return the keys of the underlying dictionary."""
        if not self.one_unique:
            raise QTeaLeavesError("Only works for one unique operator set.")
        default_key = self.set_names[0]
        return self._ops_dicts[default_key].keys()

    def write_operator(
        self, folder_dst, operator_name, params, tensor_backend, **kwargs
    ):
        """
        Write operator to file. Format depends on the tensor backend.

        **Arguments**

        folder_dst : str or filehandle
            If filehandle, write there. If string, it defines the folder.

        operator_name : str
            Name of the operator.

        params : dictionary
            Contains the simulation parameters.

        kwargs : passed to write_symtensor

        """
        if not self.one_unique:
            raise QTeaLeavesError("Fortran does not support different Hilbert spaces.")

        default_key, operator_name = self._parse_key(operator_name)

        if operator_name not in self._ops_dicts[default_key]:
            raise QTeaLeavesError("Operator `%s` not defined." % (operator_name))

        if tensor_backend == 1:
            return self.write_operator_abeliansym(
                folder_dst, operator_name, params, **kwargs
            )

        if tensor_backend == 2:
            self.write_operator_dense(folder_dst, operator_name, params)
            return None

        raise QTeaLeavesError("Unknown tensor backend %d." % (tensor_backend))

    def write_operator_dense(self, folder_dst, operator_name, params):
        """
        Write dense tensor based on the numpy array.

        **Arguments**

        see write_operator
        """
        # There is a check on entry that operators are equal for all sites
        # Choose any valid site here ...
        site_idx = 0

        if hasattr(folder_dst, "write"):
            # filehandle
            full_filename = folder_dst
        else:
            # pylint: disable-next=no-member
            full_filename = os.path.join(folder_dst, operator_name + ".dat")

        op_mat = self.get_operator(site_idx, operator_name, params)

        write_tensor(op_mat, full_filename)

        return operator_name + ".dat"

    def write_operator_abeliansym(self, folder_dst, operator_name, params, **kwargs):
        """
        Write an abelian symmetry tensor based on the parameter dictionary,
        which has to provide the definitions of the symmetry, i.e., generators
        and symmetry type.

        **Arguments**

        see write_operator
        """
        # There is a check on entry that operators are equal for all sites
        # Choose any valid site here ...
        site_idx = 0

        if hasattr(folder_dst, "write"):
            # filehandle
            dst = folder_dst
        else:
            # pylint: disable-next=no-member
            dst = os.path.join(folder_dst, operator_name + ".dat")

        op_mat = self.get_operator(site_idx, operator_name, params)

        sector = params.get("SymmetrySectors", None)
        generators = params.get("SymmetryGenerators", None)
        gen_types = params.get("SymmetryTypes", None)

        if (sector is None) and (generators is None) and (gen_types is None):
            sector = []
            generators = [0 * op_mat]
            gen_types = "U"
        elif (
            (sector is not None)
            and (generators is not None)
            and (gen_types is not None)
        ):
            length_sectors = len(sector)
            length_generators = len(generators)
            length_symmetry_types = len(gen_types)

            if (length_sectors != length_generators) or (
                length_generators != length_symmetry_types
            ):
                raise QTeaLeavesError(
                    "Symmetry specifications must be of equal length."
                )
        else:
            raise NotImplementedError("Incomplete definition of symmetry.")

        generator_matrices = []
        for elem in generators:
            if isinstance(elem, str):
                op_ii = self.get_operator(site_idx, elem, params)
            elif isinstance(elem, np.ndarray):
                op_ii = elem
            else:
                raise QTeaLeavesError("Unknown data type for generator.")

            generator_matrices.append(op_ii)

        op_info = write_symtensor(op_mat, dst, generator_matrices, gen_types, **kwargs)
        # if(hasattr(folder_dst, 'write')):
        #    tmp = 'check_op_' + operator_name + '.dat'
        #    write_symtensor(op, tmp, generator_matrices, gen_types, **kwargs)

        # Check if argument is set (v3 onwards)
        if kwargs.get("op_info", False):
            return op_info

        # legacy version: return filename (v1 and v2)
        return operator_name + ".dat"

    def write_input(self, folder_name, params, tensor_backend, required_operators):
        """
        Write the input for each operator.

        **Arguments**

        folder_name : str
            Folder name with all the input files; will be extended
            by the subfolder with the operators.

        params : dict
            Dictionary with the simulation parameters.

        tensor_backend : integer
            The integer flag indicates if ``AbelianSymTensors`` or
            ``Tensors`` should be written to the input files.

        required_operators : list
            List of operators keys which is needed for AbelianSymTensors,
            where we distinguish between left, right, center, and independent
            operators.
        """
        folder_operators = "operators"
        # pylint: disable-next=no-member
        full_path = os.path.join(folder_name, folder_operators)
        # pylint: disable-next=no-member
        if not os.path.isdir(full_path):
            # pylint: disable-next=no-member
            os.makedirs(full_path)

        # pylint: disable-next=no-member
        relative_file = os.path.join(full_path, "operators.dat")
        buffer_str = StrBuffer()

        operator_id_mapping = {}

        ii = 0
        for operator_ii in self.keys():
            ii += 1
            op_info = self.write_operator(
                buffer_str, operator_ii, params, tensor_backend, op_info=True
            )

            operator_id_mapping[(operator_ii, op_info)] = ii

        if tensor_backend == 1:
            # Need to provide all operators
            required_operators_ = deepcopy(required_operators)
            # pylint: disable-next=unnecessary-lambda
            required_operators_.sort(key=lambda xx: str(xx))

            for elem in operator_id_mapping:
                if elem not in required_operators_:
                    continue

                required_operators_.remove(elem)

            for elem in required_operators_:
                ii += 1
                op_info = self.write_operator(
                    buffer_str, elem[0], params, tensor_backend, add_links=elem[1]
                )

                operator_id_mapping[elem] = ii

            # Aposterio length because added operator are written
            nn = len(operator_id_mapping)
        else:
            # Provide keys for 'l', 'r' (tensor unchanged without symmetry)

            # Apriori length because operators are not written
            nn = len(operator_id_mapping)

            for key in list(operator_id_mapping.keys()):
                idx = operator_id_mapping[key]

                operator_id_mapping[(key[0], "l")] = idx
                operator_id_mapping[(key[0], "r")] = idx

        with open(relative_file, "w+") as fh:
            fh.write(str(nn) + "\n")
            fh.write(buffer_str())

        return relative_file, operator_id_mapping
