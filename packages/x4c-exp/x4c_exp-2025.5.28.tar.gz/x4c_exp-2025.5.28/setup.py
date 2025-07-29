from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

setup(
    name='x4c-exp',  # required
    version='2025.5.28',
    description='x4c: Xarray for CESM',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Feng Zhu',
    author_email='fengzhu@ucar.edu',
    url='https://github.com/fzhu2e/x4c',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    scripts=['bin/x4c'],
    keywords='Xarray, CESM, Climate Data Analysis and Visualization',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=[
        'netCDF4',
        'xarray',
        'dask',
        'nc-time-axis',
        'colorama',
        'tqdm',
        'xhistogram',
    ],
)
