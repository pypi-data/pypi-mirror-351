"""
Symbolic manipulations for differential geometry operations.

This module provides symbolic tools for computing geometric quantities
such as gradients, divergences, Laplacians, and metric-related operations
in general curvilinear coordinates using SymPy.

These operations are essential in symbolic tensor calculus, particularly
in the context of differential geometry, general relativity, and
coordinate transformations in physics and applied mathematics.

These functions are integrated intoPyMetric for advanced handling
of geometry dependencies, such as computing specialized D- and L-terms.
"""
from typing import Any, List, Optional, Sequence, Union

import numpy as np
import sympy as sp
from sympy.tensor.array import permutedims, tensorcontraction, tensorproduct

from pymetric._typing._generic import BasisAlias

_MetricType = Union[
    sp.ImmutableMatrix,
    sp.MutableMatrix,
    sp.MutableDenseMatrix,
    sp.ImmutableDenseMatrix,
    sp.ImmutableDenseNDimArray,
    sp.MutableDenseNDimArray,
]
_TensorType = Union[
    sp.MutableDenseNDimArray,
    sp.ImmutableDenseNDimArray,
    sp.ImmutableMatrix,
    sp.MutableMatrix,
]


# ====================================== #
# METRIC MANIPULATION FUNCTIONS          #
# ====================================== #
# These functions are used to manipulate the metric
# tensor symbolically to produce various relevant
# outputs.
def invert_metric(metric: _MetricType) -> sp.Matrix:
    r"""
    Compute the inverse of the metric :math:`g_{\mu \nu}`.

    Parameters
    ----------
    metric: :py:class:`~sympy.matrices.dense.dense.MutableDenseMatrix` or :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The metric to invert. If the metric is provided as a full matrix, it will be returned
        as a full matrix. If it is provided as a single array (1D), it is assumed to be a diagonal
        metric and the returned inverse is also diagnonal and returned as an array.


    Returns
    -------
    :py:class:`~sympy.matrices.dense.dense.MutableDenseMatrix` or :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The inverted metric.

    See Also
    --------
    raise_index
    lower_index
    compute_metric_density
    compute_Dterm
    compute_Lterm

    Examples
    --------
    To invert the metric for spherical coordinates, one need only do the following:

    .. code-block:: python

        >>> from pymetric.differential_geometry.symbolic import invert_metric
        >>> import sympy as sp
        >>>
        >>> # Construct the symbols and the metric to
        >>> # pass into the function.
        >>> r,theta,phi = sp.symbols('r,theta,phi')
        >>> metric = sp.Matrix([
        ...     [1,0,0],
        ...     [0,r**2,0],
        ...     [0,0,(r*sp.sin(theta))**2]
        ...     ])
        >>>
        >>> # Now compute the inverse metric.
        >>> print(invert_metric(metric))
        Matrix([[1, 0, 0], [0, r**(-2), 0], [0, 0, 1/(r**2*sin(theta)**2)]])

    We can also invert a metric which is diagonal by simply pushing through
    the diagonal values as an array:

    .. code-block:: python

        >>> from pymetric.differential_geometry.symbolic import invert_metric
        >>> import sympy as sp
        >>>
        >>> # Construct the symbols and the metric to
        >>> # pass into the function.
        >>> r,theta,phi = sp.symbols('r,theta,phi')
        >>> metric = sp.Array([1,r**2,(r*sp.sin(theta))**2])
        >>>
        >>> # Now compute the inverse metric.
        >>> print(invert_metric(metric))
        [1, r**(-2), 1/(r**2*sin(theta)**2)]
    """
    try:
        if len(metric.shape) == 1:
            return sp.Array([1 / _i for _i in metric])
        else:
            return metric.inv()
    except Exception as e:
        raise ValueError(
            f"Failed to invert metric due to an error at the Sympy level: {e}"
        )


