from setuptools import setup, find_packages


long_description = """
This Python package offers a collection of utilities for managing and interacting 
with Unix-based operating systems using only standard libraries. It includes 
functions for retrieving system information, inspecting user environments, 
performing file and directory operations, and managing process-level tasks. 
The library also provides helpers for working with pip installation, parsing system 
configuration files, and handling common administrative actions programmatically. 
Designed for automation, scripting, and lightweight system tooling, it serves
 as a versatile toolkit for system administrators, developers, and power users 
 working in Unix-like environments.
"""

setup(
    name='nix-utils',
    version='1.3.8',
    packages=find_packages(),
    description='nix-utils',
    long_description_content_type='text/plain',
    long_description=long_description,
    url='https://github.com/neodyme-labs/nix-utilities',
    download_url='https://github.com/neodyme-labs/nix-utilities',
    project_urls={
        'Documentation': 'https://github.com/neodyme-labs/nix-utilities'},
    author='Daniel K',
    author_email='dkilimnik@neodymetechnologies.com',
    platforms=['Linux'],
    license='GNU',
    install_requires=[
        'pycryptodomex',
        'pip',
        'cloud-ds-api',
        'img-splicer'
    ],

)
