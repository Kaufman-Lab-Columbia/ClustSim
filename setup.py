from setuptools import setup

def read_long_description():
    with open('README.md', 'r') as open_file_description:
        return open_file_description.read()

def read_requirements():
    with open('requirements.txt', 'r') as open_file_requirements:
        return open_file_requirements.read()

setup(
    name='ClustSim',
    version='1.0.0',
    description='Cluster simulations',
    long_description_content_tyype='text/markdown',
    long_description=read_long_description(),
    author='Joseph L. Hammer',
    author_email='jhammer3018@gmail.com',
    url='',
    packages=['ClustSim'],
    license ="MIT",
    keywords = "cluster clusters clustering simulation simulate",
    install_requires=read_requirements(),
    classifiers=['License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3',
                 'Topic :: Scientific/Engineering'
                 ]

)