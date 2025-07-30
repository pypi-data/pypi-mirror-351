from setuptools import setup, find_packages

setup(
    name="cli-test-framework",
    version="0.2.0",
    author="Xiaotong Wang",
    author_email="xiaotongwang98@gmail.com",
    description="A small command line testing framework in Python with file comparison capabilities.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "dukpy==0.5.0",
        "h5py>=3.8.0",
        "numpy>=2.0.1",
        "setuptools>=75.8.0",
        "wheel>=0.45.1"
    ],
    entry_points={
        'console_scripts': [
            'cli-test=cli_test_framework.cli:main',
            'compare-files=cli_test_framework.commands.compare:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)