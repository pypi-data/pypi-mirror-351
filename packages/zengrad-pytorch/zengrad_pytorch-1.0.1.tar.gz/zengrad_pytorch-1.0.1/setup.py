
from setuptools import setup, find_packages

setup(
    name='zengrad-pytorch',  
    version='1.0.1',
    description='ZenGrad: A gradient descent method focused on stability, smooth updates, and efficient, adaptive learning.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author= 'Rishi Chaitanya',
    author_email='rishichaitanya888@gmail.com',
    packages=find_packages(),
    url='https://github.com/Rishichaitanya-Nalluri/zengrad-pytorch',
    license="Apache-2.0",
    install_requires=[ 
        "torch>=1.6.0"
    ],
    classifiers=[
    'Programming Language :: Python :: 3',
    "License :: OSI Approved :: Apache Software License",
    'Operating System :: OS Independent',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research', 
    'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=3.6',
)
