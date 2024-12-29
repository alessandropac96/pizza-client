from setuptools import setup, find_packages

setup(
    name='pizza-client',
    version='0.1.0',
    author='Alessandro Pascucci',
    author_email='alessandro1.96@hotmail.it',
    description='Test llm client implementation in python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AlessandroPac96/pizza-client',
    packages=find_packages(where='src', include=['pizza_client', 'pizza_client.*']),
    package_dir={'': 'src'},
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)