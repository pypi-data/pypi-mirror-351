# setup.py
from setuptools import setup, find_packages

setup(
    name='mpesa_analysis',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'pdfplumber>=0.10.0',
        'numpy>=1.20.0',
        'google-generativeai>=0.3.0',
        'Flask>=2.0.0', # <--- Add Flask here
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-mock',
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A loan advisory system using M-Pesa statement analysis and Gemini AI.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/mpesa_analysis',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business :: Financial',
    ],
    python_requires='>=3.8',
)