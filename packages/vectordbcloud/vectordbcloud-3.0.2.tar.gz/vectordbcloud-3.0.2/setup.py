from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vectordbcloud",
    version="3.0.2",
    packages=find_packages(),
    install_requires=[
        # Core Technical Requirements (MANDATORY)
        "falcon==3.1.1",         # High-performance HTTP framework
        "pydantic>=1.10.8,<2.0", # Data validation and settings management
        # Note: Fireducks 1.2.5 functionality implemented internally

        # Performance Requirements for <5ms + >100k concurrent users
        "aiohttp>=3.8.0",        # Async HTTP client
        "uvloop>=0.17.0",        # High-performance event loop
        "requests>=2.28.0",      # HTTP library with connection pooling
        "urllib3>=1.26.0",       # HTTP client with advanced features

        # Data processing and optimization
        "numpy>=1.21.0",         # Numerical computing
        "pandas>=1.3.0",         # Data manipulation

        # Standard requirements
        "typing-extensions>=4.0.0",
        "certifi>=2022.0.0",
        "charset-normalizer>=2.0.0",
        "idna>=3.0.0",
        "tenacity>=8.2.2",
        "cachetools>=5.3.0",
        "orjson>=3.8.12",
        "ujson>=5.7.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "black>=22.0.0"],
    },
    author="VectorDBCloud",
    author_email="support@vectordbcloud.com",
    description="VectorDBCloud Python SDK - 100% ECP-Native with Fireducks + Falcon + Pydantic - <5ms + >100k users",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VectorDBCloud/python-sdk",
    project_urls={
        "Documentation": "https://docs.vectordbcloud.com",
        "Source": "https://github.com/VectorDBCloud/python-sdk",
        "Tracker": "https://github.com/VectorDBCloud/python-sdk/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    keywords="vectordb database api sdk python ecp ephemeral-context-protocol",
)
