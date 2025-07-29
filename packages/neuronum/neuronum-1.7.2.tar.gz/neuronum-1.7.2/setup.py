from setuptools import setup, find_packages

setup(
    name='neuronum',
    version='1.7.2',
    author='Neuronum Cybernetics',
    author_email='welcome@neuronum.net',
    description='Official client library to interact with the Neuronum Network',
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://neuronum.net",
    project_urls={
        "GitHub": "https://github.com/neuronumcybernetics/neuronum",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests', 
        'websocket-client',
        'click',
        'questionary',
        'python-dotenv',
    ],
    entry_points={
        "console_scripts": [
            "neuronum=cli.main:cli"
        ]
    },
    python_requires='>=3.8', 
)
