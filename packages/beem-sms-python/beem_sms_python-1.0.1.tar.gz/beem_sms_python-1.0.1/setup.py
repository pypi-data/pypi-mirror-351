from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Handle requirements.txt if it exists
requirements = []
if os.path.exists("requirements.txt"):
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    # Fallback to hardcoded requirements
    requirements = [
        "requests>=2.28.0",
        "urllib3>=1.26.0",
    ]

setup(
    name="beem-sms-python",
    version="1.0.1",
    author="James Mashaka",
    author_email="j1997ames@gmail.com",
    description="Professional Python SDK for Beem SMS API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/islandkid-20/beem-sms-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Communications",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.12.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "types-requests>=2.28.0",
            "pre-commit>=2.20",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "beem-sms=beem_sms.cli:main",
        ],
    },
    keywords="sms, beem, tanzania, messaging, api, sdk",
    project_urls={
        "Bug Reports": "https://github.com/islandkid-20/beem-sms-python/issues",
        "Source": "https://github.com/islandkid-20/beem-sms-python",
        "Documentation": "https://beem-sms-python.readthedocs.io/",
    },
)