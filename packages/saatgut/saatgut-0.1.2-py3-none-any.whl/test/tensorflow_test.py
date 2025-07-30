import unittest


class TestTensorflow(unittest.TestCase):
    def test_seed_tensorflow(self):
        """
        Test the seed_tensorflow function to ensure it runs without errors.
        """
        from saatgut._seed_tensorflow import seed_tensorflow
        try:
            seed_tensorflow(42)
        except Exception as e:
            self.fail(f"seed_tensorflow raised an exception: {e}")

    def test_seed_tensorflow_reproducibility(self):
        """
        Test that the seed_tensorflow function sets the same seed for multiple calls.
        """
        from saatgut._seed_tensorflow import seed_tensorflow
        import tensorflow as tf

        seed = 42
        seed_tensorflow(seed)

        # Generate a random tensor
        tensor1 = tf.random.uniform((3, 3))

        # Reset the seed and generate again
        seed_tensorflow(seed)
        tensor2 = tf.random.uniform((3, 3))

        # Check if both tensors are equal
        self.assertTrue(tf.reduce_all(tf.equal(tensor1, tensor2)), "Tensors are not equal, seeding failed.")

    def test_seed_tensorflow_reproducibility_operations(self):
        """
        Test that the seed_tensorflow function ensures reproducibility across operations.
        """
        from saatgut._seed_tensorflow import seed_tensorflow
        import tensorflow as tf

        seed = 42
        seed_tensorflow(seed)

        # Perform some operations
        tensor1 = tf.random.uniform((3, 4))
        tensor2 = tf.random.uniform((4, 5))
        tensor3 = tf.matmul(tensor1, tensor2)

        # Reset the seed and perform the same operations
        seed_tensorflow(seed)
        tensor4 = tf.random.uniform((3, 4))
        tensor5 = tf.random.uniform((4, 5))
        tensor6 = tf.matmul(tensor4, tensor5)

        # Check if both results are equal
        self.assertTrue(tf.reduce_all(tf.equal(tensor3, tensor6)), "Results of operations are not equal, seeding failed.")

    def test_domesticate_tensorflow(self):
        """
        Test the domesticate_tensorflow function to ensure it runs without errors.
        """
        from saatgut._seed_tensorflow import domesticate_tensorflow
        try:
            domesticate_tensorflow(42)
        except Exception as e:
            self.fail(f"domesticate_tensorflow raised an exception: {e}")

    def test_domesticate_tensorflow_reproducibility(self):
        """
        Test that the domesticate_tensorflow function sets the same seed for multiple calls.
        """
        from saatgut._seed_tensorflow import domesticate_tensorflow
        import tensorflow as tf

        seed = 42
        domesticate_tensorflow(seed)

        # Generate a random tensor
        tensor1 = tf.random.uniform((3, 3))

        # Reset the seed and generate again
        domesticate_tensorflow(seed)
        tensor2 = tf.random.uniform((3, 3))

        # Check if both tensors are equal
        self.assertTrue(tf.reduce_all(tf.equal(tensor1, tensor2)), "Tensors are not equal, domestication failed.")

    def test_domesticate_tensorflow_reproducibility_operations(self):
        """
        Test that the seed_tensorflow function ensures reproducibility across operations.
        """
        from saatgut._seed_tensorflow import seed_tensorflow
        import tensorflow as tf

        seed = 42
        seed_tensorflow(seed)

        # Perform some operations
        tensor1 = tf.random.uniform((3, 4))
        tensor2 = tf.random.uniform((4, 5))
        tensor3 = tf.matmul(tensor1, tensor2)

        # Reset the seed and perform the same operations
        seed_tensorflow(seed)
        tensor4 = tf.random.uniform((3, 4))
        tensor5 = tf.random.uniform((4, 5))
        tensor6 = tf.matmul(tensor4, tensor5)

        # Check if both results are equal
        self.assertTrue(tf.reduce_all(tf.equal(tensor3, tensor6)),
                        "Results of operations are not equal, seeding failed.")
