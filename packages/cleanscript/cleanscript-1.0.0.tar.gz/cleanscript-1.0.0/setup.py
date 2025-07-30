from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cleanscript",
    version="1.0.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "astor>=0.8.1,<1.0.0",
        "black>=24.0.0,<25.0.0",
        "requests>=2.25.0,<3.0.0",
        "colorama>=0.4.6,<1.0.0",
        "tenacity>=8.0.0",
        "transformers>=4.30.0",  # For local models
        "torch>=2.0.0",  # PyTorch backend
        "sentencepiece"  # Required for some models
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "mock>=4.0.0,<5.0.0",
            "twine>=4.0.0,<5.0.0",
            "wheel>=0.40.0,<1.0.0"
        ],
        "test": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "mock>=4.0.0,<5.0.0"
        ],
        "light": [  # For users who don't want local models
            "astor>=0.8.1",
            "black>=24.0.0",
            "colorama>=0.4.6"
        ]
    },
    entry_points={
        "console_scripts": [
            "cleanscript=cleanscript.cli:main"
        ],
    },
    # ... rest of your metadata ...
)