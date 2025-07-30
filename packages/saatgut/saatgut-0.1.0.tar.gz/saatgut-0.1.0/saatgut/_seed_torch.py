"""
Set all random seeds for PyTorch to ensure reproducibility.
More info: https://pytorch.org/docs/stable/notes/randomness.html

seed_torch(seed)
    Basic seeding.

domesticate_torch(seed)
    Comprehensive setup for reproducibility in PyTorch, including seeding and other configurations.
"""


from _secure_import import secure_import


@secure_import('torch')
def seed_torch(seed: int = 42):
    """
    Set the random seed for PyTorch to ensure reproducibility.

    Args:
        seed (int): The seed value to set for random number generation.
    """
    import torch

    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)


@secure_import('torch')
def domesticate_torch(seed: int = 42, force_matmul_precision: bool = False):
    """
    Like `saatgut.seed_torch`, but tries to ensure reproducibility as much as possible.
    Note: Some operations in PyTorch may still be non-deterministic, see:
    https://pytorch.org/docs/stable/notes/randomness.html

    Args:
        seed (int): The seed value to set for random number generation.
    """
    import torch

    seed_torch(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if hasattr(torch, 'use_deterministic_algorithms'):
        torch.use_deterministic_algorithms(True, warn_only=True)

    # Optionally, force deterministic behavior for certain operations
    if force_matmul_precision:
        if hasattr(torch, 'set_float32_matmul_precision'):
            torch.set_float32_matmul_precision('high')  # PyTorch >= 1.12
        torch.backends.cuda.matmul.allow_tf32 = False  # If needed for even more control

    # Note: Some operations in PyTorch may still be non-deterministic, see:
    # https://pytorch.org/docs/stable/notes/randomness.html