def compute_metric_density(metric: _MetricType) -> sp.Basic:
    r"""
    Compute the metric density function :math:`\sqrt{\det(g)}`.

    This function supports two forms of the metric:

    1. A full ``(n, n)`` Sympy Matrix representing a general metric :math:`g_{\mu\nu}`.
    2. A 1D Sympy Array representing the diagonal entries of an orthogonal metric, i.e.
       :math:`g_{\mu\mu}` with no off-diagonal terms.

    Parameters
    ----------
    metric: :py:class:`~sympy.matrices.dense.MutableDenseMatrix` or :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The metric to invert. If the metric is provided as a full matrix, it will be returned
        as a full matrix. If it is provided as a single array (1D), it is assumed to be a diagonal
        metric and the returned inverse is also diagnonal and returned as an array.

    Returns
    -------
    ~sympy.core.basic.Basic
        The metric density, :math:`\sqrt{\det(g)}`.

    See Also
    --------
    invert_metric : Invert a general or orthogonal metric
    compute_Dterm : Compute geometric D-terms
    compute_Lterm : Compute geometric L-terms

    Examples
    --------
    **Full (n x n) metric** for spherical coordinates:

    .. code-block:: python

        >>> import sympy as sp
        >>> from pymetric.differential_geometry.symbolic import compute_metric_density

        >>> r = sp.Symbol('r', positive=True)
        >>> theta = sp.Symbol('theta', positive=True)
        >>> metric_full = sp.Matrix([
        ...     [1, 0, 0],
        ...     [0, r**2, 0],
        ...     [0, 0, (r*sp.sin(theta))**2]
        ... ])
        >>> compute_metric_density(metric_full)
        r**2*Abs(sin(theta))

    **Orthogonal diagonal** metric as a 1D array:

    .. code-block:: python

        >>> import sympy as sp
        >>> from pymetric.differential_geometry.symbolic import compute_metric_density

        >>> r = sp.Symbol('r', positive=True)
        >>> theta = sp.Symbol('theta', positive=True)
        >>> # For the same spherical metric, but only diagonal entries:
        >>> metric_diag = sp.Array([1, r**2, (r*sp.sin(theta))**2])
        >>> compute_metric_density(metric_diag)
        r**2*Abs(sin(theta))
    """
    # Check the dimensionality to decide how to compute det(g).
    shape = metric.shape
    if len(shape) == 1:
        # 1D array -> interpret as diagonal of an orthogonal metric
        # So det(g) = product(diagonal_entries).
        det_g = sp.prod(metric[i] for i in range(shape[0]))
    elif len(shape) == 2:
        # Full (n x n) matrix -> compute determinant directly
        if shape[0] != shape[1]:
            raise ValueError(f"Expected a square matrix for metric, got shape {shape}.")
        det_g = metric.det()
    else:
        raise ValueError(
            f"Expected either a 1D diagonal array or a 2D square matrix for metric, got shape {shape}."
        )

    # Metric density = sqrt(det(g))
    return sp.simplify(sp.sqrt(det_g))


def compute_Dterm(metric_density: sp.Basic, axes: Sequence[sp.Symbol]) -> sp.Array:
    r"""
    Compute the **D-term** components for a particular coordinate system from the
    metric density function.

    In a general, curvilinear coordinate system, the divergence is

    .. math::

        \nabla \cdot {\bf F} = \frac{1}{\rho} \partial_\mu(\rho F^\mu) = D_\mu F^\mu + \partial_\mu F^\mu,

    where

    .. math::

        D_\mu = \frac{1}{\rho} \partial_\mu \rho.

    This function therefore computes each of the :math:`D_\mu` components.

    Parameters
    ----------
    metric_density: :py:class:`~sympy.core.basic.Basic`
        The metric density function :math:`\sqrt{{\rm Det} \; g}`.
    axes: list of :py:class:`~sympy.core.symbol.Symbol`
        The coordinate axes symbols on which to compute the D-terms. There will be ``len(axes)`` resulting
        elements in the output array each corresponding to the :math:`D_{x^i}` component of the D-terms.


    Returns
    -------
    :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The **D-term** components.

    See Also
    --------
    compute_Lterm
    compute_metric_density

    Examples
    --------
    To compute the :math:`D_\mu` components for a spherical coordinate system, we can do the following:

    >>> from pymetric.differential_geometry.symbolic import compute_Dterm
    >>> import sympy as sp
    >>> r,theta,phi = sp.symbols('r,theta,phi')
    >>> metric_density = r**2 * sp.sin(theta)
    >>> print(compute_Dterm(metric_density, axes=[r,theta,phi]))
    [2/r, 1/tan(theta), 0]
    """
    # For each axis, compute the differential of the metric density with the specific axes.
    _derivatives = sp.Array(
        [
            sp.simplify(sp.diff(metric_density, __symb__) / metric_density)
            for __symb__ in axes
        ]
    )
    return _derivatives


