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
Observable to measure tensor product observables in the system
"""

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

from .tnobase import _TNObsBase

__all__ = ["TNObsTensorProduct"]


class TNObsTensorProduct(_TNObsBase):
    """
    Observables which are tensor product between  one-site or
    two-site operators.

    This observable enables the computation of observables of the following
    form. On a tensor network with :math:`n` sites we can measure :math:`O`
    of the form:

    .. math::
        O = o_0 \\otimes o_2 \\otimes o_3 \\otimes \\dots \\otimes o_{n-1}

    where the different local observables :math:`o_i` might be different
    or even be the identity.

    The output of the measurement will be a dictionary where:

    - The key is the `name` of the observable
    - The value is its expectation value

    An example of such an observable is the Parity of the system. If we
    work on a system of qubits, then to measure the parity we simply have
    to use :math:`o_i=o_j=\\sigma_z \\; \\forall \\; i,j\\in\\{0, n-1\\}`, where
    :math:`\\sigma_z` is the Pauli matrix.

    Parameters
    ----------
    name: str
        Name to identify the observable
    operators: list of str or str
        Idenitifiers/names for the operators to be measured.
        If str the same operator is applied to the whole MPS
    sites: list of int or int
        Indexes to which the operators should be applied, in the same order.
        If int instead it is the size of the chain, and the operator is assumed
        to be applied to each site of the tensor network

    """

    def __init__(self, name, operators, sites):
        if isinstance(operators, str) and isinstance(sites, int):
            operators = [operators for _ in range(sites)]
            sites = [[ii] for ii in range(sites)]
        elif isinstance(operators, str):
            raise TypeError("If operators is str sites must be int")
        elif isinstance(sites, int):
            raise TypeError("If sites is int operators must be str")

        self.operators = [operators]
        self.sites = [sites]

        _TNObsBase.__init__(self, name)

    @classmethod
    def empty(cls):
        """
        Documentation see :func:`_TNObsBase.empty`.
        """
        obj = cls(None, None, None)
        obj.name = []
        obj.operators = []
        obj.sites = []

        return obj

    def __len__(self):
        """
        Provide appropriate length method
        """
        return len(self.name)

    def __iadd__(self, other):
        """
        Documentation see :func:`_TNObsBase.__iadd__`.
        """
        if isinstance(other, TNObsTensorProduct):
            self.name += other.name
            self.operators += other.operators
            self.sites += other.sites
        else:
            raise QTeaLeavesError("__iadd__ not defined for this type.")

        return self

    def read(self, fh, **kwargs):
        """
        Read the measurements of the correlation observable from fortran.

        Parameters
        ----------

        fh : filehandle
            Read the information about the measurements from this filehandle.
        """
        fh.readline()  # separator
        is_meas = fh.readline().replace("\n", "").replace(" ", "")
        self.is_measured = is_meas == "T"

        for name in self.name:
            if self.is_measured:
                value = fh.readline().replace("\n", "").replace(" ", "")
                value = np.array(value.split(","), dtype=float)

                yield name, value[0] + 1j * value[1]
            else:
                yield name, None

    def write(self, fh, **kwargs):
        """
        Write fortran compatible definition of observable to file.

        Parameters
        ----------

        fh : filehandle
                Write the information about the measurements to this filehandle.
        """
        operator_map = kwargs.get("operator_map")

        str_buffer = "------------------- tnobstensprod\n"

        str_buffer += "%d\n" % (len(self))

        for ii in range(len(self)):
            # Write observable name and number of operators
            str_buffer += "%d %s \n" % (len(self.operators[ii]), self.name[ii])
            for jj in range(len(self.operators[ii])):
                # Write number of sites on which the operator is defined
                str_buffer += "%d \n" % (len(self.sites[ii][jj]))
                # Write operator ID and sites
                sites = np.array(self.sites[ii][jj]) + 1
                sites_string = " ".join(sites.astype(str))
                str_buffer += "%d " % (operator_map[self.operators[ii][jj]])
                str_buffer += sites_string + " \n"
            str_buffer += ".true.\n"

        fh.write(str_buffer)

        return

    def write_results(self, fh, is_measured, **kwargs):
        """
        Write the results mocking a fortran output

        Parameters
        ----------
        fh : filehandle
            Write the information about the measurements to this filehandle.
        """
        # Write separator first
        fh.write("-" * 20 + "tnobstensprod\n")
        # Assignment for the linter
        _ = fh.write("T \n") if is_measured else fh.write("F \n")

        for name_ii in self.name:
            fh.write(f"{np.real(self.results_buffer[name_ii])}, ")
            fh.write(f"{np.imag(self.results_buffer[name_ii])} \n")
