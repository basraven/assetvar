from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()
    
VERSION = '0.0.1' 
DESCRIPTION = 'Pancake Swap Analysis'
LONG_DESCRIPTION = 'Pancake Swap data analysis and filtering'

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="panalyze", 
        version=VERSION,
        author="sjraven",
        author_email="",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=required,
        keywords=['pancake swap', 'analysis'],
        classifiers= [
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python :: 3",
            "Operating System :: Linux :: Ubuntu",
        ]
)