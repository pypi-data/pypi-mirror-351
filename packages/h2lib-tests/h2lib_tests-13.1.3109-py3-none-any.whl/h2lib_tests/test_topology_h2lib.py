from h2lib._h2lib import H2Lib

from numpy import testing as npt
from h2lib_tests.test_files import tfp
import numpy as np
import pytest


def test_number_of_bodies_and_constraints(
    h2_dtu_10mw_only_tower,
):
    nbdy, ncst = h2_dtu_10mw_only_tower.get_number_of_bodies_and_constraints()
    assert nbdy == 3
    assert ncst == 9


def test_number_of_bodies_and_constraints_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_number_of_bodies_and_constraints()


def test_get_number_of_elements(h2_dtu_10mw_only_tower):
    nelem = h2_dtu_10mw_only_tower.get_number_of_elements()
    npt.assert_array_equal(nelem, np.array([3, 3, 4]))


def test_get_number_of_elements_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    # This test is not really needed, since the check for confidential structure
    # is already done by test_number_of_bodies_and_constraints_encrypted().
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_number_of_elements()


def test_get_timoshenko_location(
    h2_dtu_10mw_only_tower,
):
    # Test first element.
    l, r1, r12, tes = h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=0, ielem=0)
    assert l - 11.5 < 1e-14
    npt.assert_array_equal(r1, np.array([0.0, 0.0, 0]))
    npt.assert_array_almost_equal_nulp(r12, np.array([0.0, 0.0, -11.5]))
    npt.assert_array_equal(
        tes,
        np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]),
    )

    # Test last element.
    l, r1, r12, tes = h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=2, ielem=3)
    assert l - 12.13 < 1e-14
    npt.assert_array_almost_equal_nulp(r1, np.array([0.0, 0.0, -34.5]))
    npt.assert_array_almost_equal_nulp(r12, np.array([0.0, 0.0, -12.13]), nulp=3)
    npt.assert_array_equal(
        tes,
        np.array([[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]),
    )


def test_get_timoshenko_location_body_does_not_exist(
    h2_dtu_10mw_only_tower,
):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=1000, ielem=0)


def test_get_timoshenko_location_element_does_not_exist(
    h2_dtu_10mw_only_tower,
):
    with pytest.raises(IndexError, match="ELEMENT_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_timoshenko_location(ibdy=0, ielem=1000)


def test_get_timoshenko_location_encrypted(
    h2_dtu_10mw_only_tower_encrypted,
):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_timoshenko_location(ibdy=0, ielem=0)


def test_get_body_rotation_tensor_1(h2_dtu_10mw_only_tower):
    amat = h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_equal(amat, np.eye(3))


def test_get_body_rotation_tensor_2(
    h2_dtu_10mw_only_tower_rotated, write_dtu10mw_only_tower_rotated
):
    amat = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    _, alpha = write_dtu10mw_only_tower_rotated
    alpha_rad = np.deg2rad(alpha)
    sa = np.sin(alpha_rad)
    ca = np.cos(alpha_rad)
    npt.assert_array_almost_equal_nulp(
        amat, np.array([[1.0, 0.0, 0.0], [0.0, ca, -sa], [0.0, sa, ca]])
    )


def test_get_body_rotation_tensor_body_does_not_exist(h2_dtu_10mw_only_tower):
    with pytest.raises(IndexError, match="BODY_DOES_NOT_EXIST"):
        h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=1000)


def test_get_body_rotation_tensor_encrypted(h2_dtu_10mw_only_tower_encrypted):
    with pytest.raises(RuntimeError, match="STRUCTURE_IS_CONFIDENTIAL"):
        h2_dtu_10mw_only_tower_encrypted.get_body_rotation_tensor(ibdy=0)


def test_set_orientation_base_not_found(h2_dtu_10mw_only_tower):
    with pytest.raises(ValueError, match="MAIN_BODY_NOT_FOUND"):
        h2_dtu_10mw_only_tower.set_orientation_base(main_body="blade")


def test_set_orientation_base_1(h2_dtu_10mw_only_tower, h2_dtu_10mw_only_tower_rotated):
    # Start from h2_dtu_10mw_only_tower and rotate the base.
    # See if it matches h2_dtu_10mw_only_tower_rotated.
    h2_dtu_10mw_only_tower.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )
    amat_desired = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    amat_actual = h2_dtu_10mw_only_tower.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)
    # Reset orientation.
    h2_dtu_10mw_only_tower.set_orientation_base(main_body="tower")


def test_set_orientation_base_with_reset_orientation(
    h2_dtu_10mw_only_tower_rotated,
):
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", reset_orientation=True
    )
    amat_actual = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, np.eye(3))
    # Reset orientation.
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )


