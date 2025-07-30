from setuptools import setup, find_packages

setup(
    name='clockangle',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[],  # No external dependencies
    description='A Python library to calculate the angle between the two hands of a clock.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Niral Bhatt (NY Co.)',
    author_email='niralbhatt@hotmail.com',  
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)