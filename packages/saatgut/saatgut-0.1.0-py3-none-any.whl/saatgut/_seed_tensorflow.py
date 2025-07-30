""" This module provides functions to set random seeds for reproducibility in TensorFlow (Keras) and related libraries. """
from _secure_import import secure_import


@secure_import('tensorflow')
def seed_tensorflow(seed: int):
    """
    Set basic random seeds for reproducibility with TensorFlow (Keras), NumPy, and Python's random module.

    Args:
        seed (int): The seed value to set.
    """
    import tensorflow as tf
    tf.random.set_seed(seed)


@secure_import('tensorflow')
def domesticate_tensorflow(seed: int = 42, disable_parallelism: bool = False):
    """
    Set up TensorFlow (Keras) for reproducibility by setting random seeds and configuring options. Works
    like `saatgut.seed_tensorflow`, but tries to ensure reproducibility as much as possible using additional
    configurations.

    Args:
        seed (int): The seed value to set.
        disable_parallelism (bool): If True, sets intra-op and inter-op parallelism threads to 1 for full determinism.
    """
    # For recent TensorFlow versions (>=2.1), set environmental variables and options
    import os
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'  # TensorFlow >=2.1
    os.environ['TF_CUDNN_DETERMINISTIC'] = '1'  # TensorFlow >=2.1

    import tensorflow as tf
    seed_keras(seed)

    if disable_parallelism:
        # Set intra-op and inter-op parallelism threads to 1 for full determinism
        # Note: This may significantly slow down training
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)

    # Note: Some operations may still not be fully deterministic.
    # See: https://www.tensorflow.org/api_docs/python/tf/config/experimental/enable_op_determinism

    # For TensorFlow >=2.8:
    try:
        tf.config.experimental.enable_op_determinism()
    except AttributeError:
        pass  # Not available in older TF versions


if __name__ == '__main__':
    seed_keras(1234)
