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
The module contains solvers for the Krylov eigensolver as an API (multiplication
matrix-vector are passed as function, vector class needs only a few attributes).

**Attributes needed for vector class**

* `norm`
* `dot` for inner product between two vectors.
* `add_update(self, other, factor_self, factor_other)
* `__itruediv__`
* `__imul__`
* `abs`
* `dtype_eps`
* `shape`
"""

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments

import logging

import numpy as np

from qtealeaves.tooling import QTeaLeavesError

__all__ = ["EigenSolverH"]

logger = logging.getLogger(__name__)


class EigenSolverH:
    """
    Eigensolver for hermitian matrix.

    **Arguments**

    vec0 : vector to apply exponential matrix to / initial guess

    matvec_func : callable, multiplies matrix in exponential with vector.

    args_func : list, arguments for matvec_func

    kwargs_func : dict, keyword arguments for matvec_func

    injected_funcs : `None` or dictionary.
        If data types are missing necessary attributes, e.g., `real`, we
        allow to inject them. Right now only for `real`. Key must be
        the attribute name to be replaces. Callable takes one argument
        being the obj.
    """

    def __init__(
        self,
        vec0,
        matvec_func,
        conv_params,
        args_func=None,
        kwargs_func=None,
        injected_funcs=None,
    ):
        self.vec = vec0
        self.conv_params = conv_params
        self.func = matvec_func
        self.args = [] if args_func is None else args_func
        self.kwargs = {} if kwargs_func is None else kwargs_func

        self.dim_problem = np.prod(vec0.shape)
        self.nn_max = min(self.dim_problem, conv_params.arnoldi_maxiter)

        tolerance = conv_params.sim_params["arnoldi_tolerance"]
        if tolerance is None:
            tolerance = conv_params.sim_params["arnoldi_min_tolerance"]
        self.tolerance = tolerance
        self.basis = []

        if injected_funcs is None:
            self.injected_funcs = {}
        else:
            self.injected_funcs = injected_funcs

        self.dtype_eps = vec0.dtype_eps
        if (self.tolerance < vec0.dtype_eps) and (self.tolerance > 0.0):
            # If tolerance == 0, then enforce max iterations ...
            logger.warning(
                "Non-zero Lanczos tolerance is smaller than machine precision. Resetting."
            )
            self.tolerance = self.dtype_eps

        self.init_basis()

    def init_basis(self):
        """Initialize the basis and create diagonal / subdiagonal entries."""

        self.diag = np.zeros(self.nn_max + 1)
        self.sdiag = np.zeros(self.nn_max)
        self.sdiag_0 = self.vec.norm_sqrt()

        eps = abs(1 - self.sdiag_0)
        if (eps > 1e3 * self.dtype_eps) and (not self.conv_params.data_type_switch):
            raise QTeaLeavesError(
                f"Expecting normalized vector, but {eps} for tolerance {self.tolerance}."
            )
        if eps > 10 * self.dtype_eps:
            logger.warning(
                "Expecting normalized vector, but %2.14f for tolerance %2.14f.",
                eps,
                self.tolerance,
            )

        self.basis.append(self.vec.copy())

    def real(self, obj):
        """Supporting taking the real part of complex number via attribute or injected function."""
        if "real" in self.injected_funcs:
            return self.injected_funcs["real"](obj)

        return obj.real

    def abs(self, obj):
        """Supporting taking the absolute value of any number via attribute or injected function."""
        if "abs" in self.injected_funcs:
            return self.injected_funcs["abs"](obj)

        return obj.abs()

    def solve(self):
        """Solver step executing iterations until new vector is returned."""

        for ii in range(self.nn_max):
            # Matrix-vector multiplication interface
            self.vec = self.func(self.vec, *self.args, **self.kwargs)

            overlap = self.vec.dot(self.basis[ii])
            self.vec.add_update(self.basis[ii], factor_other=-overlap)

            if ii > 0:
                self.vec.add_update(
                    self.basis[ii - 1], factor_other=-self.sdiag[ii - 1]
                )

            # Beyond numpy/cupy, problem started (range can be set with tensor of len 1,
            # single integer cannot be set with tensor of len 1 for jax/tensorflow?)
            # Moreover, overlap can be on device, not host.
            if self.vec.linear_algebra_library == "torch":
                self.diag[ii] = self.real(overlap)
            else:
                self.diag[ii : ii + 1] = self.vec.get_of(self.real(overlap))
            self.sdiag[ii] = self.vec.norm_sqrt()

            mat = np.diag(self.diag[: ii + 1])
            for jj in range(ii):
                mat[jj, jj + 1] = self.sdiag[jj]
                mat[jj + 1, jj] = self.sdiag[jj]

            evals, evecs = np.linalg.eigh(mat)

            # Check on exit criteria
            precision_fom = evecs[ii, 0] * self.sdiag[ii]
            if abs(precision_fom) < self.tolerance:
                logger.info(
                    "EigenSolverH converged in %d steps with %f", ii + 1, precision_fom
                )
                break

            if ii + 1 == self.nn_max:
                logger.warning(
                    "EigenSolverH stopped at max_iter with %2.14f (target %2.14f)",
                    precision_fom,
                    self.tolerance,
                )
                break

            # Re-orthogonalize
            for ket in self.basis:
                overlap = ket.dot(self.vec)
                if self.abs(overlap) > min(self.dtype_eps, self.tolerance):
                    self.vec.add_update(ket, factor_other=-overlap)

            self.sdiag[ii] = self.vec.norm_sqrt()
            self.vec /= self.sdiag[ii]
            self.basis.append(self.vec.copy())

        # Build solution (expecting list of eigenvalues even if size-one)
        val = [evals[0]]
        vec = self.basis[0] * evecs[0, 0]

        for jj in range(1, ii + 1):
            vec.add_update(self.basis[jj], factor_other=evecs[jj, 0])

        return val, vec
