from setuptools import setup, find_packages
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("querysh/__init__.py", "r", encoding="utf-8") as f:
    version = re.search(r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read()).group(1)

setup(
    name="querysh",
    version=version,
    description="A local, offline shell interface powered by MLX-optimized Llama model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mlx-lm>=0.0.6",
        "rich>=13.7.0",
        "torch==2.0.1",
        "transformers==4.36.0",
        "numpy>=1.21.6,<1.28.0",
        "protobuf>=3.19.5,<5.0.0",
        "urllib3<2.0.0",
        "requests==2.11.1",
        "requests-toolbelt==0.7.0",
        "flask<3.0,>=1.0",
    ],
    entry_points={
        "console_scripts": [
            "querysh=querysh.cli:main",
        ],
    },
) 