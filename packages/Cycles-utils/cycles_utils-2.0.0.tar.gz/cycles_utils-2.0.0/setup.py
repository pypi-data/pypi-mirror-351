from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='Cycles-utils',
    version='2.0.0',
    author='Yuning Shi',
    author_email="shiyuning@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    description='Python scripts to build Cycles input files and post-process Cycles output files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PSUmodeling/Cycles-utils',
    license='MIT',
    python_requires='>=3.10',
    install_requires=['pandas>=1.2.4', 'geopandas>=0.9.0', 'numpy>=1.19.5'],
    extras_require = {
        'soilgrids':  ['rioxarray>=0.5.0', 'owslib>=0.24.1', 'rasterio>=1.2.3', 'shapely>=1.7.1'],
        'gssurgo': ['shapely>=1.7.1'],
        'plot': ['cartopy>=0.18.0', 'matplotlib>=3.4.2'],
        'soilgrids': ['rioxarray>=0.5.0', 'owslib>=0.24.1', 'rasterio>=1.2.3', 'shapely>=1.7.1'],
        'weather': ['netCDF4>=1.5.7', 'tqdm>=4.60.0'],
    }
)
