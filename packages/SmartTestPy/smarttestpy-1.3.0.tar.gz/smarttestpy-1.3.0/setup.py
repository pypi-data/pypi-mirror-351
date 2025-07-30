from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="SmartTestPy",
    version="1.3.0",
    author="Roberto Lima",
    author_email="robertolima.izphera@gmail.com",
    description="🧪 Framework Inteligente para Testes em Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robertolima-dev/SmartTestPy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pytest>=6.0.0",
        "requests>=2.31.0",
        "PyJWT>=2.8.0",
        "freezegun>=1.2.0",
        "pytest-cov>=2.12.0",
        "pytest-xdist>=2.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "pytest-xdist>=2.4.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
    },
)
