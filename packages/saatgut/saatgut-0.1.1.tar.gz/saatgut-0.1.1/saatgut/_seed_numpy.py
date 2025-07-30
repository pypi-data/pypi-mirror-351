import os

from saatgut._secure_import import secure_import


@secure_import('numpy')
def seed_numpy(seed: int):
    """
    Set the random seed for NumPy's RNG.

    Args:
        seed (int): The seed value to set.
    """
    import numpy as np
    np.random.seed(seed)


@secure_import('numpy')
def domesticate_numpy(seed: int):
    """
    Set NumPy's seed and enforce as much determinism as possible.

    Args:
        seed (int): The seed value to set.
    """
    # Try to minimize sources of nondeterminism from underlying libraries (before importing NumPy)
    # Set environment variables to control thread usage
    os.environ['PYTHONHASHSEED'] = str(seed)  # Sometimes relevant for hashing
    os.environ['OMP_NUM_THREADS'] = '1'  # OpenMP
    os.environ['MKL_NUM_THREADS'] = '1'  # Intel MKL
    os.environ['NUMEXPR_NUM_THREADS'] = '1'  # NumExpr
    os.environ['OPENBLAS_NUM_THREADS'] = '1'  # OpenBLAS

    import numpy as np
    seed_numpy(seed)

    if hasattr(np.random, 'set_state'):
        # If available, set the state of the random number generator
        np.random.set_state(np.random.get_state())