def test_set_orientation_base_without_reset_orientation(
    h2_dtu_10mw_only_tower_rotated,
):
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower",
        mbdy_eulerang_table=np.array([-30.0, 0.0, 0.0]),
        reset_orientation=False,
    )
    amat_actual = h2_dtu_10mw_only_tower_rotated.get_body_rotation_tensor(ibdy=0)
    npt.assert_array_almost_equal_nulp(amat_actual, np.eye(3))
    # Reset orientation.
    h2_dtu_10mw_only_tower_rotated.set_orientation_base(
        main_body="tower", mbdy_eulerang_table=np.array([30.0, 0.0, 0.0])
    )


def test_set_orientation_base_speed(h2_dtu_10mw_only_blade):
    # Add a sensor for the blade root force, in this case only due to centrifugal force.
    id = h2_dtu_10mw_only_blade.add_sensor("mbdy forcevec blade1 1 1 blade1")

    # Set speed.
    h2_dtu_10mw_only_blade.set_orientation_base(
        main_body="blade1",
        reset_orientation=False,
        mbdy_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )
    # Run static solver.
    h2_dtu_10mw_only_blade.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade.step()
    val = h2_dtu_10mw_only_blade.get_sensor_values(id)

    # Test against: result at the time of writing.
    # The result is close, but not identical, to test_static_solver_run_2.
    npt.assert_allclose(val, np.array([10879.363636, 793.815211, 1034.923463]))

    # Reset speed.
    h2_dtu_10mw_only_blade.set_orientation_base(
        main_body="blade1",
        reset_orientation=False,
    )


def test_set_orientation_relative_main_body_not_found(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    h2_dtu_10mw_only_blade_rotate_relative.stop_on_error(False)
    with pytest.raises(ValueError, match="MAIN_BODY_NOT_FOUND"):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative("hub1", "last", "blade", 0)


def test_set_orientation_relative_rot_not_found(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    with pytest.raises(ValueError, match="RELATIVE_ROTATION_NOT_FOUND"):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
            "hub1", "last", "blade1", "last"
        )


def test_set_orientation_relative_reset(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Reset orientation.
    # Now the blade is aligned with the hub, which is vertical.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        reset_orientation=True,
    )
    # Get orientation of blade root.
    amat_actual = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    # It must be the same as the hub.
    amat_desired = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=0
    )
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)
    # This matches a rotation around x by 180 deg.
    # angle = np.deg2rad(180.0)
    # s = np.sin(angle)
    # c = np.cos(angle)
    # amat_test = np.array(
    #     [[1.0, 0.0, 0.0], [0.0, c, -s], [0.0, s, c]],
    # )
    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )


def test_set_orientation_relative_2(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Get orientation of blade root.
    amat_desired = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    # Change orientation a few times.
    rng = np.random.default_rng(seed=123)
    for _ in range(5):
        h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
            main_body_1="hub1",
            node_1="last",
            main_body_2="blade1",
            node_2=0,
            mbdy2_eulerang_table=rng.uniform(0.0, 360.0, (7, 3)),
            reset_orientation=0,
        )
    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )
    # Check.
    amat_actual = h2_dtu_10mw_only_blade_rotate_relative.get_body_rotation_tensor(
        ibdy=1
    )
    npt.assert_array_almost_equal_nulp(amat_actual, amat_desired)


def test_set_orientation_relative_static(
    h2_dtu_10mw_only_blade_rotate_relative,
):
    # Add a sensor for the blade root force.
    id = h2_dtu_10mw_only_blade_rotate_relative.add_sensor(
        "mbdy forcevec blade1 1 1 blade1"
    )

    # Set arbitrary orientation and speed.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        reset_orientation=True,
        mbdy2_eulerang_table=np.array([-80.0, 0.0, 0.0]),
        mbdy2_ini_rotvec_d1=[0.0, 1.0, 0.0, 0.8],
    )
    # Run static solver.
    h2_dtu_10mw_only_blade_rotate_relative.solver_static_run(reset_structure=True)

    # Do 1 step to get the output.
    h2_dtu_10mw_only_blade_rotate_relative.step()
    val = h2_dtu_10mw_only_blade_rotate_relative.get_sensor_values(id)

    # Test against: result at the time of writing.
    npt.assert_allclose(val, np.array([8702.206018, 306.728782, 640.051269]))

    # Reset to original value.
    h2_dtu_10mw_only_blade_rotate_relative.set_orientation_relative(
        main_body_1="hub1",
        node_1="last",
        main_body_2="blade1",
        node_2=0,
        mbdy2_eulerang_table=np.array([-90.0, 0.0, 0.0]),
        reset_orientation=True,
        mbdy2_ini_rotvec_d1=np.array([0.0, 1.0, 0.0, 1.0]),
    )
