import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='bloomtracker',
    version='0.4.0',
    author='Sascha Triller',
    author_email='sascha.triller@posteo.de',
    description='API client for the "Deutscher Wetterdienst" to get the current pollen load in Germany',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/striller/BloomTracker',
    packages=['bloomtracker'],
    install_requires=[
        'requests>=2.31.0', 
        'pytz>=2023.3',
        'aiohttp>=3.8.0',
        'rich>=13.0.0',
        'matplotlib>=3.5.0',
        'numpy>=1.20.0',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
    ],
)