def compute_Lterm(
    inverse_metric: _MetricType,
    metric_density: sp.Basic,
    axes: Sequence[sp.Symbol],
) -> sp.Array:
    r"""
    Compute the **L-term** components for a general or orthogonal coordinate system from
    the metric density :math:`\rho` and the inverse metric :math:`g^{\mu\nu}`.

    The Laplacian in curvilinear coordinates can be written as:

    .. math::

        \nabla^2 \phi \;=\;
            \frac{1}{\rho} \,\partial_\mu\!\Bigl(\rho\, g^{\mu\nu}\,\partial_\nu \phi\Bigr)
        \;=\;
            L^\nu \,\partial_\nu \phi \;+\; g^{\mu\nu}\,\partial^2_{\mu\nu} \phi,

    where the **L-term** is:

    .. math::

        L^\nu \;=\; \frac{1}{\rho}\,\partial_\mu\,\bigl(\rho\,g^{\mu\nu}\bigr).

    **Usage**:

    - If ``inverse_metric`` is a full :math:`(n{\times}n)` matrix, the standard formula for
      :math:`\partial_\mu(\rho\,g^{\mu\nu})` is used (summing over :math:`\mu`).
    - If ``inverse_metric`` is a 1D array of length :math:`n`, we assume an **orthogonal** system,
      and use the diagonal simplification:

      .. math::

          L^\nu \;=\;\frac{1}{\rho}\,\partial_\nu\!\Bigl(\rho\,g^{\nu\nu}\Bigr).

    Parameters
    ----------
    inverse_metric : ~sympy.matrices.dense.MutableDenseMatrix or ~sympy.tensor.array.MutableDenseNDimArray
        Either a full inverse metric :math:`g^{\mu\nu}` (shape ``(n, n)``) or a 1D diagonal
        array of shape ``(n,)`` for orthogonal coordinates.
    metric_density : ~sympy.core.basic.Basic
        The metric density :math:`\rho = \sqrt{\det g}`.
    axes : list of ~sympy.core.symbol.Symbol
        The coordinate variables, :math:`x^\mu`.

    Returns
    -------
    ~sympy.tensor.array.MutableDenseNDimArray
        A 1D array of L-term components :math:`L^\nu`.

    See Also
    --------
    compute_Dterm : D-term used in divergence
    compute_metric_density : For obtaining :math:`\rho`

    Examples
    --------
    **1) Full Inverse Metric**

    Spherical coordinates, with
    :math:`g_{\mu\nu} = \mathrm{diag}\bigl(1,\;r^2,\;r^2\,\sin^2\theta\bigr)`:

    .. code-block:: python

        >>> import sympy as sp
        >>> from pymetric.differential_geometry.symbolic import compute_Lterm
        >>> r, theta, phi = sp.symbols('r theta phi')
        >>> rho = r**2*sp.sin(theta)  # metric density
        >>> g_inv = sp.Matrix([       # full inverse metric
        ...     [1,     0,                   0],
        ...     [0, 1/r**2,                0],
        ...     [0,     0, 1/(r**2*sp.sin(theta)**2)]
        ... ])
        >>> L = compute_Lterm(g_inv, rho, [r,theta,phi])
        >>> L
        [2/r, 1/(r**2*tan(theta)), 0]

    **2) Orthogonal (Diagonal) Inverse Metric**

    Provide just the diagonal as a 1D array:

    .. code-block:: python

        >>> g_inv_diag = sp.Array([1, 1/r**2, 1/(r**2*sp.sin(theta)**2)])
        >>> L_orth = compute_Lterm(g_inv_diag, rho, [r,theta,phi])
        >>> L_orth
        [2/r, 1/(r**2*tan(theta)), 0]
    """
    # Validate that we have as many axes as expected.
    ndim = len(axes)

    shape = inverse_metric.shape
    if len(shape) == 2:
        # Full (ndim x ndim) inverse metric
        if shape[0] != ndim or shape[1] != ndim:
            raise ValueError(
                f"Inverse metric shape {shape} does not match {ndim} coordinate axes."
            )
        L_terms = []
        # L^nu = (1 / rho) * sum_{mu}( d/dx^mu [rho * g^{mu,nu}] )
        for nu in range(ndim):
            term_sum = sum(
                sp.diff(metric_density * inverse_metric[mu, nu], axes[mu])
                for mu in range(ndim)
            )
            L_nu = sp.simplify(term_sum / metric_density)
            L_terms.append(L_nu)
        return sp.Array(L_terms)

    elif len(shape) == 1:
        # 1D => orthogonal diagonal metric
        if shape[0] != ndim:
            raise ValueError(
                f"Orthogonal inverse metric length {shape[0]} does not match {ndim} axes."
            )
        L_terms = []
        # L^nu = (1 / rho) * d/dx^nu [rho * g^{nu,nu}]
        for nu in range(ndim):
            expr = metric_density * inverse_metric[nu]
            dexpr = sp.diff(expr, axes[nu])
            L_nu = sp.simplify(dexpr / metric_density)
            L_terms.append(L_nu)
        return sp.Array(L_terms)

    else:
        raise ValueError(
            "Expected inverse_metric to be either (ndim x ndim) or (ndim,), "
            f"but got shape {shape}."
        )


