import codecs
import re
from os import path

from setuptools import find_packages, setup

# parts below shamelessly stolen from pypa/pip
here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        version_file,
        re.M,
    )
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


long_description = read('README.rst')

base_reqs = [
    'Flask',
    'Flask-Login',
    'Flask-WTF',
    'Flask-SQLAlchemy',
    'Flask-Babel',
    'Flask-Migrate',
    'Bootstrap-Flask',
    'SQLAlchemy-Filters',
    'validators',
    'Werkzeug',
    'Click',
    'keyring',
    'keyrings.cryptfile',
    'texttable',
    'markdown',
    'python-dotenv',
    'text-unidecode',
]

test_reqs = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pytest-factoryboy',
    'pytest-flask',
]

dev_reqs = [
    'ipython',
    'ipdb',
    'pip',
    'setuptools',
    'wheel',
    'flake8',
    'flake8-builtins',
    'flake8-bugbear',
    'flake8-mutable',
    'flake8-comprehensions',
    'pep8-naming',
    'dlint',
    'doc8',
    'pyroma',
    'rope',
    'isort',
    'towncrier',
    'Sphinx',
    'sphinx-autodoc-typehints',
    'flask-shell-ipython',
    'termcolor',
    'watchdog',
] + test_reqs

setup(
    name='biuletyn-bip',
    version=find_version('src', 'bip', '_version.py'),
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    description='Polish BIP (Biuletyn Informacji Publicznej) as Flask application',
    keywords='bip public information bulletin',
    long_description=long_description,
    license='GPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    url='http://github.com/zgoda/bip',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: Polish',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System',
    ],
    install_requires=base_reqs,
    extras_require={
        'prod': [
            'uwsgi',
        ],
        'dev': dev_reqs,
        'test': test_reqs,
    },
    entry_points={
        'console_scripts': [
            'bip=bip.cli:main',
        ]
    },
    python_requires='~=3.7',
)
