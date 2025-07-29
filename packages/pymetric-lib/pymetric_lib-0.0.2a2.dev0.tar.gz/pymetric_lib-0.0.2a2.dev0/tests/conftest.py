"""
Test configuration for pymetric.

This module is used to control the behavior of pytest when running the testing
system.
"""
import numpy as np

# --- Imports --- #
import pytest

from pymetric.coordinates import (
    CartesianCoordinateSystem1D,
    CartesianCoordinateSystem2D,
    CartesianCoordinateSystem3D,
    ConicCoordinateSystem,
    CylindricalCoordinateSystem,
    EllipticCylindricalCoordinateSystem,
    OblateHomoeoidalCoordinateSystem,
    OblateSpheroidalCoordinateSystem,
    PolarCoordinateSystem,
    ProlateHomoeoidalCoordinateSystem,
    ProlateSpheroidalCoordinateSystem,
    SphericalCoordinateSystem,
)
from pymetric.grids import UniformGrid

# --------------------------------- #
# Configuration State Variables     #
# --------------------------------- #
__default_uniform_grid_resolution__: int = 10
""" The default resolution along each axis of the uniform coordinate
grids made available for each of the relevant coordinate systems.
"""

# --- Coordinate System Registration --- #
# Each of the pymetric coordinate systems must be registered
# here in order to be recognized as testing parameters. Each entry
# is (class, bbox) for generating grids.
__pymetric_all_coordinate_systems__ = {
    "cartesian1D": (CartesianCoordinateSystem1D, [[0], [1]]),
    "cartesian2D": (CartesianCoordinateSystem2D, [[0, 0], [1, 1]]),
    "cartesian3D": (CartesianCoordinateSystem3D, [[0, 0, 0], [1, 1, 1]]),
    "spherical": (SphericalCoordinateSystem, [[0, 0, 0], [1, np.pi, 2 * np.pi]]),
    "cylindrical": (CylindricalCoordinateSystem, [[0, 0, 0], [1, 2 * np.pi, 1]]),
    "polar": (PolarCoordinateSystem, [[0, 0], [1, 2 * np.pi]]),
    "oblate_spheroidal": (
        lambda: OblateSpheroidalCoordinateSystem(a=1.0),
        [[0, -np.pi / 2, 0], [1.5, np.pi / 2, 2 * np.pi]],
    ),
    "prolate_spheroidal": (
        lambda: ProlateSpheroidalCoordinateSystem(a=1.0),
        [[0, 0, 0], [1.5, np.pi, 2 * np.pi]],
    ),
    "elliptic_cylindrical": (
        lambda: EllipticCylindricalCoordinateSystem(a=1.0),
        [[0, 0, 0], [1.5, 2 * np.pi, 1]],
    ),
    "oblate_homoeoidal": (
        lambda: OblateHomoeoidalCoordinateSystem(ecc=0.3),
        [[1, 0, 0], [2, np.pi, 2 * np.pi]],
    ),
    "prolate_homoeoidal": (
        lambda: ProlateHomoeoidalCoordinateSystem(ecc=0.3),
        [[1, 0, 0], [2, np.pi, 2 * np.pi]],
    ),
    "conic": (
        lambda: ConicCoordinateSystem(a=1.0),
        [[0.1, 0.2, 0], [np.pi - 0.1, np.pi - 0.2, 2 * np.pi]],
    ),
}


# ---------------------------------- #
# CLI Options                        #
# ---------------------------------- #
# These are CLI options which enrich the behavior
# and control of pytest for this suite of tests.
def pytest_addoption(parser):
    """
    Adds the ``--coord-systems`` option to the pytest command line. This
    is (by default) ``"all"``, which will cause tests to go through all of
    the registered coordinate systems.

    It can be set to a comma-separated list of coordinate systems to restrict
    which coordinate systems are tested.
    """
    parser.addoption(
        "--coord_systems",
        action="store",
        default="all",
        help="Comma-separated list of coordinate systems (e.g. 'spherical,cartesian3D')",
    )


# ---------------------------------- #
# Test Generation                    #
# ---------------------------------- #
def pytest_generate_tests(metafunc):
    # --- Parameterizing over cs_flag --- #
    # This generates tests with parameterization over the cs_flag fixture
    # if it is asked for. In this case, the parameterization is implicit.
    selected_flag = metafunc.config.getoption("coord_systems")

    if selected_flag == "all":
        selected_names = list(__pymetric_all_coordinate_systems__.keys())
    else:
        selected_names = [x.strip() for x in selected_flag.split(",")]

    if "cs_flag" in metafunc.fixturenames:
        metafunc.parametrize("cs_flag", selected_names, ids=selected_names)


# ---------------------------------- #
# Testing Fixtures                   #
# ---------------------------------- #
@pytest.fixture(scope="session")
def coordinate_system_flag(request):
    """
    Fixture providing the coordinate system flag for the
    testing session.
    """
    return request.config.getoption("--coord-systems")


@pytest.fixture(scope="session")
def coordinate_systems(request):
    """
    Fixture that returns the filtered set of coordinate systems
    as a dictionary keyed by their ID.

    The result respects the --coord-systems flag.
    """
    selected = request.config.getoption("--coord_systems")

    # Determine if the selected is all or a subset of
    # keys.
    if selected == "all":
        selected = list(__pymetric_all_coordinate_systems__.keys())
    else:
        selected = [x.strip() for x in selected.split(",")]

    # Construct the dictionary of constructed, fully realized
    # coordinate systems.
    try:
        __coordinate_systems_initialized__ = {
            k: __pymetric_all_coordinate_systems__[k][0]() for k in selected
        }
    except KeyError:
        raise ValueError(
            f"Coordinate system flag --coord_systems={request.config.getoption('--coord_systems')} is not valid."
        )

    return __coordinate_systems_initialized__


@pytest.fixture(scope="session")
def uniform_grids(coordinate_systems):
    """
    Fixture that returns a dictionary of UniformGrid instances
    keyed by coordinate system name. Grids are built using the
    filtered coordinate systems and associated bounding boxes.
    """
    grids = {}
    for name, cs in coordinate_systems.items():
        _, bbox = __pymetric_all_coordinate_systems__[name]
        shape = [__default_uniform_grid_resolution__] * cs.ndim
        grids[name] = UniformGrid(cs, bbox, shape, center="cell")
    return grids
