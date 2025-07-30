from _secure_import import secure_import


@secure_import("jax")
def seed_jax(seed: int):
    import jax
    return jax.random.PRNGKey(seed)


@secure_import("jax")
def domesticate_jax(seed: int):
    import jax
    return seed_jax(seed)