def raise_index(
    tensor: _TensorType,
    inverse_metric: _MetricType,
    axis: int,
) -> _TensorType:
    r"""
    Raise a single index of a tensor using the provided inverse metric.

    This function supports:
    - A **full** inverse metric :math:`g^{\mu\nu}` (shape ``(n,n)``).
    - A **diagonal** inverse metric (1D array of length ``n``) for orthogonal coordinates.

    **General Formula** (when `inverse_metric` is a full matrix):

    .. math::

        T^{\ldots\mu\ldots} \;=\; T_{\ldots\nu\ldots}\; g^{\mu\nu},

    **Orthogonal Diagonal Case** (1D array):

    .. math::

        T^{\ldots\mu\ldots} \;=\; T_{\ldots\mu\ldots} \;\times\; g^{\mu\mu}.

    Parameters
    ----------
    tensor : ~sympy.tensor.array.MutableDenseNDimArray
     A symbolic tensor of arbitrary rank.
    inverse_metric: ~sympy.matrices.dense.MutableDenseMatrix or ~sympy.tensor.array.MutableDenseNDimArray
     Either a full inverse metric :math:`g^{\mu\nu}` (shape ``(n, n)``) or a 1D diagonal
     array of shape ``(n,)`` for orthogonal coordinates.
    axis : int
     The index position to raise.

    Returns
    -------
    ~sympy.tensor.array.MutableDenseNDimArray
        A new tensor with the specified index raised.

    See Also
    --------
    lower_index

    Examples
    --------
    1) **Full matrix** usage:

    .. code-block:: python

     >>> import sympy as sp
     >>> from pymetric.differential_geometry.symbolic import raise_index
     >>>
     >>> r, theta = sp.symbols('r theta', positive=True)
     >>> # Inverse metric for polar coords
     >>> ginv = sp.Matrix([[1, 0], [0, 1/r**2]])
     >>> # Rank-2 tensor
     >>> T = sp.Array([
     ...     [sp.Function("T0")(r, theta), sp.Function("T1")(r, theta)],
     ...     [sp.Function("T2")(r, theta), sp.Function("T3")(r, theta)]
     ... ])
     >>>
     >>> raise_index(T, ginv, axis=1)
     [[T0(r, theta), T1(r, theta)/r**2], [T2(r, theta), T3(r, theta)/r**2]]

    2) **Orthogonal diagonal** usage (just multiply each slice):

    .. code-block:: python

     >>> # Suppose inverse_metric is [1, 1/r^2]
     >>> ginv_diag = sp.Array([1, 1/r**2])
     >>> raise_index(T, ginv_diag, axis=1)
     [[T0(r, theta), T1(r, theta)/r**2], [T2(r, theta), T3(r, theta)/r**2]]
    """
    ndim = tensor.rank()
    if not (0 <= axis < ndim):
        raise ValueError(f"Axis {axis} out of bounds for a tensor of rank {ndim}.")

    shape = inverse_metric.shape
    if len(shape) == 2:
        # Full (n x n) approach
        # Standard tensor contraction approach
        tp = tensorproduct(inverse_metric, tensor)  # shape (ndim, ndim, ...)
        contracted = tensorcontraction(tp, (1, axis + 2))
        # Permute to place the new index in position 'axis'
        perm = list(range(1, axis + 1)) + [0] + list(range(axis + 1, ndim))
        return permutedims(contracted, perm)

    elif len(shape) == 1:
        # 1D => orthogonal diagonal approach
        new_tensor = sp.MutableDenseNDimArray(tensor)
        if tensor.shape[axis] > inverse_metric.shape[0]:
            raise ValueError(
                f"Tensor index {axis} has {tensor.shape[axis]} elements. Cannot contract with metric of length {inverse_metric.shape[0]}."
            )

        for i in range(tensor.shape[axis]):
            idx: List[Any] = [slice(None)] * ndim
            idx[axis] = i
            new_tensor[tuple(idx)] *= inverse_metric[i]
        return new_tensor

    else:
        raise ValueError(
            f"inverse_metric shape {shape} not understood. "
            "Must be 2D (square) or 1D (diagonal)."
        )


def lower_index(
    tensor: _TensorType,
    metric: _MetricType,
    axis: int,
) -> _TensorType:
    r"""
    Lower a single index of a tensor using the provided metric.

    This function supports:

    - A **full** metric :math:`g_{\mu\nu}` (shape ``(n,n)``).
    - A **diagonal** metric (1D array of length ``n``) for orthogonal coordinates.

    **General Formula** (when `metric` is a full matrix):

    .. math::

        T_{\ldots\nu\ldots} \;=\; T^{\ldots\mu\ldots}\; g_{\mu\nu},

    **Orthogonal Diagonal Case** (1D array):

    .. math::

        T_{\ldots\mu\ldots} \;=\; T^{\ldots\mu\ldots} \;\times\; g_{\mu\mu}.

    Parameters
    ----------
    tensor : ~sympy.tensor.array.MutableDenseNDimArray
     A symbolic tensor of arbitrary rank.
    metric : ~sympy.matrices.dense.MutableDenseMatrix or~sympy.tensor.array.MutableDenseNDimArray
     The metric used to lower the index. Either a full ``(n x n)`` matrix or a 1D array of length ``n``.
    axis : int
     The index position to lower.

    Returns
    -------
    ~sympy.tensor.array.MutableDenseNDimArray
     A new tensor with the specified index lowered.

    See Also
    --------
    raise_index

    Examples
    --------
    1) **Full matrix** usage:

    .. code-block:: python

        >>> import sympy as sp
        >>> from pymetric.differential_geometry.symbolic import lower_index
        >>>
        >>> r, theta = sp.symbols('r theta', positive=True)
        >>> # Metric for polar coords
        >>> g = sp.Matrix([[1, 0], [0, r**2]])
        >>> # Rank-2 tensor
        >>> T = sp.Array([
        ...     [sp.Function("T0")(r, theta), sp.Function("T1")(r, theta)],
        ...     [sp.Function("T2")(r, theta), sp.Function("T3")(r, theta)]
        ... ])
        >>>
        >>> lower_index(T, g, axis=1)
        [[T0(r, theta), r**2*T1(r, theta)], [T2(r, theta), r**2*T3(r, theta)]]

    2) **Orthogonal diagonal** usage (just multiply each slice):

    .. code-block:: python

        >>> g_diag = sp.Array([1, r**2])
        >>> lower_index(T, g_diag, axis=1)
        [[T0(r, theta), r**2*T1(r, theta)], [T2(r, theta), r**2*T3(r, theta)]]
    """
    ndim = tensor.rank()
    if not (0 <= axis < ndim):
        raise ValueError(f"Axis {axis} out of bounds for a tensor of rank {ndim}.")

    shape = metric.shape
    if len(shape) == 2:
        # Full (n x n) approach
        # Standard tensor contraction approach
        tp = tensorproduct(metric, tensor)  # shape: (ndim, ndim, ...)
        contracted = tensorcontraction(tp, (1, axis + 2))
        # Permute to place the new index in position 'axis'
        perm = list(range(1, axis + 1)) + [0] + list(range(axis + 1, ndim))
        return permutedims(contracted, perm)

    elif len(shape) == 1:
        # 1D => orthogonal diagonal approach
        new_tensor = sp.MutableDenseNDimArray(tensor)
        for i in range(tensor.shape[axis]):
            idx: List[Any] = [slice(None)] * ndim
            idx[axis] = i
            new_tensor[tuple(idx)] *= metric[i]
        return new_tensor

    else:
        raise ValueError(
            f"metric shape {shape} not understood. "
            "Must be 2D (square) or 1D (diagonal)."
        )


