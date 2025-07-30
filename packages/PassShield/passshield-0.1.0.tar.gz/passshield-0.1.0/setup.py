from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="PassShield",
    version="0.1.0",
    author="Raaj Kennedy",
    author_email="kennedyraaj@gmail.com",
    description="Secure password handling for database connections",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/passhash",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'cryptography>=3.4',
        'mysql-connector-python>=8.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
        ],
    },
    keywords='password encryption security mysql database',
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/passhash/issues',
        'Source': 'https://github.com/yourusername/passhash',
    },
)