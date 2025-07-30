import unittest

from saatgut import seed_everything


class TestSeedEverything(unittest.TestCase):
    def test_seed_everything(self):
        """
        Test the seed_everything function to ensure it runs without errors.
        """
        try:
            seed_everything(42)
        except Exception as e:
            self.fail(f"seed_everything raised an exception: {e}")

    def test_seed_everything_reproducibility(self):
        """
        Test that the seed_everything function sets the same seed for multiple calls.
        """
        import random
        import numpy as np
        import torch

        seed = 42
        seed_everything(seed)

        # Generate a random number
        rand_num1 = random.random()
        np_rand_num1 = np.random.rand()
        torch_rand_num1 = torch.rand(1).item()

        # Reset the seed and generate again
        seed_everything(seed)
        rand_num2 = random.random()
        np_rand_num2 = np.random.rand()
        torch_rand_num2 = torch.rand(1).item()

        # Check if all generated numbers are equal
        self.assertEqual(rand_num1, rand_num2, "Random numbers are not equal, seeding failed.")
        self.assertEqual(np_rand_num1, np_rand_num2, "NumPy random numbers are not equal, seeding failed.")
        self.assertEqual(torch_rand_num1, torch_rand_num2, "Torch random numbers are not equal, seeding failed.")