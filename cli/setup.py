from setuptools import setup, find_packages

setup(
    name="vodka-cli",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "vodka-lib>=0.1.0",  # Depend on the library package
    ],
    entry_points={
        'console_scripts': [
            'vodka=vodka_cli.cli:main',
        ],
    },
    python_requires=">=3.6",
    description="A WINE Version Manager CLI App",
    author="MVDW-Java",
)