def adjust_tensor_signature(
    tensor: _TensorType,
    variance_in: Sequence[int],
    variance_out: Sequence[int],
    metric: _MetricType,
    inverse_metric: _MetricType,
) -> _TensorType:
    """
    Adjust the variance signature of a symbolic tensor by raising or lowering indices
    as needed.

    Parameters
    ----------
    tensor : sympy.tensor.array.Array
        The input symbolic tensor.
    variance_in : Sequence[int]
        The current variance of the tensor indices (1 = contravariant, -1 = covariant).
    variance_out : Sequence[int]
        The desired target variance of the tensor.
    metric : sympy.Matrix or sympy.Array
        The metric tensor for lowering.
    inverse_metric : sympy.Matrix or sympy.Array
        The inverse metric tensor for raising.

    Returns
    -------
    The adjusted tensor with the desired index signature.
    """
    if len(variance_in) != len(variance_out):
        raise ValueError("variance_in and variance_out must have the same length")

    result = tensor
    for axis, (v_in, v_out) in enumerate(zip(variance_in, variance_out)):
        if v_in == v_out:
            continue
        if v_in == -1 and v_out == 1:
            result = raise_index(result, inverse_metric, axis)
        elif v_in == 1 and v_out == -1:
            result = lower_index(result, metric, axis)
        else:
            raise ValueError(f"Invalid variance transition: {v_in} -> {v_out}")
    return result


def compute_gradient(
    scalar_field: sp.Basic,
    coordinate_axes: Sequence[sp.Symbol],
    basis: BasisAlias = "covariant",
    inverse_metric: Optional[_MetricType] = None,
) -> _TensorType:
    r"""
    Compute the symbolic gradient of a scalar field :math:`\phi` in either covariant or contravariant basis.

    Parameters
    ----------
    scalar_field : :py:class:`~sympy.core.basic.Basic`
        The scalar field :math:`\phi` to differentiate. This should be any valid sympy expression dependent
        on the ``coordinate_axes`` and any other relevant symbols.
    coordinate_axes : list of :py:class:`~sympy.core.symbol.Symbol`
        The coordinate axes (variables) with respect to which to compute the gradient. This should be the full
        list of the coordinate axes for the relevant coordinate system.
    basis : 'covariant' or 'contravariant', optional
        The basis in which to return the gradient. Defaults to 'covariant'.

        .. note::

            if ``basis != 'covariant'``, the index must be raised and the ``inverse_metric`` will be used
            for contraction. If ``inverse_metric`` is not specified, an error results.

    inverse_metric : ~sympy.matrices.dense.MutableDenseMatrix or ~sympy.tensor.array.MutableDenseNDimArray
        Either a full inverse metric :math:`g^{\mu\nu}` (shape ``(n, n)``) or a 1D diagonal
        array of shape ``(n,)`` for orthogonal coordinates.

    Returns
    -------
    :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The components of the gradient of :math:`\phi`, in the chosen basis.

    See Also
    --------
    compute_divergence
    compute_laplacian

    Examples
    --------
    Compute the gradient of the scalar field :math:`\phi(r,\theta) = r^2 \sin(\theta)`.

    >>> # Import the necessary functions.
    >>> import sympy as sp
    >>> from pymetric.differential_geometry.symbolic import compute_gradient
    >>>
    >>> # Create the symbols.
    >>> r, theta, phi = sp.symbols('r theta phi')
    >>> Phi = (r**2)*sp.sin(theta)
    >>> inv_metric = sp.Matrix([[1,0,0],[0,r**2,0],[0,0,r**2*sp.sin(theta)]]).inv()
    >>>
    >>> # Compute the covariant gradient.
    >>> compute_gradient(Phi, [r,theta, phi])
    [2*r*sin(theta), r**2*cos(theta), 0]
    >>>
    >>> # Compute the contravariant gradient.
    >>> compute_gradient(Phi, [r, theta, phi],basis='contravariant',inverse_metric=inv_metric)
    [2*r*sin(theta), cos(theta), 0]

    """
    # Begin by computing each of the relevant derivatives of the scalar field.
    _field_derivatives_ = sp.Array(
        [sp.diff(scalar_field, __axis_symbol__) for __axis_symbol__ in coordinate_axes]
    )

    # If contravariant basis is requested, raise the index using the inverse metric.
    if basis == "contravariant":
        if inverse_metric is None:
            raise ValueError(
                "An inverse_metric is required for contravariant gradient computation."
            )
        _field_derivatives_ = raise_index(_field_derivatives_, inverse_metric, axis=0)
    elif basis != "covariant":
        raise ValueError("`basis` must be either 'covariant' or 'contravariant'.")

    return _field_derivatives_


