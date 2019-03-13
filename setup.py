from setuptools import setup
from pathlib import Path

here = Path(__file__).parent

with (here/'README.md').open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ja2sci',
    version='0.1.2',
    description='Translate Japanese name into scientific name',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AzukiOtter/ja2sci',
    author='AzukiOtter',
    author_email='ogran.std@gmail.com',
    license='MIT',
    keywords='biology species',
    python_requires='>=3.6, <4',
    packages=['ja2sci'],
    package_data={'ja2sci': ['dictionary/ja2sci.pkl']},
    install_requires=['aiohttp>=3.3.0'],
    entry_points={
        'console_scripts':[
            'ja2sci = ja2sci.main:commandline',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
