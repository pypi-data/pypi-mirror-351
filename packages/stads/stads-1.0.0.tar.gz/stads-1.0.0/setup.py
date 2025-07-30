from setuptools import setup, find_packages

setup(
    name='STADS',
    version='1.0.0',
    author='Akarsh Bharadwaj',
    author_email="akarsh_sudheendra.bharadwaj@dfki.de",
    description='a spatiotemporal statistics-based adaptive sampling algorithm',
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "numpy"
    ],
    entry_points={
        "console_scripts": [
            "main-main = src.main:main",
        ]
    },
    python_requires=">=3.8"
)