def compute_tensor_gradient(
    tensor: _TensorType,
    coordinate_axes: Sequence[sp.Symbol],
    basis: BasisAlias = "covariant",
    inverse_metric: Optional[_MetricType] = None,
) -> _TensorType:
    r"""
    Compute the gradient of a symbolic tensor field with arbitrary rank.

    This generalizes the scalar gradient to compute :math:`\partial_mu T^{\ldots}_{\ldots}` for each component,
    returning a new tensor of shape ``(n, *tensor.shape)``, where n is the number of coordinates.

    Parameters
    ----------
    tensor : sympy.Array
        The input symbolic tensor field.
    coordinate_axes : list of sympy.Symbol
        Coordinate variables.
    basis : 'covariant' or 'contravariant'
        Whether to compute ∂_μ or ∇^μ.
    inverse_metric : sympy.Matrix or Array
        Required if basis is 'contravariant'.

    Returns
    -------
    sympy.Array
        The symbolic gradient tensor with an added leading index.
    """
    ndim = len(coordinate_axes)
    grad_components = []

    for mu in range(ndim):
        deriv_tensor = sp.MutableDenseNDimArray.zeros(*tensor.shape)
        for idx in np.ndindex(*tensor.shape):
            deriv_tensor[idx] = sp.diff(tensor[idx], coordinate_axes[mu])
        grad_components.append(deriv_tensor)

    grad_tensor = sp.Array(grad_components)

    if basis == "contravariant":
        if inverse_metric is None:
            raise ValueError("inverse_metric is required for contravariant gradient.")
        grad_tensor = raise_index(grad_tensor, inverse_metric, axis=0)
    elif basis != "covariant":
        raise ValueError("`basis` must be either 'covariant' or 'contravariant'.")

    return grad_tensor


