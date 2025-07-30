# setup.py

from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()


with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='doculinkr',
    version='0.1.0', # Start with a basic version
    author='Nicholas Roy / FormuLearn B.V.',
    author_email='nicholas.roy@formulearn.org', 
    description='A Python CLI to seamlessly link & manage Docusaurus documentation from multiple Git projects into one unified website.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FormuLearn/DocuLinkr', # Replace with your actual GitHub URL
    packages=find_packages(), # Automatically finds the 'doculinkr' package
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'doculinkr=doculinkr.cli:cli',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Documentation',
        'Topic :: Software Development :: Build Tools',
    ],
    python_requires='>=3.10', # Adjust as needed, so far 3.10 seems reasonable.
)