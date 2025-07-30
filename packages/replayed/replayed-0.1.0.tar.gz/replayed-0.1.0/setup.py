import os
from setuptools import setup, find_packages

# Package metadata
NAME = 'replayed'
VERSION = '0.1.0' # Should match __version__ in replayed/__init__.py
DESCRIPTION = 'A Python library for parsing and analyzing Beat Saber BSOR replay files.'
AUTHOR = 'CodeSoftGit' 
AUTHOR_EMAIL = 'hello@mail.codesoft.is-a.dev' # Placeholder email, please update
URL = 'https://github.com/CodeSoftGit/replayed' # Placeholder URL, please update
PYTHON_REQUIRES = '>=3.8' # Pydantic 2.x generally requires Python 3.8+

# Dependencies
REQUIRED_PACKAGES = [
    'pydantic>=2.0.0,<3.0.0', # Specify a version range for Pydantic 2.x
]

# Function to read the long description from README.md
def read_long_description():
    """Reads the README.md file for use as the long description."""
    try:
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: README.md not found. Long description will be empty.")
        return None

LONG_DESCRIPTION = read_long_description()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown', # Important for rendering README on PyPI
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    python_requires=PYTHON_REQUIRES,
    # find_packages() automatically discovers all packages and subpackages.
    # The 'where' argument can be used if your packages are in a subdirectory (e.g., 'src').
    # Assuming 'replayed' directory is at the root level alongside setup.py.
    packages=find_packages(where='.', exclude=['tests*', '*.tests', '*.tests.*', 'tests.*']),
    # If your 'replayed' package was inside an 'src' directory:
    # package_dir={'': 'src'},
    # packages=find_packages(where='src'),
    install_requires=REQUIRED_PACKAGES,
    # extras_require=EXTRA_PACKAGES, # Uncomment if you have optional dependencies
    # include_package_data=True, # If you have non-code files inside your package to include
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.org/classifiers/
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Games/Entertainment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
        'Typing :: Typed',
    ],
    keywords='beatsaber bsor replay parser pydantic games', # Keywords for PyPI search
    project_urls={ # Optional
        'Bug Reports': f'{URL}/issues',
        'Source': URL
    },
)
