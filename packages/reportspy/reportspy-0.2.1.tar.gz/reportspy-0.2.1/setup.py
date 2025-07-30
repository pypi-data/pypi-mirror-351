from setuptools import setup, find_packages

setup(
    name='reportspy',
    version='0.2.1',
    description='Generate HTML and PDF EDA reports from Excel files',
    author='Your Name',
    packages=find_packages(),
    package_data={
        'reportspy': ['pyarmor_runtime_000000/*'],  # include all runtime files
    },
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
