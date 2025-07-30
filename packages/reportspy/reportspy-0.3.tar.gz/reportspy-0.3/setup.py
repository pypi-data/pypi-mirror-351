from setuptools import setup, find_packages, Extension

ext_modules = [
    Extension("reportspy.core", ["reportspy/core.c"]),  # Use .c file here
]

setup(
    name='reportspy',
    version='0.3',
    description='Generate HTML and PDF EDA reports from Excel files',
    author='Your Name',
    packages=find_packages(),
    ext_modules=ext_modules,
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
        # Remove 'cython' here because users don’t need it to install
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
)
