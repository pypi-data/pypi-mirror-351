from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cleanscript",
    version="1.0.1",  # Update this for new releases
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        "astor>=0.8.1,<1.0.0",  # AST manipulation
        "black>=24.0.0,<25.0.0",  # Code formatting
        "requests>=2.25.0,<3.0.0",  # API calls
        "colorama>=0.4.6,<1.0.0",  # Terminal colors
        "tenacity>=8.0.0",  # Retry logic
        "transformers>=4.30.0",  # Local AI models
        "torch>=2.0.0",  # ML backend
        "sentencepiece"  # Tokenization for some models
    ],
    extras_require={
        "dev": [  # Development tools
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "mock>=4.0.0,<5.0.0",
            "twine>=4.0.0,<5.0.0",
            "wheel>=0.40.0,<1.0.0"
        ],
        "test": [  # Testing requirements
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "mock>=4.0.0,<5.0.0"
        ],
        "light": [  # Minimal install without AI
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
    author="Arun Vijo Tharakan",
    author_email="arunvijo2004@gmail.com",
    description=(
        "CleanScript: An intelligent Python code optimizer and documentation tool "
        "that enhances code quality through automated refactoring, PEP-8 compliance "
        "checks, and AI-powered comment generation. Supports both online API and "
        "local AI models for all your code cleaning needs."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators"
    ],
    python_requires='>=3.7',
    url="https://github.com/arunvijo/cleanscript",
    project_urls={
        "Bug Tracker": "https://github.com/arunvijo/cleanscript/issues",
        "Documentation": "https://github.com/arunvijo/cleanscript/wiki",
        "Source Code": "https://github.com/arunvijo/cleanscript",
        "Changelog": "https://github.com/arunvijo/cleanscript/releases",
    },
    keywords=[
        "python", "code", "optimizer", 
        "cleaner", "documentation", "gpt",
        "refactor", "pep8", "formatter",
        "ai", "autocomplete"
    ],
)