def compute_divergence(
    vector_field: _TensorType,
    coordinate_axes: Sequence[sp.Symbol],
    d_term: Optional[_TensorType] = None,
    basis: BasisAlias = "contravariant",
    inverse_metric: Optional[_MetricType] = None,
    metric_density: Optional[sp.Basic] = None,
) -> sp.Basic:
    r"""
    Compute the divergence :math:`\nabla \cdot {\bf F}` of a vector field symbolically.

    In general curvilinear coordinates, the divergence of a vector field :math:`{\bf F}` is

    .. math::

        \nabla \cdot {\bf F} = \frac{1}{\rho} \partial_\mu \left(\rho F^\mu\right),

    where :math:`\rho = \sqrt{{\rm Det} \; g}`.

    Parameters
    ----------
    vector_field : :py:class:`~sympy.tensor.array.MutableDenseNDimArray`
        The vector field components, assumed to be contravariant unless otherwise specified.
    coordinate_axes : list of :py:class:`~sympy.core.symbol.Symbol`
        The coordinate symbols associated with each axis.
    d_term : :py:class:`~sympy.tensor.array.MutableDenseNDimArray`, optional
        The D-term components, used to account for the geometry (can be derived from metric_density).
    basis : {'covariant', 'contravariant'}, optional
        The basis in which the input vector field is expressed. Defaults to 'contravariant'.
    inverse_metric : ~sympy.matrices.dense.MutableDenseMatrix or ~sympy.tensor.array.MutableDenseNDimArray
        Either a full inverse metric :math:`g^{\mu\nu}` (shape ``(n, n)``) or a 1D diagonal
        array of shape ``(n,)`` for orthogonal coordinates.
    metric_density : :py:class:`~sympy.core.basic.Basic`, optional
        The metric density :math:`\rho`, used to compute the D-term if it is not provided.

    Returns
    -------
    :py:class:`~sympy.core.basic.Basic`
        The symbolic expression for the divergence of the vector field.

    See Also
    --------
    compute_gradient
    compute_laplacian

    Examples
    --------
    In spherical coordinates, then vector field :math:`{\bf F} = r \hat{\bf e}_\theta` has a divergence

    .. math::

        \nabla \cdot {\bf F} = \frac{1}{r^2\sin\theta} \partial_\theta \left[r^3\sin \theta \right] = \frac{r}{\tan \theta}.

    To perform this operation inPyMetric,

    >>> import sympy as sp
    >>> from pymetric.differential_geometry.symbolic import (
    ...     compute_divergence, compute_Dterm
    ... )
    >>>
    >>> # Define coordinate symbols and metric
    >>> r, theta, phi = sp.symbols('r theta phi', positive=True)
    >>> coords = [r, theta, phi]
    >>> metric_density = r**2 * sp.sin(theta)
    >>>
    >>> # Define the vector field.
    >>> V = sp.Array([0, r, 0])
    >>>
    >>> # Compute divergence
    >>> compute_divergence(V, coords, metric_density=metric_density)
    r/tan(theta)

    """
    # Validation steps. Ensure that the vector field has the correct number of dimensions
    # and that the necessary components are derived to proceed with the computation.
    ndim = len(coordinate_axes)
    if vector_field.shape != (ndim,):
        raise ValueError(
            f"Expected vector field of shape ({ndim},), got {vector_field.shape}"
        )

    # check the d-term. We may need to construct it and then we need to ensure that
    # it has the intended shape.
    if d_term is None:
        # We need to derive the d_term.
        if metric_density is None:
            raise ValueError("Either d_term or metric_density must be provided.")
        d_term = compute_Dterm(metric_density, coordinate_axes)
    if d_term.shape != (ndim,):
        raise ValueError(f"Expected d_term of shape ({ndim},), got {d_term.shape}")

    # Ensure that the vector field is correctly cast in the contravariant basis so that
    # we can perform the necessary operations. If it is not, then we need to raise the index.
    if basis == "covariant":
        if inverse_metric is None:
            raise ValueError(
                "inverse_metric is required to raise a covariant vector field."
            )
        vector_field = raise_index(vector_field, inverse_metric, axis=0)
    elif basis != "contravariant":
        raise ValueError("`basis` must be either 'covariant' or 'contravariant'.")

    # Perform the sums to get the desired behavior.
    divergence = sum(
        d_term[i] * vector_field[i] + sp.diff(vector_field[i], coordinate_axes[i])
        for i in range(ndim)
    )

    return sp.simplify(divergence)


