import ast
import codecs
import re
from os import path

from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))


def read(*parts):
    with codecs.open(path.join(here, *parts), 'r') as fp:
        return fp.read()


_version_re = re.compile(r"__version__\s+=\s+(.*)")


def find_version(*where):
    return str(ast.literal_eval(_version_re.search(read(*where)).group(1)))


base_reqs = [
    'Flask',
    'Jinja2',
    'MarkupSafe',
    'itsdangerous',
    'PeeWee',
    'Flask-Login',
    'WTForms!=2.3.2',
    'Flask-WTF',
    'Flask-Babel',
    'Bootstrap-Flask',
    'sentry-sdk[flask]',
    'validators',
    'Werkzeug',
    'markdown',
    'python-dotenv',
    'text-unidecode',
    'Click',
    'keyring',
    'keyrings.cryptfile',
    'texttable',
    'python-magic',
    'passlib[argon2]',
    'PyICU',
]

test_reqs = [
    'pytest',
    'pytest-mock',
    'pytest-cov',
    'pytest-factoryboy',
    'pytest-flask',
]

docs_reqs = [
    'Sphinx',
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
    'flake8-comprehensions',
    'flake8-pytest-style',
    'pep8-naming',
    'dlint',
    'rstcheck',
    'rope',
    'flask-shell-ipython',
    'watchdog',
] + test_reqs + docs_reqs

setup(
    name='biuletyn-bip',
    version=find_version('src', 'bip', '_version.py'),
    author='Jarek Zgoda',
    author_email='jarek.zgoda@gmail.com',
    description='Polish BIP (Biuletyn Informacji Publicznej) as Flask application',
    keywords='bip public information bulletin',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    license='GPLv3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    url='https://github.com/zgoda/bip',
    project_urls={
        'Documentation': 'https://bip.readthedocs.io/',
        'Source': 'https://github.com/zgoda/bip',
        'Issues': 'https://github.com/zgoda/bip/issues',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'dev': dev_reqs,
        'test': test_reqs,
        'docs': docs_reqs,
    },
    entry_points={
        'console_scripts': [
            'bip=bip.cli:main',
        ]
    },
    python_requires='~=3.7',
)
