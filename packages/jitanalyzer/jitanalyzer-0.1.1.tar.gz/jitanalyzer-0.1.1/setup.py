from setuptools import setup, find_packages, Extension

setup(
    name='jitanalyzer',
    version='0.1.1',
    description='Generate HTML and PDF EDA reports from Excel files',
    author='JIT',
    packages=find_packages(where='dist_obf'),
    package_dir={'': 'dist_obf'},
    package_data = {
    'pyarmor_runtime_000000': ['*.pyd', '*.py'],
    },
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'plotly',
        'pdfkit',
        'openpyxl',
        'scipy',
        'matplotlib',
        'statsmodels',
        'jinja2',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
