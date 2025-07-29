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
The module for the fortran interfaces takes care of writing nml files
and tensors in the correct.
"""

from ast import literal_eval
from collections import OrderedDict

import numpy as np

from .qtealeavesexceptions import QTeaLeavesError

__all__ = ["write_nml", "write_tensor", "write_symtensor", "read_tensor", "StrBuffer"]


def write_nml(namelist_name, namelist_dict, namelist_file):
    """
    Write Fortran namelist from an ordered dictionary.

    **Parameters**

    """
    if not isinstance(namelist_dict, OrderedDict):
        raise QTeaLeavesError("Please pass ordered dict.")

    if hasattr(namelist_file, "write"):
        fh = namelist_file
    else:
        # pylint: disable-next=consider-using-with
        fh = open(namelist_file, "w+")

    fh.write("&%s \n" % (namelist_name))

    for key, value in namelist_dict.items():
        if not isinstance(key, str):
            raise QTeaLeavesError("Key is no string!")

        if isinstance(value, str):
            fh.write(key + "='" + str(value) + "' \n")
        elif isinstance(value, bool):
            bool_str = ".true." if (value) else ".false."
            fh.write(key + "=" + bool_str + " \n")
        elif isinstance(value, int):
            fh.write(key + "=" + str(value) + " \n")
        elif isinstance(value, float):
            fh.write(key + "=" + str(value) + " \n")
        else:
            raise QTeaLeavesError(
                "Unknown type "
                + str(type(value))
                + " for "
                + key
                + ". Please implement if compatible with f90."
            )

    # Terminator for nml file
    fh.write("/ \n")

    if not hasattr(namelist_file, "write"):
        fh.close()

    return


# pylint: disable-next=too-many-statements, too-many-branches, too-many-locals, too-many-arguments
def write_symtensor(
    tensor, dest, generators, gen_type, add_links=None, cmplx=True, **kwargs
):
    """
    Write a tensor stored in a numpy matrix to a file.

    **Arguments**

    tensor : np.ndarray of rank 2

    dest : str, or filehandle

    generators : list of np.ndarray of rank 2

    gen_type : str

    add_links : TBA

    cmplx : bool, optional

    **Details**

    There are multiple options to write a AbelianSymTensor. We
    list one after another.

    Coupling sectors
    ----------------

    [AbelianSymCombinedGroup]
      number of symmetries, int
      [AbelianSymGroup], dimension(#sym)
        type_id, char
        [if U1]
          [nothing]
        [if Zn]
          order, int
    [back to the AbelianSymTensor]
    number of links : int
    are links outgoing : logical(number_of_links)
    [AbelianSymLink] in for loop
      [skip symnmetry]
      [irrepListing]
        [skip format]
        [else case (optimized, format=L)]
        [if do_read_sym_indices_ = false]
          number of symmetry indices, int
          assume_sym_indices_full , logical
          [if not full] sym_indices_, integer(#sym_indices)
        number_of_sectors, int --> irreps(#sym_ind, #sectors), total number
             of sectors even if here not active
        irreps, integer(:, :)
        [if do_read_has_deg_ = false] logical
        [if do_read_deg_ = true] degeneracies, integer(#sectors)
    format, char(3) ('s' for coupling sectors in the example)
    number_elements, int
    [sectors] in for loop
      coupling_sectors, int(#links); deg_indices, int(#links); value, DTYPE

    Coupling irreps
    ---------------

    [AbelianSymCombinedGroup]
    ...
    [AbelianSymTensor]
    number of links : int
    are links outgoing : logical(number_of_links)
    [AbelianSymLink] in for loop
    ...
    format, char(3) ('S' for coupling irreps in the example)
    number_elements, int
    [sectors] in for loop
      coupling_irreps, int(#sym, #links); deg_indices, int(#links); value, DTYPE


    **Examples**

    1 = number of symmetries
    U = U(1) symmetry
    2 = number of links
    T F = are_links_outgoing
    2 = number of sectors?
    0 = irreps(:, 1)
    1 = irreps(:, 2)
    126 141 = degeneracies ?
    2
    0
    1
    126 141
    S = format irreps
    131 = number of elements specified as irreps
    0 0, 1 8, (-1.0, 0.0) : 0, 0 = coupling_irreps, 1,8 = deg_indices, (...) = value
    ...


    1 = number of symmetries
    U = U(1) symmetry
    3 = number of links
    T F F = are_links_outgoing
    [1st link]
      2 number of sectors
      0 irreps(:, 1)
      1 irreps(:, 2)
      126 141
    [2nd link]
      2
      0
      1
      126 141
    [3rd link]
      1 number of sectors
      1 irreps(:, 1)
      1 degeneracies
    S = format, file provides irreps
    96 = number of elements specified as irreps
    1 0 1, 1 1 1, (1.0, 0.0)
    1 0 1, 2 2 1, (-1.0, 0.0)
    ...


    """
    # Run check if generator is diagonal
    for elem in generators:
        tmp = elem - np.diag(np.diag(elem))
        if np.sum(np.abs(tmp)) > 1e-14:
            raise QTeaLeavesError("Generator not diagonal.")

    # Run check that there are only integer elements
    for elem in generators:
        if np.sum(np.abs(np.imag(np.diag(elem)))) > 1e-14:
            raise QTeaLeavesError("Diagonal elements cannot be complex.")

        tmp = elem - np.array(np.diag(np.real(np.diag(elem))), dtype=int)
        if np.sum(np.abs(tmp)) > 1e-14:
            raise QTeaLeavesError("Diagonal elements must be integers in generator.")

    # Support only matrices for now (additional links can be added)
    if len(tensor.shape) != 2:
        raise QTeaLeavesError("Please pass matrix to write AbelianSymTensor.")

    # Catch case with all zeros in operator, write the cheapest tensor
    # with diagonal element tensor[0, 0]
    is_zero_matrix = np.max(np.abs(tensor)) < 1e-14

    # Retrieve matrix dimension
    dim = generators[0].shape[0]

    # mask for different symmetries
    mask_u1 = np.zeros(len(gen_type), dtype=bool)
    for ii, elem in enumerate(gen_type):
        mask_u1[ii] = elem == "U"

    mask_zn = np.logical_not(mask_u1)

    vals_zn = []
    if np.any(mask_zn):
        for ii, elem in enumerate(gen_type):
            if not mask_zn[ii]:
                continue

            vals_zn.append(int(elem.replace("Z", "")))

    vals_zn = np.array(vals_zn, dtype=int)

    # Generate maps: index <--> quantum numbers
    qnum_2_ind = OrderedDict()
    ind_2_qnum = []

    # pylint: disable-next=consider-using-generator
    for ii in range(dim):
        # pylint: disable-next=consider-using-generator
        key = tuple([int(np.real(elem[ii, ii])) for elem in generators])
        ind_2_qnum.append(key)

        if key in qnum_2_ind:
            tmp = qnum_2_ind[key]
            tmp.append(ii)
            qnum_2_ind[key] = tmp
        else:
            qnum_2_ind[key] = [ii]

    qnum_keys = list(qnum_2_ind.keys())

    # Scan elements
    active_1 = np.zeros(len(qnum_keys))
    active_2 = np.zeros(len(qnum_keys))

    sparse_entries = []

    # Keep track of difference in quantum numbers
    qnum_remainder = None

    for ii in range(tensor.shape[0]):
        for jj in range(tensor.shape[1]):
            if np.abs(tensor[ii, jj]) < 1e-14:
                if not is_zero_matrix:
                    continue

                if (ii != 0) or (jj != 0):
                    # For zero matrix, do not skip element Mat[0, 0]
                    continue

            qnum_1 = ind_2_qnum[ii]
            qnum_2 = ind_2_qnum[jj]

            diff = np.array(qnum_1) - np.array(qnum_2)
            if np.any(mask_zn):
                diff[mask_zn] = diff[mask_zn] % vals_zn

            if qnum_remainder is None:
                qnum_remainder = diff

            if np.any(np.abs(qnum_remainder - diff) > 1e-14):
                # Check theory if we can have multiple difference, but for
                # now forbid
                raise QTeaLeavesError(
                    "No support for 3rd link with multiple sectors "
                    + "(if even allowed at all)."
                )

            # Keep track how many are used
            active_1[qnum_keys.index(qnum_1)] = 1
            active_2[qnum_keys.index(qnum_2)] = 1

            # Degeneracy index: convert to fortran style with +1
            deg_ind_1 = qnum_2_ind[qnum_1].index(ii) + 1
            deg_ind_2 = qnum_2_ind[qnum_2].index(jj) + 1

            sparse_entries.append(
                ([qnum_1, qnum_2], [deg_ind_1, deg_ind_2], tensor[ii, jj])
            )

    if (add_links is None) and (np.sum(np.abs(qnum_remainder)) > 0):
        # print('Warning: we are adding a third link to the tensor '
        #      + '(2-body interaction??).')
        add_links = "3"

    if (add_links is None) and (np.sum(np.abs(qnum_remainder)) > 0):
        raise QTeaLeavesError("We recommend adding a third link. Check model etc.")

    # Combine those for later access in loop
    active = [active_1, active_2]

    buff = ""

    # Number of symmetries and symmetry type
    buff += "%d\n" % (len(generators))

    for elem in gen_type:
        if elem.startswith("U"):
            buff += "U\n"
        elif elem.startswith("Z"):
            buff += "Z\n"

            # Ensure remaining entry is integer
            buff += "%d\n" % (int(elem.replace("Z", "")))
        else:
            raise QTeaLeavesError("Unknown generator type %s." % (elem))

    # Describe links
    if add_links is None:
        out = ["F", "T"]
    elif add_links == "l":
        out = ["F", "T", "F"]
        qnum_3 = [
            int(-ii) if (mask_u1[jj]) else abs(int(ii))
            for jj, ii in enumerate(qnum_remainder)
        ]
        qnum_3_str = " ".join(map(str, qnum_3))
    elif add_links == "r":
        out = ["F", "T", "T"]
        qnum_3 = [
            int(ii) if (mask_u1[jj]) else abs(int(ii))
            for jj, ii in enumerate(qnum_remainder)
        ]
        qnum_3_str = " ".join(map(str, qnum_3))
    elif add_links in ["lr", "4"]:
        raise NotImplementedError("add_links `%s` not implemented." % (add_links))
    elif add_links == "3":
        # Negative coupling sectors are allowed ...
        # raise QTeaLeavesError('Be explicit ...')

        # Choose based on first coupling sector (enforcing non-negative)
        if qnum_remainder[0] > 0:
            out = ["F", "T", "F"]
            qnum_3 = [
                int(-ii) if (mask_u1[jj]) else abs(int(ii))
                for jj, ii in enumerate(qnum_remainder)
            ]
        else:
            out = ["F", "T", "T"]
            qnum_3 = [
                int(ii) if (mask_u1[jj]) else abs(int(ii))
                for jj, ii in enumerate(qnum_remainder)
            ]

        qnum_3_str = " ".join(map(str, qnum_3))
    else:
        raise QTeaLeavesError("Unknown add_links value.")

    # number_of_links, are_links_outgoing
    buff += "%d\n" % len(out)
    buff += " ".join(out) + "\n"

    # Reset, apparently we write all of them here (no, but it simplifies things
    # for the moment and should not break anything)
    active_1 = np.ones(len(qnum_keys))
    active_2 = np.ones(len(qnum_keys))
    active = [active_1, active_2]

    # Loop over AbelianSymLink (cannot do range(len(out)) anymore)
    for ii in range(2):
        # number_of_sectors
        buff += "%d\n" % (int(np.sum(active[ii])))

        # The irreps have to be sorted ascending in column-major indexing
        degeneracy = []
        irreps = []

        # Collect them
        for jj in range(len(active[ii])):
            tmp = qnum_keys[jj]
            irreps.append(tmp)

        # Sort them
        ind_sorted = argsort_irreps(irreps)

        for kk in range(len(active[ii])):
            jj = ind_sorted[kk]
            # if(active[ii][jj] == 0): continue

            # Get keys
            tmp = qnum_keys[jj]
            buff += " ".join(map(str, tmp)) + "\n"

            degeneracy.append(str(len(qnum_2_ind[tmp])))

        buff += " ".join(degeneracy) + "\n"

    # Additional AbelianSymLink added (cheat a bit for the easy case)
    if add_links in ["3", "r", "l"]:
        buff += "1\n"

        degeneracy = ["1"]
        # pylint: disable-next=possibly-used-before-assignment
        buff += qnum_3_str + "\n"
        buff += " ".join(degeneracy) + "\n"

    # Format of sparse entries
    buff += "S\n"
    buff += "%d\n" % (len(sparse_entries))

    for elem in sparse_entries:
        # Coupling_irreps
        qnum_1 = " ".join(map(str, elem[0][0]))
        qnum_2 = " ".join(map(str, elem[0][1]))

        if add_links in ["3", "l", "r"]:
            qnum = " ".join([qnum_1, qnum_2, qnum_3_str])
        else:
            qnum = " ".join([qnum_1, qnum_2])

        # deg_indices
        deg_ind = " ".join(map(str, elem[1]))
        if add_links in ["3", "l", "r"]:
            deg_ind += " 1"

        # value of sparse entry
        if cmplx:
            val_str = "(%30.15E, %30.15E)" % (np.real(elem[2]), np.imag(elem[2]))
        else:
            val_str = "%30.15E" % (np.real(elem[2]))

        buff += ", ".join([qnum, deg_ind, val_str]) + "\n"

    if isinstance(dest, str):
        # pylint: disable-next=consider-using-with
        fh = open(dest, "w+")
        fh.write(buff)
        fh.close()
    elif hasattr(dest, "write"):
        fh = dest
        fh.write(buff)

    return add_links


def argsort_irreps(irreps):
    """
    Irreps have to be sorted ascending in column-major indices. This function
    will return the argsort array for a list of irreps.

    We check for multiple entries of the same irrep. Should not occur,
    but who knowns.
    """
    dim0 = len(irreps)
    dim1 = len(irreps[0])

    irreps_mat = np.zeros((dim0, dim1))
    for ii, elem in enumerate(irreps):
        irreps_mat[ii, :] = np.array(elem)

    irreps_dim = np.zeros(dim1)
    for jj in range(dim1):
        # Shift to zero if there is any offset
        minval = np.min(irreps_mat[:, jj])
        irreps_mat[:, jj] = irreps_mat[:, jj] - minval

        # Find dimension (offset due to start indexing at zero)
        irreps_dim[jj] = np.max(irreps_mat[:, jj]) + 1

    # Cumulative product
    irreps_dim[1:] = np.cumprod(irreps_dim)[:-1]
    irreps_dim[0] = 1

    # Value to be sorted
    irreps_val = np.zeros(dim0)
    for ii in range(dim0):
        irreps_val[ii] = np.sum(irreps_dim * irreps_mat[ii, :])

    if len(set(list(irreps_val))) != dim0:
        raise QTeaLeavesError("Double entry in irreps.")

    return np.argsort(irreps_val)


def write_tensor(tensor, dest, cmplx=True, **kwargs):
    """
    Write a tensor stored in a numpy matrix to a file. Conversion
    to column major is taken care of here.

    **Arguments**

    tensor : np.ndarray
        Tensor to be written to the file.

    dest : str, or filehandle
        If string, file will be created or overwritten. If filehandle,
        then data will be written there.
    """
    if isinstance(dest, str):
        # pylint: disable-next=consider-using-with
        fh = open(dest, "w+")
    elif hasattr(dest, "write"):
        fh = dest
    else:
        raise ValueError(
            f"Argument `dest` {dest} not recognized to open file-like object."
        )

    # Number of links
    fh.write("%d\n" % (len(tensor.shape)))

    # Dimensions of links
    dimensions_links = " ".join(list(map(str, tensor.shape)))
    fh.write(dimensions_links + "\n")

    # Now we need to transpose
    tensor_colmajor = np.ravel(tensor, order="F")

    for elem in tensor_colmajor.flat:  # .flat precaution for numpy.matrix behaviour
        if cmplx:
            fh.write("(%30.15E, %30.15E)\n" % (np.real(elem), np.imag(elem)))
        else:
            fh.write("%30.15E\n" % (np.real(elem)))
            imag_part = np.imag(elem)
            if np.abs(imag_part) > 1e-14:
                raise QTeaLeavesError(
                    "Writing complex valued tensor as real valued tensor."
                )

    if isinstance(dest, str):
        fh.close()

    return


def read_tensor(file, cmplx=True, order="F"):
    """
    Read a tensor written in a file from fortran and store it in a numpy matrix. Conversion
    to row major is taken care of here if order='F'.
    author: mb

    Parameters
    ----------
    file: str, or filehandle
        If string, file will be opened. If filehandle, then data will be read from there.

    cmplx: bool, optional
        If True the tensor is complex. Otherwise is real. Default to True.

    order: str, optional
        If 'F' the tensor is transformed from column-major to row-major, if 'C'
        it is left as read.
    """
    if order not in ["F", "C"]:
        raise ValueError("Only fortran('F') or C 'C' order are available.")
    if isinstance(file, str):
        # pylint: disable-next=consider-using-with
        fh = open(file, "r")
    elif hasattr(file, "read"):
        fh = file
    else:
        raise TypeError(
            f"Input file has to be either string or filehandle, not {type(file)}."
        )

    # Number of links
    _ = int(fh.readline())
    # Dimensions of links
    dl = fh.readline().replace("\n", "")
    dl = dl.split(" ")
    dl = np.array(dl, dtype=int)

    # Define numpy array
    if cmplx:
        tens = np.zeros(np.prod(dl), dtype=np.complex128)
    else:
        tens = np.zeros(np.prod(dl))
    # Read array
    for ii in range(np.prod(dl)):
        if cmplx:
            elem = literal_eval(fh.readline().strip())
            tens[ii] = complex(elem[0], elem[1])
        else:
            elem = fh.readline()
            tens[ii] = np.double(elem[0])

    tensor_rowmajor = tens.reshape(dl, order=order)

    return tensor_rowmajor


class StrBuffer:
    """
    Class to buffer strings, which is acting like a file
    handle, i.e., it has a write attribute.

    **Variables**

    buffer_str : str
        Will act as a string buffer.
    """

    def __init__(self):
        self.buffer_str = ""

    def write(self, elem):
        """
        Provide write method, which stores information in local buffer.
        """
        self.buffer_str += elem

    def __call__(self):
        """
        Return the current buffer (buffer remains and is not emptied).
        """
        return self.buffer_str
