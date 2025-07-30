from setuptools import setup, find_packages

setup(
    name='u3m',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'tqdm',
        'numpy',
        'opencv-python',
        'scikit-image',
        'scipy',
        'laspy',
        'pyproj',
        'lazrs[laszip]',
        'leafmap',
        'xarray',
        'rasterio',
        'localtileserver',
        'ipykernel',
        'openrs-python',
        'd2spy'
    ],
    python_requires='>=3.10',  # Specify your Python version requirement here
)