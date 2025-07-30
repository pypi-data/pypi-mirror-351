
import setuptools
import os


setuptools.setup(
    name='ODEpower',
    version='0.9.0',
    author='Robert Annuth',
    author_email='robert.annuth@tuhh.de',
    description='ODE-based power system modeling and simulation package',
    long_description=open('README.md').read() if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    url='https://github.com/rAnnuth/ODEpower',
    packages=setuptools.find_packages(),
    license='LICENSE.txt',
    install_requires=[
        'scipy',
        'sympy',
        'pandas',
        'numpy',
        'control',
        'tabulate',
        'networkx',
        'matlabengine==24.2.2', # Uncomment if available via pip
    ],
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)