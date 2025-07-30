import os


def seed_random(seed: int):
    """
    Set the seed for Python's built-in random module.

    Args:
        seed (int): The seed value to set.
    """
    import random
    random.seed(seed)


def domesticate_random(seed: int, derandomize_cryptography: bool = False):
    """
    Set the seed for Python's random module and enforce maximum determinism.
    (For Python's random, this mostly means also controlling hash seed.)

    Args:
        seed (int): The seed value to set.
    """
    # PYTHONHASHSEED affects hash() and related functions, relevant if hash randomization is used
    os.environ['PYTHONHASHSEED'] = str(seed)
    # Note: Setting PYTHONHASHSEED has effect only if set before the Python interpreter starts.
    # Here, we set it for consistency, but to actually affect hashing you must launch Python with:
    #   PYTHONHASHSEED=42 python myscript.py

    import random
    seed_random(seed)

    if derandomize_cryptography:
        # Cryptographic functions often relay on random entropy from the OS. We stop this here.
        # NEVER USE IN PRODUCTION, THIS IS FOR TESTING PURPOSES ONLY!
        print("[saatgut] WARNING: Derandomizing OS entropy! "
              "This makes cryptographic functions insecure and should only be used for testing purposes.")
        class FakeRandom(random.Random):
            def randbytes(self, n):
                return bytes([self.randint(0, 255) for _ in range(n)])

        fake = FakeRandom(seed)
        os.urandom = lambda n: fake.randbytes(n)
