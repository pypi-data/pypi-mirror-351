from setuptools import setup, find_packages

setup(
    name='boxplot',
    version='0.1.0',
    description='boxplots easily',
    author='nukhes',
    author_email='nukhes@protonmail.com',
    url='https://github.com/nukhes/boxplot',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    python_requires='>=3.9',
)