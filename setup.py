import codecs
from setuptools import setup
from setuptools import find_namespace_packages

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'pyhamcrest',
    'zope.testrunner',
]

def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()

setup(
    name='nti.property',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI Property",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    url="https://github.com/OpenNTI/nti.property",
    license='Apache',
    keywords='Property',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    zip_safe=True,
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'zope.annotation',
        'zope.cachedescriptors >= 4.2',
        'zope.component',
        'zope.contenttype',
        'zope.schema >= 4.7.0',
        'ZConfig',
    ],
    extras_require={
        'zodb': [
            'zope.file >= 1.0',
        ],
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'furo',
            'zope.file',
        ],
    },
    entry_points=entry_points,
)
