from setuptools import setup, find_packages

setup(
    name="putils-z",
    version="0.1.1",
    description="Utility CLI tool",
    author="ubuntu",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'lz=zz_tool.cli:main',
        ],
    },
    python_requires=">=3.6",
)
