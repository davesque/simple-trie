from setuptools import (
    setup,
    find_packages,
)


extras_require={
    'dev': [
        'pytest',
        'hypothesis',
        'ipython',
    ],
}


setup(
    name='simple-trie',
    version='0.1.0-alpha.0',
    description="""simple-trie: A simple Ethereum trie implementation.""",
    long_description_markdown_filename='README.md',
    author='David Sanders',
    author_email='davesque@gmail.com',
    url='https://github.com/ethereum/simple-trie',
    include_package_data=True,
    install_requires=[
        'eth-utils',
        'eth-hash[pycryptodome]',
    ],
    extras_require=extras_require,
    py_modules=['simpletrie'],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=find_packages(exclude=["tests", "tests.*"]),
)
