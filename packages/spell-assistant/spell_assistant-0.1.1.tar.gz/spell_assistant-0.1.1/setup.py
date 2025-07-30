# SpeLL_Project/setup.py
from setuptools import setup, find_packages
import os
import re

# Function to get version from spell/__init__.py
def get_version(package_name):
    with open(os.path.join(package_name, '__init__.py'), 'r', encoding='utf-8') as f:
        init_content = f.read()
    match = re.search(r"""^__version__\s*=\s*['"]([^'"]*)['"]""", init_content, re.MULTILINE)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find __version__ string.")

# Function to read core requirements
def read_requirements(filename="requirements.txt"):
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found. No core dependencies will be listed from it.")
        return []
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Function to read long description from README
def get_long_description(filename="README.md"):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

PACKAGE_NAME = "spell" # The name of your package directory (import spell)
DISTRIBUTION_NAME = "spell-assistant" # The name for pip install (pip install spell-assistant)
VERSION = get_version(PACKAGE_NAME)

# Core dependencies are read from requirements.txt
INSTALL_REQUIRES = read_requirements("requirements.txt")

setup(
    name=DISTRIBUTION_NAME,
    version=VERSION,
    author="Jiashun Fu",
    author_email="fujiashun1998@163.com",
    description="SpeLL: An expert AI assistant for spectral data modeling and Python code generation. See LICENSE.txt for usage terms.",
    long_description=get_long_description("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/Drjiashun/spell-assistant",
    license="Custom - See LICENSE.txt", # Or "MIT", "Apache-2.0" etc. if you choose a standard one
    license_files=('LICENSE.txt',),
    packages=find_packages(include=[PACKAGE_NAME, f'{PACKAGE_NAME}.*']),

    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.8', # Specify compatible Python versions
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent', # If true; llama-cpp might have OS specifics for compilation
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Chemistry',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='spell, ai, spectral analysis, chemistry, code generation, rag, llm, llama, assistant',
)
print(f"\n--- setup.py for {DISTRIBUTION_NAME} v{VERSION} ---")
print(f"Packages found: {find_packages(include=[PACKAGE_NAME, f'{PACKAGE_NAME}.*'])}")
print(f"Core install_requires: {INSTALL_REQUIRES}")
print("Remember to guide users for manual installation of heavy dependencies in README.md.")