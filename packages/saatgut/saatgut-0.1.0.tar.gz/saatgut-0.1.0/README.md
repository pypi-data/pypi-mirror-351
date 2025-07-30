![saatgut - Seed everything, everywhere, all at once.](./saatgut.png)


Set a seed across all your libraries and frameworks with a single function call.

```python
from saatgut import seed_everything

# Seed everything, everywhere, all at once.
seed_everything(42)
```

But sometimes, the seed is not enough. To improve reproducibility even more, you can domesticate everything. 
This will seed your libraries and modify OS variables to ensure that the environment is as consistent as possible.

```python
from saatgut import domesticate_everything

domesticate_everything(42)
```

To exterminate even the last but of randomness, you can use the hard mode. 
This will disable parallel execution in libraries that support it, modify more OS variables, and overwrite some
functions from the `random` module. This will ensure that your code runs in a fully deterministic manner, 
but it will significantly slow down your code (depending on the libraries you use) and make 
cryptographic functions deterministic as well. Never use this in a production environment!
```python
from saatgut import domesticate_everything

domesticate_everything(42, hard_mode=True)
```

## Installation
```bash
pip install saatgut
```


## Supported libraries
- `random`
- `numpy`
- `torch`
- `tensorflow`
- `jax`

By extension, this leads to reproducibility in libraries that use these libraries, such as:
- `pandas`
- `scikit-learn`
- `scipy`
- huggingface libraries, like `transformers`
- opencv (`cv2`)
- `statsmodels`
- `gensim`

... and many more!


## Seeding specific libraries
You can also seed specific libraries if you don't want to seed everything. This works for all the libraries listed above.

```python
from saatgut import seed_random, seed_numpy, seed_torch, seed_tensorflow, seed_jax

# Seed only numpy and torch.
seed_numpy(42)
seed_torch(43)
```

Domestication is available for specific libraries as well:

```python
from saatgut import domesticate_random, domesticate_numpy, domesticate_torch, domesticate_tensorflow, domesticate_jax

domesticate_torch(seed=42, force_matmul_precision=True)
domesticate_tensorflow(seed=43, disable_parallelism=True)
domesticate_random(seed=44, derandomize_cryptography=True)
```

The additional parameters used above are specific to the library and can be found in the documentation of each function.
Use them only if normal domestication is not enough for your use case.
Using `hard_mode=True` in `domesticate_everything` is equivalent to setting all the additional parameters to `True` in the specific domestication functions.


## Why "saatgut"?
The name "saatgut" is derived from the German word for "seed" (Saatgut).


## Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue on GitHub.
If you want to contribute code, please take a look at the open issues.


## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
