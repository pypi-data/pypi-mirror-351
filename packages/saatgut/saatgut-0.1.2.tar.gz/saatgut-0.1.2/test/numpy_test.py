import unittest

from saatgut import seed_numpy


class TestNumpy(unittest.TestCase):
    def test_seed_numpy(self):
        """
        Test the seed_numpy function to ensure it runs without errors.
        """
        seed_numpy(42)

    def test_seed_numpy_reproducibility(self):
        """
        Test that the seed_numpy function sets the same seed for multiple calls.
        """
        import numpy as np
        seed = 42
        seed_numpy(seed)

        # Generate a random array
        array1 = np.random.rand(3, 3)

        # Reset the seed and generate again
        seed_numpy(seed)
        array2 = np.random.rand(3, 3)

        # Check if both arrays are equal
        np.testing.assert_array_equal(array1, array2, "Arrays are not equal, seeding failed.")
