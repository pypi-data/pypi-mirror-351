from setuptools import setup

setup(
    name='erioon',
    version='0.0.0',
    author='Zyber Pireci',
    author_email='zyber.pireci@erioon.com',
    description='Erioon SDF for Python',
    long_description='This SDK allows you to interact with all the Erioon resources.',
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=['requests', 'pyodbc'],
    python_requires='>=3.6',
    license='MIT', 
)
