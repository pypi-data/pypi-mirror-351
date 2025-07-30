from saatgut._seed_jax import seed_jax, domesticate_jax
from saatgut._seed_numpy import seed_numpy, domesticate_numpy
from saatgut._seed_random import seed_random, domesticate_random
from saatgut._seed_tensorflow import seed_tensorflow, domesticate_tensorflow
from saatgut._seed_torch import seed_torch, domesticate_torch

from saatgut._secure_import import _exception_catcher, _silent_secure_import


__ALL_SEEDING_FUNCTIONS__ = {
    "torch": seed_torch,
    "tensorflow": seed_tensorflow,
    "numpy": seed_numpy,
    "random": seed_random,
    "jax": seed_jax,
}

__ALL_CULTIVATION_FUNCTIONS__ = {
    "torch": domesticate_torch,
    "tensorflow": domesticate_tensorflow,
    "numpy": domesticate_numpy,
    "random": domesticate_random,
    "jax": domesticate_jax,
}


def seed_everything(seed: int = 42):
    """
    Set the random seed for all supported libraries to ensure reproducibility.
    This function does not ensure full determinism, but is sufficient for most use cases.

    Args:
        seed (int): The seed value to set for random number generation.
    """
    for package_name, planter in __ALL_SEEDING_FUNCTIONS__.items():
        try:
            _exception_catcher(package_name, _silent_secure_import(package_name)(planter))(seed)
        except Exception as e:
            print(f"Error while seeding with {planter.__name__}: {e}")


def domesticate_everything(seed: int = 42, hard_mode: bool = False):
    """
    Set up all supported libraries for reproducibility by setting random seeds and configuring options.
    Works like `saatgut.seed_everything`, but tries to ensure reproducibility as much as possible using additional configurations.
    This can make your code a lot more deterministic, but also slow it down significantly.

    You can set `hard_mode=True` to enable additional configurations for full determinism, such as setting intra-op
    and inter-op parallelism threads to 1 in TensorFlow and enabling deterministic algorithms in PyTorch.
    This further reduces non-determinism, but may significantly slow down runtime performance.

    Args:
        seed (int): The seed value to set for random number generation.
        hard_mode (bool): If True, sets additional configurations for full determinism.
    """
    # First cultivate all libraries normally:
    for package_name, planter in __ALL_CULTIVATION_FUNCTIONS__.items():
        try:
            _exception_catcher(package_name, _silent_secure_import(package_name)(planter))(seed)
        except Exception as e:
            print(f"Error while cultivating {planter}: {e}")

    # If hard_mode is enabled, set additional configurations for full determinism by hand:
    if hard_mode:
        domesticate_torch(seed=seed, force_matmul_precision=True)
        domesticate_tensorflow(seed=seed, disable_parallelism=True)
        domesticate_random(seed=seed, derandomize_cryptography=True)