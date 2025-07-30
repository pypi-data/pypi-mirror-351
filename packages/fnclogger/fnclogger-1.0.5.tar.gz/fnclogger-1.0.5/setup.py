from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fnclogger',
    version='1.0.5',
    description='Простой и мощный логгер для Python с цветным выводом',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='plv88',
    author_email='your.email@example.com',
    url='https://github.com/plv88/fnclogger',
    packages=find_packages(),
    python_requires='>=3.7',
    install_requires=[
        'rich>=10.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'build>=0.7.0',
            'twine>=3.4.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ],
    keywords='logging logger fancy colored json simple rich',
)