def compute_laplacian(
    scalar_field: sp.Basic,
    coordinate_axes: Sequence[sp.Symbol],
    inverse_metric: sp.Matrix,
    l_term: Optional[_TensorType] = None,
    metric_density: Optional[sp.Basic] = None,
) -> sp.Basic:
    r"""
    Compute the Laplacian :math:`\nabla^2 \phi` of a scalar field in general or orthogonal curvilinear coordinates.

    In a general coordinate system, the Laplacian of a scalar field :math:`\phi` can be expressed as:

    .. math::

        \nabla^2 \phi = \frac{1}{\rho} \,\partial_\mu \bigl(\rho \,g^{\mu\nu}\,\partial_\nu \phi\bigr)
                     = L^\nu \,\partial_\nu \phi \;+\; g^{\mu\nu}\,\partial^2_{\mu\nu}\phi,

    where :math:`\rho` is the metric density :math:`\sqrt{\det g}` and :math:`g^{\mu\nu}` is the inverse metric.
    The **L-term** is defined by:

    .. math::

        L^\nu = \frac{1}{\rho} \,\partial_\mu \bigl(\rho \,g^{\mu\nu}\bigr).

    **Usage**:

    - If ``inverse_metric`` is a full :math:`(n \times n)` matrix, a fully general coordinate system is assumed.
    - If ``inverse_metric`` is a 1D array of length :math:`n`, an orthogonal system is assumed (the array contains the diagonal
      elements :math:`g^{\mu\mu}`).

    Parameters
    ----------
    scalar_field : ~sympy.core.basic.Basic
        The scalar field :math:`\phi` whose Laplacian is computed.
    coordinate_axes : list of ~sympy.core.symbol.Symbol
        The coordinate variables :math:`x^\mu` with respect to which differentiation occurs.
    inverse_metric : ~sympy.matrices.dense.MutableDenseMatrix or ~sympy.tensor.array.MutableDenseNDimArray
        Either a full inverse metric :math:`g^{\mu\nu}` (shape ``(n, n)``) or a 1D diagonal
        array of shape ``(n,)`` for orthogonal coordinates.

    l_term : ~sympy.tensor.array.MutableDenseNDimArray, optional
        Precomputed L-terms :math:`L^\nu`. If not provided, these will be derived from ``metric_density`` and ``inverse_metric``.
    metric_density : ~sympy.core.basic.Basic, optional
        The metric density :math:`\rho = \sqrt{\det g}`. Required if ``l_term`` is not given.

    Returns
    -------
    ~sympy.core.basic.Basic
        The scalar Laplacian :math:`\nabla^2 \phi`.

    See Also
    --------
    compute_Lterm : Compute the L-term from :math:`\rho` and :math:`g^{\mu\nu}`.
    compute_metric_density : For computing :math:`\rho`.
    compute_divergence : The divergence in curvilinear coordinates.

    Examples
    --------
    **1) Full Inverse Metric (Spherical)**

    .. code-block:: python

        >>> import sympy as sp
        >>> from pymetric.differential_geometry.symbolic import compute_laplacian, compute_metric_density
        >>>
        >>> r, theta, phi = sp.symbols('r theta phi')
        >>> scalar = r**2 * sp.sin(theta)
        >>>
        >>> # Full inverse metric for spherical coordinates
        >>> g_inv = sp.Matrix([
        ...     [1, 0, 0],
        ...     [0, 1/r**2, 0],
        ...     [0, 0, 1/(r**2 * sp.sin(theta)**2)]
        ... ])
        >>> # Metric density
        >>> rho = compute_metric_density(sp.Matrix([
        ...     [1,      0, 0],
        ...     [0, r**2, 0],
        ...     [0,      0, (r*sp.sin(theta))**2]
        ... ]))
        >>>
        >>> # Compute Laplacian
        >>> lap = compute_laplacian(scalar, [r, theta, phi], g_inv, metric_density=rho)
        >>> lap
        4*sin(theta) + 1/sin(theta)

    **2) Orthogonal Inverse Metric (Diagonal Only)**

    .. code-block:: python

        >>> # Provide just the diagonal of g^{\mu\nu} for an orthogonal system
        >>> g_inv_diag = sp.Array([1, 1/r**2, 1/(r**2*sp.sin(theta)**2)])
        >>> # Same metric_density as above
        >>> lap_ortho = compute_laplacian(scalar, [r, theta, phi], g_inv_diag, metric_density=rho)
        >>> lap_ortho
        4*sin(theta) + 1/sin(theta)
    """
    # Determine the number of dimensions in the coordinate
    # system and start ensuring that the L-terms are available and
    # accounted for.
    ndim = len(coordinate_axes)

    # Build the L-terms.
    if l_term is None:
        if (metric_density is None) or (inverse_metric is None):
            raise ValueError(
                "Either `l_term` or `metric_density` and `inverse_metric` must be provided."
            )
        l_term = compute_Lterm(inverse_metric, metric_density, coordinate_axes)

    if l_term.shape != (ndim,):
        raise ValueError(f"Expected l_term of shape ({ndim},), got {l_term.shape}")

    # Build up the Laplacian: ∇²φ = L^μ ∂_μ φ + g^{μν} ∂²_{μν} φ
    gradient_terms = [
        l_term[i] * sp.diff(scalar_field, coordinate_axes[i]) for i in range(ndim)
    ]

    # Distinguish between diagonal or full inverse metric
    shape = inverse_metric.shape
    if len(shape) == 1:
        # Diagonal -> orthogonal
        second_deriv_terms = [
            inverse_metric[i]
            * sp.diff(scalar_field, coordinate_axes[i], coordinate_axes[i])
            for i in range(ndim)
        ]
    elif len(shape) == 2:
        # Full metric
        second_deriv_terms = [
            inverse_metric[i, j]
            * sp.diff(scalar_field, coordinate_axes[i], coordinate_axes[j])
            for i in range(ndim)
            for j in range(ndim)
        ]
    else:
        raise ValueError("Inverse metric must be either 1D (orthogonal) or 2D (full).")

    return sp.simplify(sum(gradient_terms) + sum(second_deriv_terms))


def compute_tensor_laplacian(
    tensor: _TensorType,
    coordinate_axes: Sequence[sp.Symbol],
    inverse_metric: _MetricType,
    l_term: Optional[_TensorType] = None,
    metric_density: Optional[sp.Basic] = None,
) -> _TensorType:
    """
    Compute the Laplacian of each component of a symbolic tensor field.

    Parameters
    ----------
    tensor : sympy.Array
        A symbolic tensor field of arbitrary shape.
    coordinate_axes : list of sympy.Symbol
        The coordinate variables.
    inverse_metric : sympy.Matrix or Array
        Inverse metric tensor.
    l_term : sympy.Array, optional
        Precomputed L-term (otherwise derived from metric_density).
    metric_density : sympy.Basic, optional
        Used to compute L-term if not provided.

    Returns
    -------
    sympy.Array
        A symbolic tensor of the same shape, with Laplacian applied component-wise.
    """
    lap = sp.MutableDenseNDimArray.zeros(*tensor.shape)
    for idx in np.ndindex(*tensor.shape):
        lap[idx] = compute_laplacian(
            tensor[idx], coordinate_axes, inverse_metric, l_term, metric_density
        )
    return lap
