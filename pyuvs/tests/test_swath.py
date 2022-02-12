import numpy as np
import pytest
from pyuvs.swath import swath_number


class TestSwathNumber:
    @pytest.fixture
    def one_swath_mirror_angles(self):
        yield np.linspace(70, 110, num=50)

    @pytest.fixture
    def one_swath_swath_numbers(self):
        yield np.zeros((50,))

    @pytest.fixture
    def six_swath_increasing_mirror_angles(self):
        mirror_angles = np.linspace(70, 110, num=50)
        yield np.concatenate([mirror_angles for f in range(6)])

    @pytest.fixture
    def six_swath_decreasing_mirror_angles(self):
        mirror_angles = np.linspace(110, 70, num=50)
        yield np.concatenate([mirror_angles for f in range(6)])

    @pytest.fixture
    def six_swath_swath_numbers(self):
        yield np.concatenate([np.ones((50,)) * f for f in range(6)])

    def test_six_swath_increasing_mirror_angles_match_known_swath_numbers(
            self, six_swath_increasing_mirror_angles, six_swath_swath_numbers):
        assert np.array_equal(swath_number(six_swath_increasing_mirror_angles),
                              six_swath_swath_numbers)

    def test_six_swath_decreasing_mirror_angles_match_known_swath_numbers(
            self, six_swath_decreasing_mirror_angles, six_swath_swath_numbers):
        assert np.array_equal(swath_number(six_swath_decreasing_mirror_angles),
                              six_swath_swath_numbers)

    def test_monotonically_increasing_mirror_angles_returns_array_of_0s(
            self, one_swath_mirror_angles, one_swath_swath_numbers):
        assert np.array_equal(swath_number(one_swath_mirror_angles),
                              one_swath_swath_numbers)

    def test_single_integration_returns_array_of_0(self):
        assert np.array_equal(swath_number(np.array([100])), np.array([0]))
