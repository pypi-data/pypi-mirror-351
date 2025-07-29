from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
setup(
    name='pywebcrwl',
    version='0.1.2',
    description='Web crawling tool',
    author_email='idriss1433@gmail.com',
    packages=find_packages(),
    project_urls={
    'Homepage and Documentation': 'https://github.com/NoneToRoot/pywebcrwl',
},

    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
    'requests',
    'beautifulsoup4',
    'phonenumbers',
    'geotext'
],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)