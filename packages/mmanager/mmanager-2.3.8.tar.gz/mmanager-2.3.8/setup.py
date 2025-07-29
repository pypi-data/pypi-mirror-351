from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mmanager',
    version='2.3.8',
    description='Modelmanager API With Insight Generation and Pycausal, MLFlow Integration, Causal Insights',
    author='falcon',
    license='MIT',
    packages=['mmanager'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests',
        'colorama',
        'ipython',
    ],
    package_data={
        'mmanager': [
            'test/*.py',
            'example_scripts/*.py',
            'assets/model_assets/*.csv',
            'assets/model_assets/*.json',
            'assets/model_assets/*.h5',
            'assets/model_assets/*.jpg',
            'assets/project_assets/*.jpg',
        ],
    },
    include_package_data=True,  
    python_requires='>=3.6',    
)
