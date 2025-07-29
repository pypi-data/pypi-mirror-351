# -*- coding: utf-8 -*-
"""
Test the static solver.

@author: ricriv
"""

# Here we are relying on the default behavior of pytest, which is to execute
# the tests in the same order that they are specified.
# If one day this will not be the case anymore, we can enforce the order by
# using the solution proposed at: https://stackoverflow.com/a/77793427/3676517

import pytest

import numpy as np
from numpy import testing as npt

from h2lib._h2lib import H2Lib
from h2lib_tests.test_files import tfp


def test_solver_static_update_no_init(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_NOT_INITIALIZED"):
        h2_dtu_10mw_only_blade.solver_static_update()


def test_solver_static_solve_no_init(h2_dtu_10mw_only_blade):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_NOT_INITIALIZED"):
        h2_dtu_10mw_only_blade.solver_static_solve()


def test_solver_static_init(h2_dtu_10mw_only_blade):

    # First execution is fine.
    h2_dtu_10mw_only_blade.solver_static_init()

    # The next should automatically deallocate the static solver and initialize it again.
    h2_dtu_10mw_only_blade.solver_static_init()


def test_solver_static_update(h2_dtu_10mw_only_blade):
    # This should happen after test_solver_static_init().
    h2_dtu_10mw_only_blade.solver_static_update()


def test_solver_static_solve(h2_dtu_10mw_only_blade):
    # This should happen after test_solver_static_update().
    h2_dtu_10mw_only_blade.solver_static_solve()


def test_solver_static_delete(h2_dtu_10mw_only_blade):
    h2_dtu_10mw_only_blade.solver_static_delete()


def test_static_solver_run_fail(h2_dtu10mw_only_blade_low_max_iter):
    with pytest.raises(RuntimeError, match="STATIC_SOLVER_DID_NOT_CONVERGE"):
        h2_dtu10mw_only_blade_low_max_iter.solver_static_run()


def test_static_solver_run_1(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.
    # Add a sensor for the blade root moment, in this case only due to gravity.
    id = h2_dtu_10mw_only_blade.add_sensor("mbdy momentvec blade1 1 1 blade1")

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade.step()
    val = h2_dtu_10mw_only_blade.get_sensor_values(id)
    # Test against: initial_condition 2; followed by time simulaiton.
    npt.assert_allclose(
        val, np.array([-1.072136e04, -3.978756e-02, -4.066154e01]), rtol=1e-6
    )


def test_static_solver_run_2(h2_dtu_10mw_only_blade_rotate_base):
    # Apply centrifugal loading with the base command.
    # Add a sensor for the blade root force, in this case only due to centrifugal force.
    id = h2_dtu_10mw_only_blade_rotate_base.add_sensor(
        "mbdy forcevec blade1 1 1 blade1"
    )

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_base.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade_rotate_base.step()
    val = h2_dtu_10mw_only_blade_rotate_base.get_sensor_values(id)
    # Test against: result at the time of writing.
    npt.assert_allclose(val, np.array([10879.057846, 383.58397, 991.216685]))


def test_static_solver_run_3(h2_dtu_10mw_only_blade_rotate_relative):
    # Apply centrifugal loading with the relative command.
    # Add a sensor for the blade root force, in this case only due to centrifugal force.
    id = h2_dtu_10mw_only_blade_rotate_relative.add_sensor(
        "mbdy forcevec blade1 1 1 blade1"
    )

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_relative.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade_rotate_relative.step()
    val = h2_dtu_10mw_only_blade_rotate_relative.get_sensor_values(id)
    # Test against: result at the time of writing.
    npt.assert_allclose(val, np.array([10879.011239, 383.582323, 991.217846]))


def test_static_solver_run_4(h2_dtu_10mw_only_blade_rotate_bearing3):
    # Apply centrifugal loading with the bearing3 command.
    # Add a sensor for the blade root moment, in this case only due to centrifugal force.
    id = h2_dtu_10mw_only_blade_rotate_bearing3.add_sensor(
        "mbdy momentvec blade1 1 1 blade1"
    )

    # Run the static solver.
    h2_dtu_10mw_only_blade_rotate_bearing3.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade_rotate_bearing3.step()
    val = h2_dtu_10mw_only_blade_rotate_bearing3.get_sensor_values(id)
    # Test against: result at the time of writing.
    npt.assert_allclose(val, np.array([-3097.095312, 115414.360165, 366.321024]))


def test_static_solver_run_no_reset(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Run it again, without resetting the structure.
    # The static solver must exit immediately and output the same residuals.
    _, resq_1, resg_1, resd_1 = h2_dtu_10mw_only_blade.check_convergence()
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=False)
    _, resq_2, resg_2, resd_2 = h2_dtu_10mw_only_blade.check_convergence()

    npt.assert_allclose(
        np.array([resq_2, resg_2, resd_2]), np.array([resq_2, resg_2, resd_2])
    )


def test_static_solver_run_with_reset(h2_dtu_10mw_only_blade):
    # Use gravity to deflect the clamped blade.

    # Run the static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Run it again, but first reset the structure.
    # The static solver must follow the same convergence history.
    # Note that here we are only checking the last value of the residuals.
    _, resq_1, resg_1, resd_1 = h2_dtu_10mw_only_blade.check_convergence()
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)
    _, resq_2, resg_2, resd_2 = h2_dtu_10mw_only_blade.check_convergence()

    npt.assert_allclose(
        np.array([resq_2, resg_2, resd_2]), np.array([resq_2, resg_2, resd_2])
    )


def test_structure_reset():
    # Apply centrifugal loading with the base command.
    # We cannot use h2_dtu_10mw_only_blade_rotate_base because we need to add a sensor,
    # and this must be done before init.

    with H2Lib(suppress_output=True) as h2:
        model_path = f"{tfp}DTU_10_MW/"
        htc_path = "htc/DTU_10MW_RWT_only_blade_rotate_base.htc"
        id = h2.add_sensor(
            "mbdy statevec_new blade1 c2def global absolute 85.0 1.0 0.0 0.0"
        )
        h2.init(htc_path=htc_path, model_path=model_path)
        h2.stop_on_error(False)

        # Do 1 step to get the output. This is our reference.
        h2.step()
        val_desired = h2.get_sensor_values(id)

        # Run static solver.
        h2.solver_static_run(reset_structure=False)

        # The deflection must have changed.
        h2.step()
        val_actual = h2.get_sensor_values(id)
        npt.assert_raises(AssertionError, npt.assert_allclose, val_actual, val_desired)

        # Reset the structure and check that we match the reference.
        h2.structure_reset()
        h2.step()
        val_actual = h2.get_sensor_values(id)
        npt.assert_allclose(val_actual, val_desired)
