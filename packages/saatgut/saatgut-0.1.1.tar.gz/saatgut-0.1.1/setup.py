from setuptools import setup, find_packages


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='saatgut',
    version='0.1.1',
    author='Tim Wibiral',
    packages=find_packages(),
    install_requires=[],    # Nothing! The package checks and seeds what is available.
    long_description=long_description,
    long_description_content_type='text/markdown',
    description="saatgut: seed everything, everywhere, all at once.",
    url="https://www.github.com/twibiral/saatgut",
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development",
        "Topic :: Utilities"
    ]
)
