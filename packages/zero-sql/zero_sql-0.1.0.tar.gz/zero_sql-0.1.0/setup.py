from setuptools import setup, find_packages

setup(
    name='zero-sql',
    version='0.1.0',
    packages=find_packages(),
    description='A SQL-less lightweight Python DB layer',
    author='ABINAYA SAKTHIVEL',
    author_email='abisakthivel8@gmail.com',
    license='MIT',
    keywords='database sql abstraction sqlite',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
