import unittest

from saatgut._seed_torch import seed_torch


class TestTorch(unittest.TestCase):
    def test_seed_torch(self):
        """
        Test the seed_torch function to ensure it runs without errors.
        """
        try:
            seed_torch(42)
        except Exception as e:
            self.fail(f"seed_torch raised an exception: {e}")

    def test_seed_torch_reproducibility(self):
        """
        Test that the seed_torch function sets the same seed for multiple calls.
        """
        import torch
        seed = 42
        seed_torch(seed)

        # Generate a random tensor
        tensor1 = torch.rand(3, 3)

        # Reset the seed and generate again
        seed_torch(seed)
        tensor2 = torch.rand(3, 3)

        # Check if both tensors are equal
        self.assertTrue(torch.equal(tensor1, tensor2), "Tensors are not equal, seeding failed.")

    def test_seed_torch_reproducibility_operations(self):
        """
        Test that the seed_torch function ensures reproducibility across operations.
        """
        import torch
        seed = 42
        seed_torch(seed)

        # Perform some operations
        tensor1 = torch.rand(3, 4)
        tensor2 = torch.rand(4, 5)
        tensor3 = torch.matmul(tensor1, tensor2)

        # Reset the seed and perform the same operations
        seed_torch(seed)
        tensor4 = torch.rand(3, 4)
        tensor5 = torch.rand(4, 5)
        tensor6 = torch.matmul(tensor4, tensor5)

        # Check if both results are equal
        self.assertTrue(torch.equal(tensor3, tensor6), "Results of operations are not equal, seeding failed.")

    def test_domesticate_torch(self):
        """
        Test the domesticate_torch function to ensure it runs without errors.
        """
        from saatgut._seed_torch import domesticate_torch
        try:
            domesticate_torch(42)
        except Exception as e:
            self.fail(f"domesticate_torch raised an exception: {e}")

    def test_domesticate_torch_reproducibility(self):
        """
        Test that the domesticate_torch function sets the same seed for multiple calls.
        """
        from saatgut._seed_torch import domesticate_torch
        import torch

        seed = 42
        domesticate_torch(seed)

        # Generate a random tensor
        tensor1 = torch.rand(3, 3)

        # Reset the seed and generate again
        domesticate_torch(seed)
        tensor2 = torch.rand(3, 3)

        # Check if both tensors are equal
        self.assertTrue(torch.equal(tensor1, tensor2), "Tensors are not equal, domestication failed.")

    def test_domesticate_torch_reproducibility_operations(self):
        """
        Test that the domesticate_torch function ensures reproducibility across operations.
        """
        from saatgut._seed_torch import domesticate_torch
        import torch

        seed = 42
        domesticate_torch(seed)

        # Perform some operations
        tensor1 = torch.rand(3, 4)
        tensor2 = torch.rand(4, 5)
        tensor3 = torch.matmul(tensor1, tensor2)

        # Reset the seed and perform the same operations
        domesticate_torch(seed)
        tensor4 = torch.rand(3, 4)
        tensor5 = torch.rand(4, 5)
        tensor6 = torch.matmul(tensor4, tensor5)

        # Check if both results are equal
        self.assertTrue(torch.equal(tensor3, tensor6), "Results of operations are not equal, domestication failed.")


